import bpy
from .map import EZB_Map_Marmoset


class EZB_Map_Object_ID(bpy.types.PropertyGroup, EZB_Map_Marmoset):
    id = 'Object ID'
    label = 'Object ID'
    icon = 'OBJECT_DATAMODE'
    category = 'IDs & Masks'

    suffix: bpy.props.StringProperty(default='_objid')
    active: bpy.props.BoolProperty(default=False)

    def _draw_info(self, layout):
        pass
