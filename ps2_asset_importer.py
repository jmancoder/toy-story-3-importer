import bpy

from bpy.types import Context
from .asset_importer import AssetImporter
from .ps2_meshdata_z_reader import PS2MeshDataZReader

class PS2AssetImporter(AssetImporter):
    @staticmethod
    def import_mesh_data_z(context: Context, name: str, file_path: str) -> None:
        with open(file_path, "rb") as f:
            mesh_data = PS2MeshDataZReader()
            mesh_data.load_data(f.read())

        mesh = bpy.data.meshes.new("Mesh")
        mesh.from_pydata(mesh_data.positions, [], mesh_data.triangles)

        # Transfer normals from faces to loops
        loop_normals = []
        for poly in mesh.polygons:
            for _ in range(3):
                loop_normals.append(mesh_data.face_normals[poly.index])
        mesh.normals_split_custom_set(loop_normals)

        # Store unknown data in custom attributes
        if len(mesh_data.unk_vert_values) > 0:
            unk_vert_attr = mesh.attributes.new(
                name=f"unk_vert_value", type='INT', domain='POINT')
            unk_vert_attr.data.foreach_set("value", mesh_data.unk_vert_values)

        if len(mesh_data.unk_face_values_0) > 0:
            unk_face_attr_0 = mesh.attributes.new(
                name=f"unk_face_value_0", type='INT', domain='FACE')
            unk_face_attr_0.data.foreach_set("value", mesh_data.unk_face_values_0)

        if len(mesh_data.unk_face_values_0) > 0:
            unk_face_attr_1 = mesh.attributes.new(
                name=f"unk_face_value_1", type='INT', domain='FACE')
            unk_face_attr_1.data.foreach_set("value", mesh_data.unk_face_values_1)

        mesh.validate()
        mesh.update()

        # Create mesh object
        mesh_obj = bpy.data.objects.new(name, mesh)
        context.collection.objects.link(mesh_obj)
