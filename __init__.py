import bpy
import bpy.utils.previews
import os

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
    "version": (0, 1, 4),
    "category": "3D View",
    "location": "3D View > Tools Panel > EZ Baker",
    "warning": "",
    "wiki_url": "https://gitlab.com/AquaticNightmare/ez_baker",
    "doc_url": "https://gitlab.com/AquaticNightmare/ez_baker",
    "tracker_url": "https://gitlab.com/AquaticNightmare/ez_baker/-/issues",
}
class EZB_preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def set_abs_handplane_path(self, value):
        new_path = os.path.abspath(bpy.path.abspath(value))
        self.abs_handplane_path = new_path
    
    def get_abs_handplane_path(self):
        return self.abs_handplane_path
    
    abs_handplane_path: StringProperty (default='C:\\Program Files\\Handplane3D LLC\\Handplane Baker\\')
    handplane_path: bpy.props.StringProperty(subtype='DIR_PATH', set=set_abs_handplane_path, get=get_abs_handplane_path)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'handplane_path')

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
