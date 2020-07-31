import bpy
from .map import EZB_Map_Blender

class EZB_Map_Shadow(bpy.types.PropertyGroup, EZB_Map_Blender):
    id = 'SHADOW'
    pass_name = 'SHADOW'
    label = 'Shadow'
    icon = 'OUTLINER_OB_LIGHT'

    suffix: bpy.props.StringProperty(default='_SH')

    samples: bpy.props.IntProperty(name='Samples', default=128)

    def _draw_info(self, layout):
        layout.prop(self, 'samples', toggle=True)