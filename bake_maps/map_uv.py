import bpy
from .map import EZB_Map

class EZB_Map_UV(bpy.types.PropertyGroup, EZB_Map):
    id = 'UV'
    label = 'UV'

    suffix: bpy.props.StringProperty(default='_UV')