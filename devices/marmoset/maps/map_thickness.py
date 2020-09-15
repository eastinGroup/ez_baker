import bpy
from .map import EZB_Map_Marmoset


class EZB_Map_Thickness(bpy.types.PropertyGroup, EZB_Map_Marmoset):
    id = 'Thickness'
    label = 'Thickness'
    icon = 'OUTLINER_OB_META'
    category = 'Surface'

    suffix: bpy.props.StringProperty(default='_thickness')
    active: bpy.props.BoolProperty(default=False)

    dither: bpy.props.BoolProperty(default=True, name='Dither')
    rayCount: bpy.props.IntProperty(default=256, name='Ray Count', min=32, max=4096, subtype='FACTOR')

    # TODO: search distance and Bias not available in the API?

    settings_to_copy = ['dither', 'rayCount']

    def _draw_info(self, layout):
        layout.prop(self, 'dither')
        layout.prop(self, 'rayCount')
