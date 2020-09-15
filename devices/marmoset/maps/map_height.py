import bpy
from .map import EZB_Map_Marmoset


class EZB_Map_Height(bpy.types.PropertyGroup, EZB_Map_Marmoset):
    id = 'Height'
    label = 'Height'
    icon = 'EMPTY_SINGLE_ARROW'
    category = 'Surface'

    suffix: bpy.props.StringProperty(default='_height')
    active: bpy.props.BoolProperty(default=False)

    dither: bpy.props.BoolProperty(default=True, name='Dither')
    innerDistance: bpy.props.FloatProperty(default=-8.0, name='Inner Distance', min=-100, max=100, subtype='FACTOR')
    outerDistance: bpy.props.FloatProperty(default=4.0, name='Outer Distance', min=-100, max=100, subtype='FACTOR')

    settings_to_copy = ['dither', 'innerDistance', 'outerDistance']

    def _draw_info(self, layout):
        layout.prop(self, 'dither')
        layout.prop(self, 'innerDistance')
        layout.prop(self, 'outerDistance')
