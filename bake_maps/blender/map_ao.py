import bpy
from .map import EZB_Map_Blender

class EZB_Map_AO(bpy.types.PropertyGroup, EZB_Map_Blender):
    id = 'AO'
    pass_name = 'AO'
    label = 'Ambient Occlusion'
    icon='SHADING_RENDERED'

    suffix: bpy.props.StringProperty(default='_AO')
    active: bpy.props.BoolProperty(default=True)
    samples: bpy.props.IntProperty(name='Samples', default=128)

    background_color = [0.5, 0.5, 0.5, 1.0]

    def _draw_info(self, layout):
        layout.prop(self, 'samples', toggle=True)