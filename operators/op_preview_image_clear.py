import bpy


class EZB_OT_clear_preview_image(bpy.types.Operator):
    """Clear preview image"""
    bl_idname = "ezb.clear_preview_image"
    bl_label = "Clear Preview Image"
    bl_options = {'UNDO'}

    scene: bpy.props.StringProperty()
    datapath: bpy.props.StringProperty()

    def execute(self, context):
        bpy.data.scenes.get(self.scene).path_resolve(self.datapath).clear_preview_material()

        return {'FINISHED'}
