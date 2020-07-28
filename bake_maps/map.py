import bpy
from .. import bake_settings

class Map_Context():
    def __init__(self, baker, map, high, low):
        self.baker = baker
        self.map = map
        self.high = high
        self.low = low

        self.original_materials_low = [x.material for x in low.material_slots]
        self.original_materials_high = {y: [x.material for x in y.material_slots] for y in high}

    def __enter__(self):
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')
        self.low.select_set(True)
        bpy.context.view_layer.objects.active = self.low
        for x in self.high:
            x.select_set(True)

        self.baker.setup_bake_material(self.low, self.map)
        cage = bpy.context.scene.objects.get(self.low.name + bpy.context.scene.EZB_Settings.suffix_cage)
        bpy.context.scene.render.bake.cage_object = cage

        return self.map.pass_name

    def __exit__(self, type, value, traceback):
        for i, x in enumerate(self.original_materials_low):
            self.low.material_slots[i].material = x

class EZB_Map:
    id = 'default_map'
    material_slot = 'default'
    pass_name = 'default'
    label = 'Default'

    active: bpy.props.BoolProperty(default=False)
    show_info: bpy.props.BoolProperty(default=False)

    settings: bpy.props.PointerProperty(type=bake_settings.bake_settings)

    copy_settings = []

    texture: bpy.props.PointerProperty(type=bpy.types.Image)

    suffix: bpy.props.StringProperty(default='')

    samples: bpy.props.IntProperty(default=1)

    background_color = [0.0, 0.0, 0.0, 0.0]

    context = Map_Context

    def __lt__(self, other):
        return self.label < other.label

    def setup_settings(self):
        bake_options = bpy.context.scene.render.bake
        bpy.context.scene.cycles.bake_type = self.pass_name
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
