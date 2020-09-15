import bpy
from .map import EZB_Map_Marmoset


class EZB_Map_Material_ID(bpy.types.PropertyGroup, EZB_Map_Marmoset):
    id = 'Material ID'
    label = 'Material ID'
    icon = 'MATERIAL'
    category = 'IDs & Masks'

    suffix: bpy.props.StringProperty(default='_matid')
    active: bpy.props.BoolProperty(default=False)

    def _draw_info(self, layout):
        pass
