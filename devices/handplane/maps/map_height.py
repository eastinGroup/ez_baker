import bpy
from .map import EZB_Map_Handplane


class EZB_Map_Height(bpy.types.PropertyGroup, EZB_Map_Handplane):
    id = 'HEIGHT'
    pass_name = 'height'
    label = 'Height'
    icon = 'MOD_SMOOTH'

    suffix: bpy.props.StringProperty(default='_HGHT')
    active: bpy.props.BoolProperty(default=False)

    scale: bpy.props.FloatProperty(name='Scale', default=1.0)
    offset: bpy.props.FloatProperty(name='Offset', default=0.0)

    background_color = [0.5, 0.5, 1.0, 1.0]

    def _draw_info(self, layout):
        layout.prop(self, 'scale')
        layout.prop(self, 'offset')
