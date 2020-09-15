import bpy


class EZB_OT_new_baker(bpy.types.Operator):
    """Create a new Baker"""
    bl_idname = "ezb.new_baker"
    bl_label = "New Baker"

    @classmethod
    def poll(cls, context):
        ezb_settings = context.scene.EZB_Settings
        return True

    def execute(self, context):
        ezb_settings = context.scene.EZB_Settings
        new_baker = ezb_settings.bakers.add()
        index = len(ezb_settings.bakers) - 1
        ezb_settings.baker_index = index
        new_baker.key = 'Baker_{}'.format(index)
        return {'FINISHED'}
