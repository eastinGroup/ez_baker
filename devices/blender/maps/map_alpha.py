import bpy
from .map import EZB_Map_Blender
from .map_metallic import Map_Context_Property_Switcher


class Map_Context_Alpha(Map_Context_Property_Switcher):
    from_socket = 'Alpha'
    to_socket = 'Emission'
    set_value = 1

    def __init__(self, map, high, low):
        super().__init__(map, high, low)
        self.orig_margin = self.scene.render.bake.margin
        self.scene.render.bake.margin = 0

    def __exit__(self, type, value, traceback):
        self.scene.render.bake.margin = self.orig_margin
        super().__exit__(type, value, traceback)


class EZB_Map_Alpha(bpy.types.PropertyGroup, EZB_Map_Blender):
    id = 'ALPHA'
    pass_name = 'EMIT'
    label = 'Alpha'
    icon = 'COLOR'
    category = 'Surface'

    suffix: bpy.props.StringProperty(default='_A')

    context = Map_Context_Alpha

    def setup_settings(self):
        super().setup_settings()
        scene = self.id_data
        scene.render.bake.use_pass_direct = False
        scene.render.bake.use_pass_indirect = False
        scene.render.bake.use_pass_color = True
