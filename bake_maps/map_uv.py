import bpy
from .map import EZB_Map

class EZB_Map_UV(bpy.types.PropertyGroup, EZB_Map):
    id = 'UV'
    pass_name = 'UV'
    label = 'UV'
    icon = 'UV'

    suffix: bpy.props.StringProperty(default='_UV')