import bpy
from .map import EZB_Map_Blender
from .map_metallic import Map_Context_Property_Switcher


class Map_Context_Subsurface_Color(Map_Context_Property_Switcher):
    from_socket = 'Subsurface Color'
    to_socket = 'Emission'


class EZB_Map_Subsurface_Color(bpy.types.PropertyGroup, EZB_Map_Blender):
    id = 'SUBSURFACE_COLOR'
    pass_name = 'EMIT'
    label = 'Subsurface Color'
    icon = 'COLOR'
    category = 'Surface'

    suffix: bpy.props.StringProperty(default='_SS')

    context = Map_Context_Subsurface_Color

    def setup_settings(self):
        super().setup_settings()
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.context.scene.render.bake.use_pass_color = True
