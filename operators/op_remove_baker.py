import bpy


class EZB_OT_remove_baker(bpy.types.Operator):
    """Remove Baker"""
    bl_idname = "ezb.remove_baker"
    bl_label = "Remove Baker"

    @classmethod
    def poll(cls, context):
        ezb_settings = context.scene.EZB_Settings
        return len(ezb_settings.bakers) > ezb_settings.baker_index

    def execute(self, context):
        ezb_settings = context.scene.EZB_Settings

        baker = ezb_settings.bakers[ezb_settings.baker_index]
        for bake_group in baker.bake_groups:
            bake_group.preview_cage = False

        ezb_settings.bakers.remove(ezb_settings.baker_index)
        if ezb_settings.baker_index >= len(ezb_settings.bakers):
            ezb_settings.baker_index = len(ezb_settings.bakers) - 1
        return {'FINISHED'}
