import bpy

from bpy.types import Context, Object
from pathlib import Path
from .asset_importer import AssetImporter
from .psp_mesh_z_reader import PSPMeshZReader
from .psp_skin_z_reader import PSPSkinZReader, SkinZ

class PSPAssetImporter(AssetImporter):
    def __init__(self) -> None:
        self.skin_z: SkinZ

    def import_skin_z(self, context: Context, file_path: Path) -> None:
        with open(file_path, "rb") as f:
            reader = PSPSkinZReader()
            self.skin_z = reader.read_skin_z(f.read())

        # Create skeleton (armature) object
        skel_obj = self.import_skel_z(context,
            file_path.parent / f"{str(self.skin_z.skel_crc)}.Skel_Z")

        for group in self.skin_z.point_groups:
            ids_0 = [group.points_0[i][0] for i in range(len(group.points_0))]
            ids_1 = [group.points_1[i][0] for i in range(len(group.points_1))]
            print(max(ids_0), max(ids_1))

        # Create mesh objects
        for mesh_crc in self.skin_z.mesh_crcs:
            mesh_objs = self.import_mesh_z(context,
                file_path.parent / f"{str(mesh_crc)}.Mesh_Z")
            for mesh_obj in mesh_objs:
                mesh_obj.parent = skel_obj

                modifier = mesh_obj.modifiers.new("Armature", 'ARMATURE')
                modifier.object = skel_obj

                vertex_groups = [
                    mesh_obj.vertex_groups.new(name=str(bone.crc))
                    for bone in self.skel_z.bones
                ]

    def import_mesh_z(self, context: Context, file_path: Path) -> list[Object]:
        with open(file_path, "rb") as f:
            reader = PSPMeshZReader()
            mesh_z = reader.read_mesh_z(f.read())

        mesh_objs = []
        for submesh in mesh_z.submeshes:
            mesh = bpy.data.meshes.new(str(mesh_z.crc))
            mesh.from_pydata(submesh.positions, [], submesh.triangles)

            # Import UVs
            uv_layer = mesh.uv_layers.new(name=f"UV0")
            for loop in mesh.loops:
                uv = submesh.uvs[loop.vertex_index][:2]
                uv_layer.data[loop.index].uv = (uv[0], 1.0 - uv[1])

            mesh.validate()
            mesh.update()

            mesh_obj = bpy.data.objects.new(str(mesh_z.crc), mesh)
            mesh_obj.matrix_basis = submesh.transform
            context.collection.objects.link(mesh_obj)
            mesh_objs.append(mesh_obj)

        return mesh_objs
