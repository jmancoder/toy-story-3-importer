import bpy
import math

from bpy.types import Context, Object
from mathutils import Vector
from pathlib import Path
from .skel_z_reader import SkelZReader, SkelZ
from .mesh_z_reader import MeshZReader
from .skin_z_reader import SkinZReader, SkinZ

class AssetImporter:
    def __init__(self) -> None:
        self.armature_obj: Object | None = None
        self.skel_z: SkelZ | None = None
        self.skin_z: SkinZ

    def import_skel_z(self, context: Context, file_path: Path) -> None:
        with open(file_path, "rb") as f:
            reader = SkelZReader()
            skel_z = reader.read_skel_z(f.read())

        # Create armature object
        armature = bpy.data.armatures.new(str(skel_z.crc))
        armature_obj = bpy.data.objects.new(str(skel_z.crc), armature)
        context.collection.objects.link(armature_obj)
        armature_obj.rotation_euler = (math.radians(90.0), 0.0, 0.0)

        context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode="EDIT")

        # Create bones
        for bone_data in skel_z.bones:
            bone = armature.edit_bones.new(str(bone_data.crc))
            bone.tail = Vector((0, 0.01, 0))
            bone.matrix = bone_data.transform

        # Update bone hierarchy and lengths
        for i, bone_data in enumerate(skel_z.bones):
            if bone_data.parent_id >= 0:
                bone = armature.edit_bones[i]
                bone.parent = armature.edit_bones[bone_data.parent_id]

                parent_distance = (bone.head - bone.parent.head).length
                bone.length = max(parent_distance, 0.01)

        bpy.ops.object.mode_set(mode="OBJECT")

        self.skel_z = skel_z
        self.armature_obj = armature_obj

    def import_skin_z(self, context: Context, file_path: Path) -> None:
        with open(file_path, "rb") as f:
            reader = SkinZReader()
            self.skin_z = reader.read_skin_z(f.read())

        self.import_skel_z(context,
            file_path.parent / f"{str(self.skin_z.skel_crc)}.Skel_Z")

        for mesh_crc in self.skin_z.mesh_crcs:
            self.import_mesh_z(
                context,
                file_path.parent / f"{str(mesh_crc)}.Mesh_Z"
            )

    def import_mesh_z(self, context: Context, file_path: Path) -> None:
        with open(file_path, "rb") as f:
            reader = MeshZReader()
            mesh_z = reader.read_mesh_z(f.read())

        for submesh in mesh_z.submeshes:
            mesh = bpy.data.meshes.new(str(mesh_z.crc))
            mesh.from_pydata(submesh.positions, [], submesh.triangles)

            # Import UVs
            uv_layer = mesh.uv_layers.new(name=f"UV0")
            for loop in mesh.loops:
                uv = submesh.uvs[loop.vertex_index]
                uv_layer.data[loop.index].uv = (uv[0], 1.0 - uv[1])

            # Import normals
            mesh.normals_split_custom_set_from_vertices(submesh.normals)

            mesh.validate()
            mesh.update()

            mesh_obj = bpy.data.objects.new(str(mesh_z.crc), mesh)
            mesh_obj.matrix_basis = submesh.transform
            context.collection.objects.link(mesh_obj)

            if not self.armature_obj or not self.skel_z:
                return

            mesh_obj.parent = self.armature_obj
            modifier = mesh_obj.modifiers.new("Armature", 'ARMATURE')
            modifier.object = self.armature_obj

            # Create and populate vertex groups
            vertex_groups = [
                mesh_obj.vertex_groups.new(name=str(bone_crc))
                for bone_crc in submesh.bone_crcs
                if bone_crc != -1
            ]

            for i, weight in enumerate(submesh.weights):
                for j, vertex_group in enumerate(vertex_groups):
                    vertex_group.add([i], weight[j], 'ADD')
