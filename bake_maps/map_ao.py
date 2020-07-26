import bpy
from .map import EZB_Map

class EZB_Map_AO(bpy.types.PropertyGroup, EZB_Map):
    id = 'AO'
    label = 'Ambient Occlusion'

    suffix: bpy.props.StringProperty(default='_AO')

    samples: bpy.props.IntProperty(name='Samples', default=128)

    background_color = [0.5, 0.5, 0.5, 1.0]

    def _draw_info(self, layout):
        layout.prop(self, 'samples', toggle=True)