import bpy
from .map import EZB_Map_Blender


class EZB_Map_Diffuse(bpy.types.PropertyGroup, EZB_Map_Blender):
    id = 'DIFFUSE'
    pass_name = 'DIFFUSE'
    label = 'Diffuse'
    icon = 'COLOR'
    category = 'Surface'

    suffix: bpy.props.StringProperty(default='_D')
    samples: bpy.props.IntProperty(name='Samples', default=128)

    use_pass_direct: bpy.props.BoolProperty(default=False, name='Direct', description='Bake direct light')
    use_pass_indirect: bpy.props.BoolProperty(default=False, name='Indirect', description='Bake indirect light')
    use_pass_color: bpy.props.BoolProperty(default=True, name='Color', description='Bake the surface color')

    def setup_settings(self):
        super().setup_settings()
        scene = self.id_data
        scene.render.bake.use_pass_direct = self.use_pass_direct
        scene.render.bake.use_pass_indirect = self.use_pass_indirect
        scene.render.bake.use_pass_color = self.use_pass_color

    def _draw_info(self, layout):
        row = layout.row(align=True)
        row.use_property_split = False
        row.prop(self, 'use_pass_direct', toggle=True)
        row.prop(self, 'use_pass_indirect', toggle=True)
        row.prop(self, 'use_pass_color', toggle=True)

        layout.prop(self, 'samples', toggle=True)
