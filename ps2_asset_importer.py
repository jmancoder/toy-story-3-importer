import bpy

from bpy.types import Context
from pathlib import Path
from .asset_importer import AssetImporter
from .ps2_skin_z_reader import PS2SkinZReader
from .ps2_mesh_z_reader import PS2MeshZReader
from .ps2_mesh_data_z_reader import PS2MeshDataZReader


class PS2AssetImporter(AssetImporter):
    def __init__(self) -> None:
        super().__init__()

    def import_skin_z(self, context: Context, file_path: Path) -> None:
        with open(file_path, "rb") as f:
            reader = PS2SkinZReader()
            skin_z = reader.read_skin_z(f.read())

        if skin_z.skel_crc != 0:
            skel_z_path = file_path.parent / f"{skin_z.skel_crc}.Skel_Z"
            self.import_skel_z(context, skel_z_path)

        for mesh_crc in skin_z.mesh_crcs:
            mesh_path = file_path.parent / f"{mesh_crc}.Mesh_Z"
            self.import_mesh_z(context, mesh_path)

    def import_mesh_z(self, context: Context,
            file_path: Path) -> None:
        with open(file_path, "rb") as f:
            reader = PS2MeshZReader()
            mesh_z = reader.read_mesh_z(f.read())

        mesh_data_path = file_path.parent / f"{mesh_z.mesh_data_crc}.MeshData_Z"
        self.import_mesh_data_z(context, mesh_data_path)

    def import_mesh_data_z(self, context: Context, file_path: Path) -> None:
        with open(file_path, "rb") as f:
            reader = PS2MeshDataZReader()
            mesh_data_z = reader.read_mesh_data_z(f.read())

        mesh = bpy.data.meshes.new(str(mesh_data_z.crc))
        mesh.from_pydata(mesh_data_z.positions_0, [], mesh_data_z.triangles)

        # Transfer normals from faces to loops
        loop_normals = []
        for poly in mesh.polygons:
            for _ in range(3):
                loop_normals.append(mesh_data_z.face_normals[poly.index])
        mesh.normals_split_custom_set(loop_normals)

        # Store unknown data in custom attributes
        if len(mesh_data_z.unk_vert_attrs_0) > 0:
            unk_vert_attr_0 = mesh.attributes.new(
                name=f"unk_vert_value", type='INT', domain='POINT')
            unk_vert_attr_0.data.foreach_set("value",
                mesh_data_z.unk_vert_attrs_0)

        if len(mesh_data_z.unk_face_attrs_0) > 0:
            unk_face_attr_0 = mesh.attributes.new(
                name=f"unk_face_value_0", type='INT', domain='FACE')
            unk_face_attr_0.data.foreach_set("value",
                mesh_data_z.unk_face_attrs_0)

        if len(mesh_data_z.unk_face_attrs_1) > 0:
            unk_face_attr_1 = mesh.attributes.new(
                name=f"unk_face_value_1", type='INT', domain='FACE')
            unk_face_attr_1.data.foreach_set("value",
                mesh_data_z.unk_face_attrs_1)

        mesh.validate()
        mesh.update()

        # Create mesh object
        mesh_obj = bpy.data.objects.new(str(mesh_data_z.crc), mesh)
        context.collection.objects.link(mesh_obj)

        if not self.armature_obj or not self.skel_z:
            return

        mesh_obj.parent = self.armature_obj
        modifier = mesh_obj.modifiers.new("Armature", 'ARMATURE')
        modifier.object = self.armature_obj
