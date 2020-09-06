import bpy
import pathlib
import os
import math
import random
import time
import threading

import multiprocessing
import queue
from multiprocessing.connection import Listener

from ..device import EZB_Device
from ...contexts import Custom_Render_Settings
from ...settings import file_formats_enum
from ...utilities import log

from . import maps

connection = None


class EZB_OT_run_blender_background(bpy.types.Operator):
    """Updates UI based on blender progress"""
    bl_idname = "ezb.run_blender_background"
    bl_label = "Updates UI with blender background information"

    baker_scene: bpy.props.StringProperty()
    baker_datapath: bpy.props.StringProperty()
    device_datapath: bpy.props.StringProperty()

    _timer = None
    th = None
    prog = 0
    stop_early = False

    export_path: bpy.props.StringProperty()

    @property
    def baker(self):
        return bpy.data.scenes[self.baker_scene].path_resolve(self.baker_datapath)

    @property
    def device(self):
        return bpy.data.scenes[self.baker_scene].path_resolve(self.device_datapath)

    def redraw_region(self, context):
        if context and context.area:
            for region in context.area.regions:
                if region.type == "UI":
                    region.tag_redraw()

    def modal(self, context, event):
        if self.baker.cancel_current_bake:
            self.cancel(context)

            self.stop_early = True
            self.process.terminate()
            print('MODAL CANCELLED')
            self.device.bake_cancelled()

            self.redraw_region(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            try:
                msg = self.messages.get_nowait()
                msg_split = msg.split(':::')
                if len(msg_split) == 3:
                    self.device.texture_baked(msg_split[0], msg_split[1], msg_split[2])
                if len(msg_split) == 2 and msg_split[0] == 'WORKING':
                    self.baker.baking_map_name = msg_split[1]
                    self.current_bake += 1
                    self.baker.current_baking_progress = float(self.current_bake) / self.total_bakes

                print(f'received: {msg}')
            except queue.Empty:
                pass
            # update progress widget here
            if self.process.poll() is not None and self.messages.empty():

                print('MODAL FINISHED')
                self.device.bake_finish()
                self.redraw_region(context)
                return {'FINISHED'}

        self.redraw_region(context)

        return {'PASS_THROUGH'}

    def execute(self, context):
        import subprocess

        self.total_bakes = len(list(self.device.get_active_maps()))
        self.current_bake = -1

        orig_export_path = self.baker.path
        blender_save_file = os.path.join(self.baker.get_abs_export_path(), '__temp_bake__.blend')
        self.baker.real_path = self.baker.get_abs_export_path()  # to avoid relative paths or images wont be store where we want them
        bpy.ops.wm.save_as_mainfile(filepath=blender_save_file, copy=True, check_existing=False)
        self.baker.path = orig_export_path

        path = os.path.join(os.path.split(__file__)[0], 'multithread.py')

        blender_args = [
            bpy.app.binary_path,
            "--factory-startup",  # this disables the rest of the addons
            "--addons",
            __package__.split('.')[0],  # this enables just this addon
            "--background",
            blender_save_file,
            "--python",
            path,
        ]

        self.process = subprocess.Popen(blender_args)

        address = ('localhost', 1605)     # family is deduced to be 'AF_INET'
        listener = Listener(address, authkey=bytes('ezbaker', encoding='utf8'))
        connection = listener.accept()
        print(f'connection accepted from {listener.last_accepted}')

        self.messages = queue.Queue()

        def receive_messages(connection, messages):
            print('STARTED RECEIVING MESSAGES')
            while True:
                try:
                    msg = connection.recv()
                    print(msg)
                    messages.put(msg)
                except EOFError:
                    break
                except ConnectionResetError:
                    print('connection reset?')
                    break

        self.server_thread = threading.Thread(target=receive_messages, args=(connection, self.messages))
        self.server_thread.start()

        listener.close()

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

    def update_baking_map(self, map_name):
        if 'is_subprocess' in self.parent_baker and self.parent_baker['is_subprocess']:
            connection.send(f'WORKING:::{map_name}')

    def texture_baked(self, map_id, material_name, image_path):
        if 'is_subprocess' in self.parent_baker and self.parent_baker['is_subprocess']:
            connection.send(f'{map_id}:::{material_name}:::{image_path}')

        map = next(x for x in self.get_all_maps() if x.id == map_id)

        img = self.parent_baker.get_image(map, material_name)
        img.image.source = 'FILE'
        img.image.filepath = image_path
        img.image.reload()

    def bake_local(self):
        global connection

        if 'is_subprocess' in self.parent_baker and self.parent_baker['is_subprocess']:
            from multiprocessing.connection import Client

            address = ('localhost', 1605)
            connection = Client(address, authkey=bytes('ezbaker', encoding='utf8'))

            time.sleep(0.5)
            connection.send('FIRST MESSAGE')

        with Custom_Render_Settings():
            for map in self.get_bakeable_maps():
                map.do_bake()

        connection.send('FINAL MESSAGE')
        self.bake_finish()

    def bake_multithread(self):
        bpy.ops.ezb.run_blender_background(baker_scene=self.parent_baker.id_data.name, baker_datapath=self.parent_baker.path_from_id(), device_datapath=self.path_from_id())
        pass


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
