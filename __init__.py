bl_info = {
    "name": "ADDON_NAME",
    "author": "AUTHOR_NAME",
    "description": "",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "File > Import",
    "category": "Import-Export",
}


import bpy
import os

from bpy_extras.io_utils import ImportHelper
from bpy.props import CollectionProperty, EnumProperty, StringProperty
from bpy.types import Operator, Context, OperatorFileListElement
from .ps2_model_importer import PS2ModelImporter
from .psp_model_importer import PSPModelImporter


class TS3Importer(Operator, ImportHelper):
    bl_idname = "import_scene.ts3_asset"
    bl_label = "Import Toy Story 3 Asset"

    directory: StringProperty(
        subtype='DIR_PATH', options={'SKIP_SAVE', 'HIDDEN'})

    files: CollectionProperty(
        type=OperatorFileListElement, options={'SKIP_SAVE', 'HIDDEN'})
    
    platform: EnumProperty(
        name="Game Platform",
        description="Whether the files were exported from the PS2 or the PSP version of Toy Story 3",
        items=(
            ('PSP', "PSP", "PSP"),
            ('PS2', "PS2", "PS2"),
        ),
        default='PSP',
    )

    def execute(self, context: Context):
        if not self.directory:
            return {'CANCELLED'}

        for file in self.files:
            file_path = os.path.join(self.directory, file.name)
            if self.platform == 'PSP':
                if file.name.endswith("Mesh_Z"):
                    PSPModelImporter.import_mesh_z(context, file.name, file_path)
                if file.name.endswith("Skel_Z"):
                    PSPModelImporter.import_skel_z(context, file.name, file_path)
                if file.name.endswith("MeshData_Z"):
                    pass
            else:
                if file.name.endswith("Mesh_Z"):
                    pass
                if file.name.endswith("Skel_Z"):
                    PS2ModelImporter.import_skel_z(context, file.name, file_path)
                if file.name.endswith("MeshData_Z"):
                    PS2ModelImporter.import_mesh_data_z(context, file.name, file_path)

        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(
        TS3Importer.bl_idname,
        text="Toy Story 3 Asset"
    )


def register():
    bpy.utils.register_class(TS3Importer)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(TS3Importer)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
