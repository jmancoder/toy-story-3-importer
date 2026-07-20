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

from bpy_extras.io_utils import ImportHelper
from bpy.props import CollectionProperty, StringProperty
from bpy.types import Operator, Context, OperatorFileListElement
from pathlib import Path
from .asset_importer import AssetImporter


class SkinnedMeshImporter(Operator, ImportHelper):
    """Load a Toy Story 3 skinned mesh file."""
    bl_idname = "import_scene.ts3_skinned_mesh"
    bl_label = "Import Skin_Z"
    filename_ext = ".Skin_Z"

    filter_glob: StringProperty(
        default="*.Skin_Z",
        options={'HIDDEN'},
        maxlen=255,
    )

    directory: StringProperty(
        subtype='DIR_PATH', options={'SKIP_SAVE', 'HIDDEN'})

    files: CollectionProperty(
        type=OperatorFileListElement, options={'SKIP_SAVE', 'HIDDEN'})

    def execute(self, context: Context):
        if not self.directory:
            return {'CANCELLED'}

        for file in self.files:
            importer = AssetImporter()
            in_path = Path(self.directory) / file.name
            importer.import_skin_z(context, in_path)

        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(
        SkinnedMeshImporter.bl_idname,
        text="TS3 Skinned Mesh (.Skin_Z)"
    )


def register():
    bpy.utils.register_class(SkinnedMeshImporter)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(SkinnedMeshImporter)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
