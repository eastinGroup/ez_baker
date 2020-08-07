import bpy
from .map import EZB_Map_Handplane

class EZB_Map_Thickness(bpy.types.PropertyGroup, EZB_Map_Handplane):
    id = 'THICKNESS'
    pass_name = 'thickness'
    label = 'Thickness'
    icon = 'META_DATA'

    suffix: bpy.props.StringProperty(default='_THCK')
    active: bpy.props.BoolProperty(default=False)

    sample_radius: bpy.props.FloatProperty(name='Sample Radius', default=1.0)
    sample_count: bpy.props.IntProperty(name='Sample Count', default=20)

    background_color = [0.5, 0.5, 1.0, 1.0]

    def _draw_info(self, layout):
        layout.prop(self, 'sample_radius')
        layout.prop(self, 'sample_count')

        