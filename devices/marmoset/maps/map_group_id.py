import bpy
from .map import EZB_Map_Marmoset


class EZB_Map_Group_ID(bpy.types.PropertyGroup, EZB_Map_Marmoset):
    id = 'Group ID'
    label = 'Group ID'
    icon = 'RNA'
    category = 'IDs & Masks'

    suffix: bpy.props.StringProperty(default='_grpid')
    active: bpy.props.BoolProperty(default=False)

    def _draw_info(self, layout):
        pass
