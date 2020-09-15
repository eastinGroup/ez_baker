import bpy


class EZB_OT_preview_image(bpy.types.Operator):
    """Preview image"""
    bl_idname = "ezb.preview_image"
    bl_label = "Preview Image"
    bl_options = {'UNDO'}

    scene: bpy.props.StringProperty()
    datapath: bpy.props.StringProperty()

    def execute(self, context):
        bpy.data.scenes.get(self.scene).path_resolve(self.datapath).preview()
        if context.space_data.shading.type == 'SOLID':
            context.space_data.shading.color_type = 'TEXTURE'

        return {'FINISHED'}
