import bpy
class EZB_Map:
    id = 'DEFAULT'
    label = 'Default'

    icon='TEXTURE'
    active: bpy.props.BoolProperty(default=False)
    show_info: bpy.props.BoolProperty(default=False)
    background_color = [0.0, 0.0, 0.0, 0.0]

    suffix: bpy.props.StringProperty(default='_TEST')

    def __lt__(self, other):
        return self.label < other.label

    def _draw_info(self, layout):
        pass

    def draw_prop_with_warning(self, layout, obj, prop_name, max_limit):
        row = layout.row()
        if getattr(obj, prop_name) >= max_limit:
            row.alert=True
            
        row.prop(obj, prop_name, toggle=True)
        if row.alert:
            row.label(text='', icon= 'ERROR')

    def draw(self, layout):
        row = layout.row(align=True)
        row.prop(
            self,
            'show_info',
            icon="TRIA_DOWN" if self.show_info else "TRIA_RIGHT",
            icon_only=True,
            text='',
            emboss=False
        )

        row.label(text="{}".format(self.label), icon=self.icon)

        row = row.row(align=True)
        row.enabled = self.active
        row.alignment = 'RIGHT'
        
        row.prop(self, "suffix", text="", emboss=True)

        row.prop(self, "active", text="", icon='X', icon_only=True, emboss=False)
        # r.operator("wm.url_open", text="", icon='QUESTION').url = self.url

        if(self.active and self.show_info):
            row = layout.row()
            row.separator()
            row.separator()
            col = row.column(align=False)
            col.use_property_split = True
            col.use_property_decorate = False  # No animation.
            self._draw_info(col)
