import bpy


class EZB_OT_bake(bpy.types.Operator):
    """Bake"""
    bl_idname = "ezb.bake"
    bl_label = "Bake"

    @classmethod
    def description(cls, context, properties):
        if not (context.scene.EZB_Settings.baker_index >= 0 and len(context.scene.EZB_Settings.bakers) > context.scene.EZB_Settings.baker_index):
            return 'No baker selected'
        baker = context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        device = baker.child_device
        ans = baker.check_for_errors(context)
        if ans:
            return ans
        ans = device.check_for_errors(context)
        if ans:
            return ans
        return 'Bake'

    @classmethod
    def poll(cls, context):
        if not (context.scene.EZB_Settings.baker_index >= 0 and len(context.scene.EZB_Settings.bakers) > context.scene.EZB_Settings.baker_index):
            return False
        baker = context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        device = baker.child_device
        ans = baker.check_for_errors(context)
        if ans:
            return False
        ans = device.check_for_errors(context)
        if ans:
            return False
        return True

    def execute(self, context):
        baker = context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        baker.bake()
        return {'FINISHED'}
