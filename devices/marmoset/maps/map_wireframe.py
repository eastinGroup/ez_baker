import bpy
from .map import EZB_Map_Marmoset


class EZB_Map_Wireframe(bpy.types.PropertyGroup, EZB_Map_Marmoset):
    id = 'Wireframe'
    label = 'Wireframe'
    icon = 'GROUP_UVS'
    category = 'IDs & Masks'

    suffix: bpy.props.StringProperty(default='_wireframe')
    active: bpy.props.BoolProperty(default=False)

    def _draw_info(self, layout):
        pass
