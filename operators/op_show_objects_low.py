import bpy


class EZB_OT_show_low_objects(bpy.types.Operator):
    """Show Low Objects"""
    bl_idname = "ezb.show_low_objects"
    bl_label = "Show Low Objects"

    index: bpy.props.IntProperty(name="index")

    @classmethod
    def description(cls, context, properties):
        ans = ''
        baker = context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        bake_group = baker.bake_groups[properties.index]
        for x in bake_group.objects_low:
            ans += x.name + '\n'
        return ans

    def execute(self, context):
        baker = context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        bake_group = baker.bake_groups[self.index]
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')
        for x in bake_group.objects_low:
            x.select_set(True)
        return {'FINISHED'}
