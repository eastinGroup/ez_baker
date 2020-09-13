import bpy
import math
import random
import os
import pathlib
from ...map import EZB_Map
from ....utilities import log
from ....settings import file_formats_enum_blender


postprocess_enum = [
    ('NONE', 'None', ''),
    ('DITHER', 'Dither (x100 SLOWER!)', 'Dither (EXPERIMENTAL 100x SLOWER, VERY SLOW)'),
    ('TRUNCATE', 'Truncate', 'Custom Truncate (EXPERIMENTAL)')
]

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


class Map_Context():
    def __init__(self, map, high, low):
        self.baker = map.parent_baker
        self.map = map
        self.high = high
        self.low = low
        self.scene = bpy.context.scene.copy()
        for obj in self.scene.collection.objects[:]:
            self.scene.collection.objects.unlink(obj)
        for collection in self.scene.collection.children[:]:
            self.scene.collection.children.unlink(collection)
        # self.scene = bpy.data.scenes.new(f'{self.baker.key}_{self.map.id}')

        self.original_materials_low = [x.material for x in low.material_slots]
        self.original_materials_high = {y: [x.material for x in y.material_slots] for y in high}

    def __enter__(self):
        context = bpy.context.copy()
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        context['object'] = self.low
        context['active_object'] = self.low
        all_objs = [self.low] + self.high

        log('gathering objects...')
        all_obj_and_lights = all_objs[:]
        for obj in bpy.context.scene.objects:
            if obj.type == 'LIGHT' and obj.visible_get():
                all_obj_and_lights.append(obj)

        log(all_obj_and_lights)

        for obj in all_obj_and_lights:
            self.scene.collection.objects.link(obj)
        log('LINKED')

        context['selected_objects'] = all_objs
        context['selected_editable_objects'] = all_objs
        context['editable_objects'] = all_obj_and_lights
        context['visible_objects'] = all_obj_and_lights
        context['selectable_objects'] = all_obj_and_lights
        context['view_layer'] = {'objects': all_obj_and_lights}

        log('Setting bake material...')
        self.map.setup_bake_material(self.low)
        log('Material Set')
        cage = bpy.context.scene.objects.get(self.low.name + bpy.context.scene.EZB_Settings.suffix_cage)
        bpy.context.scene.render.bake.cage_object = cage

        context['scene'] = self.scene

        return self.map.pass_name, context

    def __exit__(self, type, value, traceback):
        for i, x in enumerate(self.original_materials_low):
            self.low.material_slots[i].material = x
        for obj, mats in self.original_materials_high.items():
            for i, x in enumerate(mats):
                obj.material_slots[i].material = x

        bpy.data.scenes.remove(self.scene)


class EZB_Created_Image(bpy.types.PropertyGroup):
    material: bpy.props.PointerProperty(type=bpy.types.Material)
    image: bpy.props.PointerProperty(type=bpy.types.Image)


temp_materials = {}


class EZB_Map_Blender(EZB_Map):
    pass_name = 'TEST'

    samples: bpy.props.IntProperty(default=1, min=1)

    context = Map_Context

    created_images: bpy.props.CollectionProperty(type=EZB_Created_Image)

    postprocess: bpy.props.EnumProperty(items=postprocess_enum, default='NONE')

    def setup_settings(self):
        '''Sets up render settings for this map'''
        bpy.context.scene.cycles.bake_type = self.pass_name
        bpy.context.scene.cycles.samples = self.samples

    def get_image(self, material):
        '''Gets the image associated to the bake material from the parent baker'''

        for created_image in self.created_images:
            if created_image.material == material:
                return created_image.image

        ans = self.parent_baker.get_image(self, material.name)
        self.initialize_image(ans.image)
        print(ans.image.source)

        found_material = self.created_images.add()
        found_material.material = material
        found_material.image = ans.image

        return ans.image

    def initialize_image(self, image):
        supersampling = self.parent_baker.get_supersampling

        image.source = 'GENERATED'
        image.pack()
        image.use_generated_float = True
        image.scale(self.parent_baker.width * supersampling, self.parent_baker.height * supersampling)

        pixels = [self.background_color for i in range(0, self.parent_baker.width * supersampling * self.parent_baker.height * supersampling)]
        pixels = [chan for px in pixels for chan in px]
        image.pixels = pixels

    def create_bake_material(self, material):
        '''Creates a copy of the original "low" material with an image node to bake to'''
        temp_material = None
        if material.name not in temp_materials:
            temp_material = material.copy()
            temp_material.name = material.name + '__temp'
            temp_materials[material.name] = temp_material
            temp_material.use_nodes = True
        else:
            temp_material = temp_materials[material.name]

        material_nodes = temp_material.node_tree.nodes
        node = material_nodes.get(f'__{self.id}__')
        if not node:
            node = material_nodes.new("ShaderNodeTexImage")
            node.name = f'__{self.id}__'
            node.image = self.get_image(material)

        temp_material.node_tree.nodes.active = node

        return temp_material

    def setup_bake_material(self, object):
        '''Applies a duplicated material ready for baking to the object'''
        for mat_slot in object.material_slots:
            mat_slot.material = self.create_bake_material(mat_slot.material)

    @property
    def file_format(self):
        file_format = 'PNG'
        if self.parent_baker.image_format == 'TGA':
            file_format = 'TARGA'
        elif self.parent_baker.image_format == 'TIF':
            file_format = 'TIFF'
        return file_format

    def get_export_path(self, image_name):
        return os.path.normpath(os.path.join(bpy.path.abspath(self.parent_baker.path), image_name) + file_formats_enum_blender[self.file_format])

    def postprocess_images(self):
        bpy.context.scene.view_settings.view_transform = 'Standard'

        for created_image in self.created_images:
            image = created_image.image
            image.scale(self.parent_baker.width, self.parent_baker.height)
            image.pack()

            if self.parent_baker.color_depth == '8':
                if self.postprocess == 'DITHER':
                    log('DITHERING...')
                    all_pixels = [x * 255 for x in image.pixels]

                    all_pixels = [(all_pixels[i], all_pixels[i + 1], all_pixels[i + 2], all_pixels[i + 3]) for i in range(0, len(all_pixels), 4)]

                    dithered_image = Dither(all_pixels, image.size[0], image.size[1])
                    log('DITHERING FINISHED')
                    pixels = [chan for px in dithered_image.pixels for chan in px]

                    image.use_generated_float = False
                    image.update()
                    log('Generated float false')
                    image.pixels = pixels
                    log('Pixels Set')
                    image.pack()
                    log('Updated')

                    log('DITHERING APPLIED')

                elif self.postprocess == 'TRUNCATE':
                    all_pixels = [x * 255 for x in image.pixels]

                    return_pixels = [float(math.floor(x)) / 255 for x in all_pixels]

                    image.use_generated_float = False
                    image.update()
                    image.pixels = return_pixels
                    image.pack()

            image.file_format = self.file_format
            path_full = self.get_export_path(image.name)
            directory = os.path.dirname(path_full)

            try:
                pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
                image.save_render(path_full, scene=bpy.context.scene)
                log(f'path: {path_full}')
                image.filepath = path_full
                log('saved externally')
                image.source = 'FILE'
                log('source changed')

                image.unpack(method='REMOVE')
                log('unpacked')
                image.reload()

            except OSError:
                print('The image could not be saved to the path')
                return False

            self.parent_device.texture_baked(self.id, created_image.material.name, image.filepath)

    def pre_bake(self):
        self.parent_device.update_baking_map(self.id)
        temp_materials.clear()
        self.created_images.clear()

    def do_bake(self):
        '''Starts the bake process'''
        self.pre_bake()

        self.parent_device.setup_settings()
        self.setup_settings()

        for group in self.parent_baker.bake_groups:
            group.setup_settings()

            high = group.objects_high
            low = group.objects_low

            for x in low:
                self.bake_start(high, x)

        self.postprocess_images()

        for temp_mat in temp_materials.values():
            bpy.data.materials.remove(temp_mat, do_unlink=True)

        temp_materials.clear()

    def bake_start(self, high, low):
        '''Bakes high objects to low'''
        with self.context(self, high, low) as tup:
            map_id, selection_context = tup
            log('{} :: {} ...'.format(low.name, self.id))
            bpy.ops.object.bake(selection_context, type=map_id)
            log('FINISHED BAKE')

        # each map should override this with more settings to setup
