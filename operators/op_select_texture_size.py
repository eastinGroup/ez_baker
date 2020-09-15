import bpy


class EZB_OT_select_texture_size(bpy.types.Operator):
    """Select Texture Size"""
    bl_idname = "ezb.select_texture_size"
    bl_label = "Select Texture Size"

    size: bpy.props.EnumProperty(items=[
        ('256', '256', '256'),
        ('512', '512', '512'),
        ('1024', '1k', '1024'),
        ('2048', '2k', '2048'),
        ('4096', '4k', '4096'),
        ('8192', '8k', '8192'),
    ])

    def execute(self, context):
        baker = context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        if self.size == '256':
            baker.width = 256
            baker.height = 256
        elif self.size == '512':
            baker.width = 512
            baker.height = 512
        elif self.size == '1024':
            baker.width = 1024
            baker.height = 1024
        elif self.size == '2048':
            baker.width = 2048
            baker.height = 2048
        elif self.size == '4096':
            baker.width = 4096
            baker.height = 4096
        elif self.size == '8192':
            baker.width = 8192
            baker.height = 8192
        return {'FINISHED'}
