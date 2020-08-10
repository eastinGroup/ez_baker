import bpy
from .map import EZB_Map_Blender

class EZB_Map_Emit(bpy.types.PropertyGroup, EZB_Map_Blender):
    id = 'EMIT'
    pass_name = 'EMIT'
    label = 'Emission'
    icon='COLOR'
    category = 'Surface'
    suffix: bpy.props.StringProperty(default='_E')
