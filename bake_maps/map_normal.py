import bpy
from .map import EZB_Map

class EZB_Map_Normal(bpy.types.PropertyGroup, EZB_Map):
    id = 'NORMAL'
    label = 'Normal'

    active: bpy.props.BoolProperty(default=True)

    copy_settings = ['normal_space', 'normal_r', 'normal_g', 'normal_b']

    suffix: bpy.props.StringProperty(default='_N')

    def _draw_info(self, layout):
        

        layout.prop(self.settings, "normal_space", text="Space")

        sub = layout.column(align=True)
        sub.prop(self.settings, "normal_r", text="Swizzle R")
        sub.prop(self.settings, "normal_g", text="G")
        sub.prop(self.settings, "normal_b", text="B")