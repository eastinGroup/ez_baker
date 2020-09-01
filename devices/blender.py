import bpy
import pathlib
import os
import math
from .base import EZB_Device
from ..bake_maps import EZB_Maps_Blender
from ..contexts import Scene_Visible, Custom_Render_Settings
from ..settings import file_formats_enum
import random
from ..utilities import log

temp_materials = {}

fs_coeffs_orig = [7.0, 3.0, 5.0, 1.0]
fs_coeffs = [7.0, 3.0, 5.0, 1.0]
applied_coeffs = [x / 16 for x in fs_coeffs]


class Dither:
    def __init__(self, pixels, width, height):
        self.orig_pixels = pixels.copy()
        self.pixels = pixels.copy()
        self.width = width
        self.height = height
        self.fs_dither_color()

    def index(self, y, x):
        return self.width * (self.height - y - 1) + x

    def apply_threshold(self, value, value_change):
        return round(value + value_change)

    def fs_dither_color(self):
        for y in range(0, self.height):
            for x in range(0, self.width):

                red_oldpixel, green_oldpixel, blue_oldpixel, alpha_oldpixel = self.pixels[self.index(y, x)]

                value_change = random.uniform(-0.2, 0.2)

                red_newpixel = self.apply_threshold(red_oldpixel, value_change)
                green_newpixel = self.apply_threshold(green_oldpixel, value_change)
                blue_newpixel = self.apply_threshold(blue_oldpixel, value_change)

                red_error = (red_oldpixel - red_newpixel) * 0.8
                blue_error = (blue_oldpixel - blue_newpixel) * 0.8
                green_error = (green_oldpixel - green_newpixel) * 0.8

                if self.height <= 4 and self.width <= 4:
                    log(f'{x},{y}')
                    log(f'{red_oldpixel},{green_oldpixel},{blue_oldpixel} -> {red_newpixel}, {green_newpixel}, {blue_newpixel}')
                    log(f'{self.pixels[self.index(y, x)]}')
                    log(f'ERROR: {red_error}, {blue_error}, {green_error}\n')

                self.pixels[self.index(y, x)] = float(red_newpixel) / 255, float(green_newpixel) / 255, float(blue_newpixel) / 255, float(alpha_oldpixel) / 255

                if x < self.width - 1:
                    red = self.pixels[self.index(y, x + 1)][0] + red_error * applied_coeffs[0]
                    green = self.pixels[self.index(y, x + 1)][1] + green_error * applied_coeffs[0]
                    blue = self.pixels[self.index(y, x + 1)][2] + blue_error * applied_coeffs[0]

                    self.pixels[self.index(y, x + 1)] = (red, green, blue, alpha_oldpixel)

                if x > 0 and y < self.height - 1:
                    red = self.pixels[self.index(y + 1, x - 1)][0] + red_error * applied_coeffs[1]
                    green = self.pixels[self.index(y + 1, x - 1)][1] + green_error * applied_coeffs[1]
                    blue = self.pixels[self.index(y + 1, x - 1)][2] + blue_error * applied_coeffs[1]

                    self.pixels[self.index(y + 1, x - 1)] = (red, green, blue, alpha_oldpixel)

                if y < self.height - 1:
                    red = self.pixels[self.index(y + 1, x)][0] + red_error * applied_coeffs[2]
                    green = self.pixels[self.index(y + 1, x)][1] + green_error * applied_coeffs[2]
                    blue = self.pixels[self.index(y + 1, x)][2] + blue_error * applied_coeffs[2]

                    self.pixels[self.index(y + 1, x)] = (red, green, blue, alpha_oldpixel)

                if x < self.width - 1 and y < self.height - 1:
                    red = self.pixels[self.index(y + 1, x + 1)][0] + red_error * applied_coeffs[3]
                    green = self.pixels[self.index(y + 1, x + 1)][1] + green_error * applied_coeffs[3]
                    blue = self.pixels[self.index(y + 1, x + 1)][2] + blue_error * applied_coeffs[3]

                    self.pixels[self.index(y + 1, x + 1)] = (red, green, blue, alpha_oldpixel)


class EZB_Device_Blender(bpy.types.PropertyGroup, EZB_Device):
    name = "blender"
    maps: bpy.props.PointerProperty(type=EZB_Maps_Blender)

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

    use_dither: bpy.props.BoolProperty(default=False, description='Dithers the resulting image creating a granular pattern that hides artifacts procuded by compressing the image to 8 bits')
    use_custom_truncate: bpy.props.BoolProperty(default=False, description='Instead of rounding the pixel to its nearest value when compressing to 8 bits, it will remove the decimals of it. e.g. 1.7 -> 1 | | 2.2 -> 2')

    def draw(self, layout, context):
        col = layout.column(align=True)

        row = col.row(align=True)
        row.prop(self, 'device', text='Render', expand=True)
        row = col.row(align=True)
        row.prop(self, 'tile_size', text='Tile Size', expand=True)

        if self.parent_baker.color_depth == '8':
            if not self.use_dither:
                row = col.row(align=True)
                row.prop(self, 'use_custom_truncate', text='Custom Truncate (EXPERIMENTAL)', expand=True)

            if not self.use_custom_truncate:
                row = col.row(align=True)
                row.prop(self, 'use_dither', text='Dither (EXPERIMENTAL 100x SLOWER, VERY SLOW)', expand=True)

    # TODO: remove baker from all the function properties, get it with parent_baker property

    def setup_settings(self, baker):
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

        bpy.context.scene.render.tile_x = int(
            baker.width * tile_size_relative * supersampling)
        bpy.context.scene.render.tile_y = int(
            baker.height * tile_size_relative * supersampling)

        bake_options.margin = baker.padding * supersampling
        bake_options.use_clear = False

    def clear_temp_materials(self):
        for orig_mat, temp_mat in temp_materials.items():
            bpy.data.materials.remove(temp_mat, do_unlink=True)

        temp_materials.clear()

    def create_bake_material(self, baker, map, material):
        found_image = baker.get_image(map, material.name)
        temp_material = None
        if material.name not in temp_materials:
            temp_material = material.copy()
            temp_material.name = material.name + '__temp'
            temp_materials[material.name] = temp_material
            temp_material.use_nodes = True
        else:
            temp_material = temp_materials[material.name]

        material_nodes = temp_material.node_tree.nodes
        node = material_nodes.get(f'__{map.id}__')
        if not node:
            node = material_nodes.new("ShaderNodeTexImage")
            node.name = f'__{map.id}__'
            node.image = found_image.image

        return temp_material

    def setup_bake_material(self, object, current_baker, current_map):
        for mat_slot in object.material_slots:
            log(mat_slot)
            temp_mat = self.create_bake_material(current_baker, current_map, mat_slot.material)
            log('temp material set')
            active_node = temp_mat.node_tree.nodes.get(f'__{current_map.id}__')
            temp_mat.node_tree.nodes.active = active_node
            mat_slot.material = temp_mat

    def bake(self, baker):
        super().bake(baker)
        temp_materials.clear()

        with Custom_Render_Settings():
            for map in self.get_bakeable_maps():
                log('SETUP: {}'.format(map.id))
                self.setup_settings(baker)
                map.setup_settings()
                log('Baker Setup Correctly')
                for group in baker.bake_groups:
                    group.setup_settings()
                    high = group.objects_high
                    low = group.objects_low
                    for x in low:
                        log('Setting map context...')
                        with map.context(baker, map, high, x) as tup:
                            log('Context set')
                            map_id, selection_context = tup
                            log('{} :: {} ...'.format(x.name, map.id))
                            bpy.ops.object.bake(selection_context, type=map_id)
                            log('FINISHED BAKE')

            self.clear_temp_materials()
            baker.clear_outputs()

            bpy.context.scene.view_settings.view_transform = 'Standard'

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

            for mat in baker.materials:
                for img in mat.images:
                    img.image.scale(baker.width, baker.height)
                    img.image.pack()

                    if self.parent_baker.color_depth == '8':
                        if self.use_dither:
                            log('DITHERING...')
                            all_pixels = [x * 255 for x in img.image.pixels]

                            all_pixels = [(all_pixels[i], all_pixels[i + 1], all_pixels[i + 2], all_pixels[i + 3]) for i in range(0, len(all_pixels), 4)]

                            dithered_image = Dither(all_pixels, img.image.size[0], img.image.size[1])
                            log('DITHERING FINISHED')
                            pixels = [chan for px in dithered_image.pixels for chan in px]

                            img.image.use_generated_float = False
                            img.image.update()
                            log('Generated float false')
                            img.image.pixels = pixels
                            log('Pixels Set')
                            img.image.pack()
                            log('Updated')

                            log('DITHERING APPLIED')
                        elif self.use_custom_truncate:
                            all_pixels = [x * 255 for x in img.image.pixels]

                            return_pixels = [float(math.floor(x)) / 255 for x in all_pixels]

                            img.image.use_generated_float = False
                            img.image.update()
                            img.image.pixels = return_pixels
                            img.image.pack()

                    img.image.file_format = file_format
                    path_full = os.path.normpath(os.path.join(bpy.path.abspath(baker.path), img.image.name) + file_formats_enum[file_format])
                    directory = os.path.dirname(path_full)

                    try:

                        pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
                        img.image.save_render(path_full, scene=bpy.context.scene)
                        log(f'path: {path_full}')
                        img.image.filepath = path_full
                        log('saved externally')
                        img.image.source = 'FILE'
                        log('source changed')

                        img.image.unpack(method='REMOVE')
                        log('unpacked')
                        img.image.reload()

                    except OSError:
                        print('The image could not be saved to the path')
                        return False

        return True
