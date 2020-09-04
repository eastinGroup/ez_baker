import bpy
from .map import EZB_Map_Blender


class EZB_Map_Roughness(bpy.types.PropertyGroup, EZB_Map_Blender):
    id = 'ROUGHNESS'
    pass_name = 'ROUGHNESS'
    label = 'Roughness'
    icon = 'COLOR'
    category = 'Surface'
    suffix: bpy.props.StringProperty(default='_R')

    color_space = 'Non-Color'
