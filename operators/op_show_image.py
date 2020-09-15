import bpy


class EZB_OT_show_image(bpy.types.Operator):
    """Show Image"""
    bl_idname = "ezb.show_image"
    bl_label = "Show Image"

    image: bpy.props.StringProperty()

    def execute(self, context):
        image = bpy.data.images.get(self.image)
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'IMAGE_EDITOR':
                    area.spaces.active.image = image
                    return {'FINISHED'}
        return {'FINISHED'}
