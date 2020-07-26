import bpy
from .. import bake_settings



class EZB_Map:
    id = 'default_map'
    material_slot = 'default'
    label = 'Default'

    active: bpy.props.BoolProperty(default=False)
    show_info: bpy.props.BoolProperty(default=False)

    settings: bpy.props.PointerProperty(type=bake_settings.bake_settings)

    copy_settings = []

    texture: bpy.props.PointerProperty(type=bpy.types.Image)

    suffix: bpy.props.StringProperty(default='')

    samples: bpy.props.IntProperty(default=1)

    background_color = [0.0, 0.0, 0.0, 0.0]

    def __lt__(self, other):
        return self.label < other.label

    def setup_settings(self):
        bake_options = bpy.context.scene.render.bake
        bpy.context.scene.cycles.bake_type = self.id
        bpy.context.scene.cycles.samples = self.samples

        for x in self.copy_settings:
            setattr(bake_options, x, getattr(self.settings, x))


    def _draw_info(self, layout):
        pass

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

        row.label(text="{}".format(self.label), icon='TEXTURE')

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
