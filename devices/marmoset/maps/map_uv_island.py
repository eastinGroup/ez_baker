import bpy
from .map import EZB_Map_Marmoset


class EZB_Map_UV_Island(bpy.types.PropertyGroup, EZB_Map_Marmoset):
    id = 'UV Island'
    label = 'UV Island'
    icon = 'UV'
    category = 'IDs & Masks'

    suffix: bpy.props.StringProperty(default='_uvisland')
    active: bpy.props.BoolProperty(default=False)

    def _draw_info(self, layout):
        pass
