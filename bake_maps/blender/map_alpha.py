import bpy
from .map import EZB_Map_Blender
from .map_metallic import Map_Context_Property_Switcher


class Map_Context_Alpha(Map_Context_Property_Switcher):
    from_socket = 'Alpha'
    to_socket = 'Emission'
    set_value = 1

    def __init__(self, baker, map, high, low):
        super().__init__(baker, map, high, low)

        self.scene.render.bake.margin = 0


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
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.context.scene.render.bake.use_pass_color = True
