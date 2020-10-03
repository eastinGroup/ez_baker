from .settings import mode_group_types
from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
    PointerProperty,
)

import bpy
import os
from .addon_updater import ops as updater_ops

bl_info = {
    "name": "EZ Baker",
    "description": "Bake textures by grouping objects",
    "author": "AquaticNightmare",
    "blender": (2, 83, 0),
    "version": (1, 0, 1),
    "category": "3D View",
    "location": "3D View > Tools Panel > EZ Baker",
    "warning": "",
    "wiki_url": "https://gitlab.com/AquaticNightmare/ez_baker",
    "doc_url": "https://gitlab.com/AquaticNightmare/ez_baker",
    "tracker_url": "https://gitlab.com/AquaticNightmare/ez_baker/-/issues",
}

module_dependencies_installed = True
try:
    import PIL
except ModuleNotFoundError:
    module_dependencies_installed = False


class EZB_OT_install_dependencies(bpy.types.Operator):
    """Installs python package dependencies"""
    bl_idname = "ezb.install_dependencies"
    bl_label = "Install Dependencies"

    def execute(self, context):
        import subprocess
        import ensurepip
        ensurepip.bootstrap()

        command = [bpy.app.binary_path_python, "-m", "pip", "install", f'--target="{os.path.join(bpy.utils.user_resource("SCRIPTS", "addons"), "modules")}"', 'Pillow']
        windows_command = [f'"{bpy.app.binary_path_python}"', "-m", "pip", "install", f'--target="{os.path.join(bpy.utils.user_resource("SCRIPTS", "addons"), "modules")}"', 'Pillow']

        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        if p.returncode != 0:
            print(stderr)
            command_line = " ".join(windows_command)
            error_msg = f'An error occurred trying to install the required library\nA command has been copied to your clipboard\nTry running it in your OS command line\nThen restart blender'
            context.window_manager.clipboard = command_line
            self.report({'ERROR'}, error_msg)

            return {'CANCELLED'}
        # bpy.ops.preferences.addon_disable(module=__name__)
        # bpy.ops.preferences.addon_enable(module=__name__)

        self.report({'ERROR'}, 'Restart Blender for the changes to take effect')

        return {'FINISHED'}


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

    run_in_background: bpy.props.BoolProperty(default=True, name='Run Bakes in background', description='If active, blender will be responsive while the images are being generated')

    def set_abs_handplane_path(self, value):
        new_path = os.path.abspath(bpy.path.abspath(value))
        self.abs_handplane_path = new_path

    def get_abs_handplane_path(self):
        return self.abs_handplane_path

    abs_handplane_path: StringProperty(default='C:\\Program Files\\Handplane3D LLC\\Handplane Baker\\')
    handplane_path: bpy.props.StringProperty(
        subtype='DIR_PATH',
        name='Handplane Path',
        set=set_abs_handplane_path,
        get=get_abs_handplane_path,
    )

    def set_abs_marmoset_path(self, value):
        new_path = os.path.abspath(bpy.path.abspath(value))
        self.abs_marmoset_path = new_path

    def get_abs_marmoset_path(self):
        return self.abs_marmoset_path

    abs_marmoset_path: StringProperty(default='C:\\Program Files\\Marmoset\\Toolbag 3\\')
    marmoset_path: bpy.props.StringProperty(
        subtype='DIR_PATH',
        name='Marmoset Toolbag Path',
        set=set_abs_marmoset_path,
        get=get_abs_marmoset_path,
    )

    use_steam_toolbag: BoolProperty(
        default=False,
        name='Use Marmoset Steam version'
    )

    def get_full_marmoset_path(self):
        exe_name = 'toolbag.exe' if not self.use_steam_toolbag else 'toolbag_steam.exe'
        return os.path.join(self.marmoset_path, exe_name)

    def draw(self, context):
        layout = self.layout

        if not module_dependencies_installed:
            layout.label(text='This addon requires to have the Pillow library installed for the Uvlayout map to be available')
            layout.label(text='This is completely optional and does not affect any other aspect of the addon')
            layout.label(text='You can install this library with the button below')
            row = layout.row()
            row.scale_y = 2
            row.operator('ezb.install_dependencies')
        layout.prop(self, 'run_in_background')

        row = layout.row()
        row.alert = not(self.handplane_path and os.path.isfile(os.path.join(self.handplane_path, 'handplaneCmd.exe')))
        row.prop(self, 'handplane_path')

        row = layout.row()
        row.alert = not(self.marmoset_path and os.path.isfile(self.get_full_marmoset_path()))
        row.prop(self, 'marmoset_path')
        layout.prop(self, 'use_steam_toolbag')
        #layout.prop(self, 'marmoset_path')
        updater_ops.update_settings_ui(self, context)


classes = [EZB_OT_install_dependencies, EZB_preferences]


def register():
    from bpy.utils import register_class

    updater_ops.register(bl_info)

    for cls in classes:
        register_class(cls)

    from . import core
    import imp
    # to make sure it uses the correct variables when registering modifiers, otherwise errors will happen during development
    imp.reload(core)
    core.register()


def unregister():
    from bpy.utils import unregister_class

    from . import core
    core.unregister()

    for cls in reversed(classes):
        unregister_class(cls)

    updater_ops.unregister()
