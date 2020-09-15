import bpy
from .map import EZB_Map_Marmoset


class EZB_Map_Concavity(bpy.types.PropertyGroup, EZB_Map_Marmoset):
    id = 'Concavity'
    label = 'Concavity'
    icon = 'SHARPCURVE'
    category = 'Surface'

    suffix: bpy.props.StringProperty(default='_concave')
    active: bpy.props.BoolProperty(default=False)

    dither: bpy.props.BoolProperty(default=True, name='Dither')
    normalize: bpy.props.BoolProperty(default=True, name='Normalize')
    strength: bpy.props.FloatProperty(default=1.0, name='Strength', min=0, max=3.0, subtype='FACTOR')

    settings_to_copy = ['dither', 'normalize', 'strength']

    def _draw_info(self, layout):
        layout.prop(self, 'dither')
        layout.prop(self, 'normalize')
        layout.prop(self, 'strength')
