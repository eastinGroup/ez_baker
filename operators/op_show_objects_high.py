import bpy


class EZB_OT_show_high_objects(bpy.types.Operator):
    """Show High Objects"""
    bl_idname = "ezb.show_high_objects"
    bl_label = "Show High Objects"

    index: bpy.props.IntProperty(name="index")

    @classmethod
    def description(cls, context, properties):
        ans = ''
        baker = context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        bake_group = baker.bake_groups[properties.index]
        for x in bake_group.objects_high:
            ans += x.name + '\n'
        return ans

    def execute(self, context):
        baker = context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        bake_group = baker.bake_groups[self.index]
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')
        for x in bake_group.objects_high:
            x.select_set(True)
        return {'FINISHED'}
