import bpy
from .base import EZB_Device
from ..bake_maps import EZB_Maps_Handplane

class EZB_Device_Handplane(bpy.types.PropertyGroup, EZB_Device):
    name = "handplane"
    maps: bpy.props.PointerProperty(type=EZB_Maps_Handplane)

    def draw(self, layout, context):
        pass

    def bake(self, baker):
        print('Not yet supported')
        pass