import bpy
from .map import EZB_Map

class EZB_Map_AO(bpy.types.PropertyGroup, EZB_Map):
    id = 'AO'
    label = 'Ambient Occlusion'

    suffix: bpy.props.StringProperty(default='_AO')