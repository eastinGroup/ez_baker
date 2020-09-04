import bpy
from .map import EZB_Map_Blender


class EZB_Map_Glossy(bpy.types.PropertyGroup, EZB_Map_Blender):
    id = 'GLOSSY'
    pass_name = 'GLOSSY'
    label = 'Glossy'
    icon = 'COLOR'
    category = 'Surface'

    suffix: bpy.props.StringProperty(default='_G')

    color_space = 'Non-Color'
