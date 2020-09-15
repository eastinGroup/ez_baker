import bpy


class EZB_OT_select_object(bpy.types.Operator):
    """Select Object"""
    bl_idname = "ezb.select_object"
    bl_label = "Select Object"

    name: bpy.props.StringProperty()

    def execute(self, context):
        obj = context.scene.objects.get(self.name)
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')
        if obj:
            obj.select_set(True)
        return {'FINISHED'}
