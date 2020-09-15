import bpy
from .. import bake_group


class EZB_OT_show_cage(bpy.types.Operator):
    """Show/Hide Cage"""
    bl_idname = "ezb.show_cage"
    bl_label = "Show Cage"
    bl_options = {'INTERNAL'}

    index: bpy.props.IntProperty()

    def execute(self, context):
        baker = context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        bg = baker.bake_groups[self.index]
        bg.preview_cage = not bg.preview_cage

        bake_group.update_cage(bg, context)
        return {'FINISHED'}
