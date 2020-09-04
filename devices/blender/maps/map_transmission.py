import bpy
from .map import EZB_Map_Blender


class EZB_Map_Transmission(bpy.types.PropertyGroup, EZB_Map_Blender):
    id = 'TRANSMISSION'
    pass_name = 'TRANSMISSION'
    label = 'Transmission'
    icon = 'COLOR'
    category = 'Surface'
    suffix: bpy.props.StringProperty(default='_TS')

    color_space = 'Non-Color'
