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

    def bake(self):
        super().bake()
        with Custom_Render_Settings():
            for map in self.get_bakeable_maps():
                map.do_bake()
        return True


classes = [EZB_Device_Blender]


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
