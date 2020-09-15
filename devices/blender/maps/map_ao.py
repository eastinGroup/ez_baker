import bpy
from .map import EZB_Map_Blender


class EZB_Map_AO(bpy.types.PropertyGroup, EZB_Map_Blender):
    id = 'AO'
    pass_name = 'AO'
    label = 'Ambient Occlusion'
    icon = 'SHADING_RENDERED'
    category = 'Lighting'

    suffix: bpy.props.StringProperty(default='_AO')
    samples: bpy.props.IntProperty(name='Samples', default=128)

    active: bpy.props.BoolProperty(default=True)
    bake: bpy.props.BoolProperty(default=False)

    background_color = [0.5, 0.5, 0.5, 1.0]

    def _draw_info(self, layout):
        layout.prop(self, 'samples', toggle=True)
