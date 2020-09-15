import bpy


class EZB_OT_remove_bake_group(bpy.types.Operator):
    """Remove Bake Group"""
    bl_idname = "ezb.remove_bake_group"
    bl_label = "Remove Bake Group"

    @classmethod
    def poll(cls, context):
        baker = context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        return len(baker.bake_groups) > baker.bake_group_index

    def execute(self, context):
        baker = context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]

        baker.bake_groups[baker.bake_group_index].preview_cage = False
        baker.bake_groups.remove(baker.bake_group_index)

        if baker.bake_group_index >= len(baker.bake_groups):
            baker.bake_group_index = len(baker.bake_groups) - 1
        return {'FINISHED'}
