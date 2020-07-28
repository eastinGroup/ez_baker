import bpy
from .map import EZB_Map, Map_Context

class Map_Context_Normal(Map_Context):
    def __init__(self, baker, map, high, low):
        super().__init__(baker, map, high, low)

    def __enter__(self):
        if self.map.triangulate_low:
            self.mod = self.low.modifiers.new('TRIANGULATE', 'TRIANGULATE')
            self.mod.keep_custom_normals = True
        
        return super().__enter__()

    def __exit__(self, type, value, traceback):
        if self.map.triangulate_low:
            self.low.modifiers.remove(self.mod)
        super().__exit__(type, value, traceback)

class EZB_Map_Normal(bpy.types.PropertyGroup, EZB_Map):
    id = 'NORMAL'
    pass_name = 'NORMAL'
    label = 'Normal'

    suffix: bpy.props.StringProperty(default='_N')
    active: bpy.props.BoolProperty(default=True)
    triangulate_low: bpy.props.BoolProperty(default=True)

    copy_settings = ['normal_space', 'normal_r', 'normal_g', 'normal_b']
    background_color = [0.5, 0.5, 1.0, 1.0]

    context = Map_Context_Normal

    def _draw_info(self, layout):
        layout.prop(self.settings, "normal_space", text="Space")
        layout.prop(self, 'triangulate_low', text='Triangulate')
        sub = layout.column(align=True)
        sub.prop(self.settings, "normal_r", text="Swizzle R")
        sub.prop(self.settings, "normal_g", text="G")
        sub.prop(self.settings, "normal_b", text="B")
        