import bpy
class EZB_Map:
    id = 'DEFAULT'
    label = 'Default'
    category = 'Surface'

    icon='TEXTURE'
    active: bpy.props.BoolProperty(default=False)
    bake: bpy.props.BoolProperty(default=True)
    show_info: bpy.props.BoolProperty(default=False)
    background_color = [0.0, 0.0, 0.0, 0.0]

    color_space: bpy.props.EnumProperty(
        items=[(y.identifier, y.name, y.description) for y in bpy.types.ColorManagedInputColorspaceSettings.bl_rna.properties['name'].enum_items],
        default='sRGB'
        )

    suffix: bpy.props.StringProperty(default='_TEST')

    # "less than", for ordering lists of this class
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
        split = row.split(factor=0.5, align=True)
        row1 = split.row(align=True)
        row1.enabled=self.bake
        row1.alignment='LEFT'
        #row.alignment = 'LEFT'
        
        row1.prop(
            self,
            'show_info',
            icon="TRIA_DOWN" if self.show_info else "TRIA_RIGHT",
            icon_only=True,
            text='',
            emboss=False
        )

        #row.label(text="{}".format(self.label), icon=self.icon)
        row1.prop(
            self,
            'show_info',
            icon=self.icon,
            icon_only=False,
            text=self.label,
            emboss=False
        )

        row2 = split.row(align=True)
        
        row2.alignment = 'RIGHT'
        row3 = row2.row(align=True)
        row3.enabled = self.bake
        row3.prop(self, "suffix", text="", emboss=True)

        row2.prop(
            self,
            'bake',
            icon="HIDE_OFF" if self.bake else "HIDE_ON",
            icon_only=True,
            text='',
            emboss=False
        )

        row2.prop(self, "active", text="", icon='X', icon_only=True, emboss=False)
        # r.operator("wm.url_open", text="", icon='QUESTION').url = self.url

        if(self.active and self.show_info and self.bake):
            row = layout.row()
            row.separator()
            row.separator()
            col = row.column(align=False)
            col.use_property_split = True
            col.use_property_decorate = False  # No animation.
            col.prop(self, 'color_space', text='Color Space')
            self._draw_info(col)
