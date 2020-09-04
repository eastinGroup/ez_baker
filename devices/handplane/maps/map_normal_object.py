import bpy
from .map import EZB_Map_Handplane


class EZB_Map_Normal(bpy.types.PropertyGroup, EZB_Map_Handplane):
    id = 'NORMAL_OS'
    pass_name = 'normal_os'
    label = 'Normal (Object)'
    icon = 'NORMALS_FACE'

    suffix: bpy.props.StringProperty(default='_ON')
    active: bpy.props.BoolProperty(default=False)

    background_color = [0.5, 0.5, 1.0, 1.0]
