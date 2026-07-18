import bpy

from bpy.types import Context, Object
from mathutils import Vector
from pathlib import Path
from .skel_z_reader import SkelZReader, SkelZ


class AssetImporter:
    def __init__(self) -> None:
        self.skel_z: SkelZ

    def import_skel_z(self, context: Context, file_path: Path) -> Object:
        with open(file_path, "rb") as f:
            reader = SkelZReader()
            skel_z = reader.read_skel_z(f.read())

        # Create armature object
        armature = bpy.data.armatures.new(str(skel_z.crc))
        armature_obj = bpy.data.objects.new(str(skel_z.crc), armature)
        context.collection.objects.link(armature_obj)

        context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode="EDIT")

        # Create bones
        for i, bone_data in enumerate(skel_z.bones):
            bone = armature.edit_bones.new(str(bone_data.crc))
            bone.tail = Vector((0, 0.05, 0))
            armature.edit_bones[i].matrix = bone_data.transform

        # Update bone hierarchy
        for i, bone_data in enumerate(skel_z.bones):
            if bone_data.parent_id >= 0:
                armature.edit_bones[i].parent = armature.edit_bones[bone_data.parent_id]

        bpy.ops.object.mode_set(mode="OBJECT")
        self.skel_z = skel_z

        return armature_obj
