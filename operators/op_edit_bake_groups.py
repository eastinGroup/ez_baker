import bpy


class EZB_OT_edit_bake_groups(bpy.types.Operator):
    """Edit selected bake groups"""
    bl_idname = "ezb.edit_bake_groups"
    bl_label = "Edit Selected Bake Groups"

    def update_cage(self, context):
        baker = context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        for x in baker.bake_groups:
            if any(y.select_get() for y in x.objects_high) or any(y.select_get() for y in x.objects_low):
                x.cage_displacement = self.cage_displacement

    def update_cage_visible(self, context):
        baker = context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        for x in baker.bake_groups:
            if any(y.select_get() for y in x.objects_high) or any(y.select_get() for y in x.objects_low):
                x.preview_cage = self.preview_cage

    cage_displacement: bpy.props.FloatProperty(name='Cage Displacement', default=0.05, step=0.1, precision=3, update=update_cage)
    preview_cage: bpy.props.BoolProperty(update=update_cage_visible, default=True)

    @classmethod
    def poll(cls, context):
        if not context.selected_objects:
            return False
        return True

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.prop(
            self,
            'preview_cage',
            text='',
            icon="HIDE_OFF" if self.preview_cage else "HIDE_ON",
            icon_only=True,
            emboss=False
        )
        row.prop(self, 'cage_displacement')

    def invoke(self, context, event):
        wm = context.window_manager
        self.preview_cage = True
        return wm.invoke_props_dialog(self)

    def execute(self, context):

        return {'FINISHED'}
