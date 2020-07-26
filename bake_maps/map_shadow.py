import bpy
from .map import EZB_Map

class EZB_Map_Shadow(bpy.types.PropertyGroup, EZB_Map):
    id = 'SHADOW'
    label = 'Shadow'

    suffix: bpy.props.StringProperty(default='_SH')

    samples: bpy.props.IntProperty(name='Samples', default=128)

    def _draw_info(self, layout):
        layout.prop(self, 'samples', toggle=True)