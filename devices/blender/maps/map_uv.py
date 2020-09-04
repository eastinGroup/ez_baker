import bpy
from .map import EZB_Map_Blender


class EZB_Map_UV(bpy.types.PropertyGroup, EZB_Map_Blender):
    id = 'UV'
    pass_name = 'UV'
    label = 'UV'
    icon = 'UV'
    category = 'Mesh'

    suffix: bpy.props.StringProperty(default='_UV')
