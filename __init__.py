import bpy
import bpy.utils.previews

from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
    PointerProperty,
)

from .settings import mode_group_types

bl_info = {
    "name": "EZ Baker",
    "description": "Bake textures by grouping objects",
    "author": "AquaticNightmare",
    "blender": (2, 83, 0),
    "version": (0, 0, 1),
    "category": "3D View",
    "location": "3D View > Tools Panel > EZ Baker",
    "warning": "",
    "wiki_url": "https://gitlab.com/AquaticNightmare/ez_baker",
    "doc_url": "https://gitlab.com/AquaticNightmare/ez_baker",
    "tracker_url": "https://gitlab.com/AquaticNightmare/ez_baker/-/issues",
}
class EZB_preferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    def draw(self, context):
        layout = self.layout

def register():
    from bpy.utils import register_class

    register_class(EZB_preferences)

    from . import core
    import imp
    # to make sure it uses the correct variables when registering modifiers, otherwise errors will happen during development
    imp.reload(core)
    core.register()

def unregister():
    from bpy.utils import unregister_class

    from . import core
    core.unregister()

    unregister_class(EZB_preferences)
