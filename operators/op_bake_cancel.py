
import bpy


class EZB_OT_cancel_bake(bpy.types.Operator):
    """Cancel Bake"""
    bl_idname = "ezb.cancel_bake"
    bl_label = "Cancel Bake"

    @classmethod
    def poll(cls, context):
        if not (context.scene.EZB_Settings.baker_index >= 0 and len(context.scene.EZB_Settings.bakers) > context.scene.EZB_Settings.baker_index):
            return False
        return True

    def execute(self, context):
        baker = context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        baker.cancel_current_bake = True
        baker.is_baking = False
        return {'FINISHED'}
