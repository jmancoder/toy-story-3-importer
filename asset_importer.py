import bpy
import math

from bpy.types import Context, Object
from mathutils import Vector
from pathlib import Path
from .skel_z_reader import SkelZReader, SkelZ


class AssetImporter:
    def __init__(self) -> None:
        self.armature_obj: Object
        self.skel_z: SkelZ

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

