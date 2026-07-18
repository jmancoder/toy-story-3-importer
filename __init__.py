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
from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator, Context
from pathlib import Path
from .ps2_asset_importer import PS2AssetImporter
from .psp_asset_importer import PSPAssetImporter


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

    platform: EnumProperty(
        name="Game Platform",
        description="Whether the files were exported" \
            "from the PS2 or the PSP version of Toy Story 3",
        items=(
            ('PSP', "PSP", ""),
            ('PS2', "PS2", ""),
        ),
        default='PSP',
    )

    def execute(self, context: Context):
        in_path = Path(self.filepath)
        if self.platform == 'PSP':
            importer = PSPAssetImporter()
        else:
            importer = PS2AssetImporter()

        importer.import_skin_z(context, in_path)

        return {'FINISHED'}


class StaticMeshImporter(Operator, ImportHelper):
    """Load a Toy Story 3 static mesh file."""
    bl_idname = "import_scene.ts3_static_mesh"
    bl_label = "Import Mesh_Z"
    filename_ext = ".Mesh_Z"

    filter_glob: StringProperty(
        default="*.Mesh_Z",
        options={'HIDDEN'},
        maxlen=255,
    )

    platform: EnumProperty(
        name="Game Platform",
        description="Whether the files were exported" \
            "from the PS2 or the PSP version of Toy Story 3",
        items=(
            ('PSP', "PSP", ""),
            ('PS2', "PS2", ""),
        ),
        default='PSP',
    )

    def execute(self, context: Context):
        in_path = Path(self.filepath)
        if self.platform == 'PSP':
            importer = PSPAssetImporter()
        else:
            importer = PS2AssetImporter()

        importer.import_mesh_z(context, in_path)

        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(
        SkinnedMeshImporter.bl_idname,
        text="TS3 Skinned Mesh (.Skin_Z)"
    )

    self.layout.operator(
        StaticMeshImporter.bl_idname,
        text="TS3 Static Mesh (.Mesh_Z)"
    )


def register():
    bpy.utils.register_class(SkinnedMeshImporter)
    bpy.utils.register_class(StaticMeshImporter)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(SkinnedMeshImporter)
    bpy.utils.unregister_class(StaticMeshImporter)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
