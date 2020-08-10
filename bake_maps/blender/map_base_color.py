import bpy
from .map import EZB_Map_Blender
from .map_metallic import Map_Context_Property_Switcher

class Map_Context_Subsurface_Color(Map_Context_Property_Switcher):
    from_socket = 'Base Color'
    to_socket = 'Emission'

class EZB_Map_Base_Color(bpy.types.PropertyGroup, EZB_Map_Blender):
    id = 'BASE_COLOR'
    pass_name = 'EMIT'
    label = 'Base Color'
    icon='COLOR'
    category = 'Surface'

    suffix: bpy.props.StringProperty(default='_C')

    context = Map_Context_Subsurface_Color

    def setup_settings(self):
        super().setup_settings()
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.context.scene.render.bake.use_pass_color = True
