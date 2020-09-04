import bpy
import pathlib
import os
import math
import random

from ..device import EZB_Device
from ...contexts import Custom_Render_Settings
from ...settings import file_formats_enum
from ...utilities import log

from . import maps


class EZB_OT_run_blender_background(bpy.types.Operator):
    """Updates UI based on blender progress"""
    bl_idname = "ezb.run_blender_background"
    bl_label = "Updates UI with blender background information"

    _timer = None
    th = None
    prog = 0
    stop_early = False

    export_path: bpy.props.StringProperty()

    def modal(self, context, event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)

            self.stop_early = True
            self.th.join()
            print('MODAL CANCELLED')
            return {'CANCELLED'}

        if event.type == 'TIMER':
            # update progress widget here

            if not self.th.isAlive():
                self.th.join()
                print('MODAL FINISHED')
                return {'FINISHED'}
        return {'PASS_THROUGH'}

    def execute(self, context):
        import threading
        blender_save_file = os.path.join(self.export_path, 'bake.blend')
        print(blender_save_file)
        bpy.ops.wm.save_as_mainfile(filepath=blender_save_file)

        def run_blender_background(self, blender_save_file):
            import subprocess

            path = os.path.join(os.path.split(__file__)[0], 'multithread.py')

            blender_args = [
                bpy.app.binary_path,
                "--background",
                blender_save_file,
                "--python",
                path
            ]

            subprocess.run(blender_args)

        self.th = threading.Thread(target=run_blender_background, args=(self, blender_save_file))
        self.th.start()

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


class EZB_Device_Blender(bpy.types.PropertyGroup, EZB_Device):
    name = "blender"
    maps: bpy.props.PointerProperty(type=maps.EZB_Maps_Blender)

    tile_size: bpy.props.EnumProperty(
        items=[
            ('1/8', '1/8', '1/8'),
            ('1/4', '1/4', '1/4'),
            ('1/2', '1/2', '1/2'),
            ('x1', 'x1', 'x1'),
        ],
        default='x1'
    )

    device: bpy.props.EnumProperty(
        items=[
            ('CPU', 'CPU', 'CPU'),
            ('GPU', 'GPU', 'GPU')
        ]
    )

    def draw(self, layout, context):
        col = layout.column(align=True)

        row = col.row(align=True)
        row.prop(self, 'device', text='Render', expand=True)
        row = col.row(align=True)
        row.prop(self, 'tile_size', text='Tile Size', expand=True)

    # TODO: remove baker from all the function properties, get it with parent_baker property

    def setup_settings(self):
        baker = self.parent_baker

        bake_options = bpy.context.scene.render.bake
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.device = self.device
        bpy.context.scene.cycles.progressive = 'PATH'
        bake_options.use_selected_to_active = not baker.use_low_to_low
        tile_size_relative = 1
        if self.tile_size == '1/8':
            tile_size_relative = 0.125
        if self.tile_size == '1/4':
            tile_size_relative = 0.25
        elif self.tile_size == '1/2':
            tile_size_relative = 0.5
        elif self.tile_size == 'x1':
            tile_size_relative = 1

        supersampling = baker.get_supersampling

        bpy.context.scene.render.tile_x = int(baker.width * tile_size_relative * supersampling)
        bpy.context.scene.render.tile_y = int(baker.height * tile_size_relative * supersampling)

        bake_options.margin = baker.padding * supersampling
        bake_options.use_clear = False

        file_format = 'PNG'
        if baker.image_format == 'TGA':
            file_format = 'TARGA'
        elif baker.image_format == 'TIF':
            file_format = 'TIFF'

        bpy.context.scene.render.image_settings.file_format = file_format
        bpy.context.scene.render.image_settings.color_mode = baker.color_mode
        bpy.context.scene.render.image_settings.color_depth = baker.color_depth
        bpy.context.scene.render.image_settings.compression = 0
        bpy.context.scene.render.image_settings.tiff_codec = 'DEFLATE'

    def bake_local(self):
        super().bake()
        with Custom_Render_Settings():
            for map in self.get_bakeable_maps():
                map.do_bake()
        return True

    def bake_multithread(self):
        bpy.ops.ezb.run_blender_background(export_path=self.parent_baker.get_abs_export_path())
        pass

    def bake(self):
        if self.parent_baker.run_in_background:
            self.bake_multithread()
        else:
            self.bake_local()


classes = [EZB_Device_Blender, EZB_OT_run_blender_background]


def register():
    from bpy.utils import register_class

    maps.register()

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    maps.unregister()

    for cls in reversed(classes):
        unregister_class(cls)
