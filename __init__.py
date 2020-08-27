import bpy
import bpy.utils.previews
import os
from . import addon_updater_ops
from .addon_updater import Updater as updater

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
    "version": (0, 1, 6),
    "category": "3D View",
    "location": "3D View > Tools Panel > EZ Baker",
    "warning": "",
    "wiki_url": "https://gitlab.com/AquaticNightmare/ez_baker",
    "doc_url": "https://gitlab.com/AquaticNightmare/ez_baker",
    "tracker_url": "https://gitlab.com/AquaticNightmare/ez_baker/-/issues",
}


class EZB_preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    auto_check_update: bpy.props.BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=True,
    )
    updater_intrval_months: bpy.props.IntProperty(
        name='Months',
        description="Number of months between checking for updates",
        default=0,
        min=0
    )
    updater_intrval_days: bpy.props.IntProperty(
        name='Days',
        description="Number of days between checking for updates",
        default=7,
        min=0,
        max=31
    )
    updater_intrval_hours: bpy.props.IntProperty(
        name='Hours',
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23
    )
    updater_intrval_minutes: bpy.props.IntProperty(
        name='Minutes',
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
    )

    def set_abs_handplane_path(self, value):
        new_path = os.path.abspath(bpy.path.abspath(value))
        self.abs_handplane_path = new_path

    def get_abs_handplane_path(self):
        return self.abs_handplane_path

    abs_handplane_path: StringProperty(default='C:\\Program Files\\Handplane3D LLC\\Handplane Baker\\')
    handplane_path: bpy.props.StringProperty(subtype='DIR_PATH', set=set_abs_handplane_path, get=get_abs_handplane_path)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'handplane_path')
        addon_updater_ops.update_settings_ui(self, context)


def register():
    from bpy.utils import register_class

    addon_updater_ops.register(bl_info)

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

    addon_updater_ops.unregister()
