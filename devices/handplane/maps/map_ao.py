import bpy
from .map import EZB_Map_Handplane


class EZB_Map_AO(bpy.types.PropertyGroup, EZB_Map_Handplane):
    id = 'AO'
    pass_name = 'ao'
    label = 'AO'
    icon = 'SHADING_RENDERED'

    suffix: bpy.props.StringProperty(default='_AO')
    active: bpy.props.BoolProperty(default=False)

    sample_radius: bpy.props.FloatProperty(name='Sample Radius', default=1.0)
    sample_count: bpy.props.IntProperty(name='Sample Count', default=20)

    background_color = [0.5, 0.5, 1.0, 1.0]

    def _draw_info(self, layout):
        layout.prop(self, 'sample_radius')
        layout.prop(self, 'sample_count')
