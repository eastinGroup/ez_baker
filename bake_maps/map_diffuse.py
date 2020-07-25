import bpy
from .map import EZB_Map

class EZB_Map_Diffuse(bpy.types.PropertyGroup, EZB_Map):
    id = 'DIFFUSE'
    label = 'Diffuse'

    copy_settings = ['use_pass_direct', 'use_pass_indirect', 'use_pass_color']

    suffix: bpy.props.StringProperty(default='_D')

    def _draw_info(self, layout):
        row = layout.row(align=True)
        row.use_property_split = False
        row.prop(self.settings, 'use_pass_direct', toggle=True)
        row.prop(self.settings, 'use_pass_indirect', toggle=True)
        row.prop(self.settings, 'use_pass_color', toggle=True)