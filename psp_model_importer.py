import bpy

from bpy.types import Context
from .model_importer import ModelImporter
from .psp_mesh_z_reader import PSPMeshZReader

class PSPModelImporter(ModelImporter):
    @staticmethod
    def import_mesh_z(context: Context, name: str, file_path: str) -> None:
        with open(file_path, "rb") as f:
            reader = PSPMeshZReader()
            reader.load_data(f.read())

        for submesh in reader.submeshes:
            mesh = bpy.data.meshes.new("Mesh")
            mesh.from_pydata(submesh.positions, [], submesh.triangles)

            mesh.validate()
            mesh.update()

            mesh_obj = bpy.data.objects.new(name, mesh)
            mesh_obj.matrix_basis = submesh.transform
            context.collection.objects.link(mesh_obj)
