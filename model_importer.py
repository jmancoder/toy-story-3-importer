import bpy

from bpy.types import Context
from mathutils import Vector
from .skel_z_reader import SkelZReader


class ModelImporter:
    @staticmethod
    def import_skel_z(context: Context, name: str, file_path: str) -> None:
        with open(file_path, "rb") as f:
            skel = SkelZReader()
            skel.load_data(f.read())
        
        # Create armature object
        armature = bpy.data.armatures.new(f"Armature")
        armature_obj = bpy.data.objects.new(name, armature)
        context.collection.objects.link(armature_obj)

        context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode="EDIT")

        # Create bone hierarchy
        for i, parent_id in enumerate(skel.bone_parent_ids):
            bone = armature.edit_bones.new(f"Bone_{i}")
            bone.tail = Vector((0, 0.05, 0))
            if parent_id >= 0:
                bone.parent = armature.edit_bones[parent_id]
        
        # Update bone matrices
        for i, bone_matrix in enumerate(skel.bone_matrices):
            armature.edit_bones[i].matrix = bone_matrix

        bpy.ops.object.mode_set(mode="OBJECT")
