import bpy

from bpy.types import Context
from .asset_importer import AssetImporter
from .psp_mesh_z_reader import PSPMeshZReader

class PSPAssetImporter(AssetImporter):
    @staticmethod
    def import_mesh_z(context: Context, name: str, file_path: str) -> None:
        with open(file_path, "rb") as f:
            reader = PSPMeshZReader()
            reader.load_data(f.read())

        for submesh in reader.submeshes:
            mesh = bpy.data.meshes.new("Mesh")
            mesh.from_pydata(submesh.positions, [], submesh.triangles)

            # Import UVs
            uv_layer = mesh.uv_layers.new(name=f"UV0")
            for loop in mesh.loops:
                uv = submesh.uvs[loop.vertex_index][:2]
                uv_layer.data[loop.index].uv = (uv[0], 1.0 - uv[1])

            # Import unknown attributes
            for i in range(4):
                unk_0_attr = mesh.attributes.new(
                    name=f"unk_a_{i}", type='INT', domain='POINT')
                unk_0_attr.data.foreach_set("value",
                    [col[i] for col in submesh.unks_0])
                
                unk_1_attr = mesh.attributes.new(
                    name=f"unk_b_{i}", type='INT', domain='POINT')
                unk_1_attr.data.foreach_set("value",
                    [col[i] for col in submesh.unks_1])

            mesh.validate()
            mesh.update()

            mesh_obj = bpy.data.objects.new(name, mesh)
            mesh_obj.matrix_basis = submesh.transform
            context.collection.objects.link(mesh_obj)
