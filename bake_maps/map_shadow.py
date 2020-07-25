import bpy
from .map import EZB_Map

class EZB_Map_Shadow(bpy.types.PropertyGroup, EZB_Map):
    id = 'SHADOW'
    label = 'Shadow'

    suffix: bpy.props.StringProperty(default='_SH')