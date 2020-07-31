import subprocess
import pathlib
import os

import bpy

from . import handlers
from . import devices

from .bake_group import EZB_Bake_Group
from .contexts import Scene_Visible, Custom_Render_Settings
from .settings import mode_group_types, file_formats_enum
from .outputs import EZB_Stored_Material

def set_path(self, value):
    # checks if the provided path is inside a subdirectory of the current file to save it as a relative path
    if bpy.data.is_saved:
        value = os.path.realpath(bpy.path.abspath(value))
        file_path = os.path.dirname(os.path.realpath(bpy.path.abspath(bpy.data.filepath)))
        if os.path.commonprefix([os.path.realpath(bpy.path.abspath(value)), file_path]) == file_path:
            value = bpy.path.relpath(value)

    self.real_path = value

def get_path(self):
    return self.real_path

bake_textures = []

class EZB_Baker(bpy.types.PropertyGroup):
    key: bpy.props.StringProperty(default='')

    bake_groups: bpy.props.CollectionProperty(type=EZB_Bake_Group)
    bake_group_index: bpy.props.IntProperty(update=handlers.update_group_objects_on_index_change)

    device_type: bpy.props.EnumProperty(
        items=[
            ('BLENDER', 'Blender', 'Blender', 'BLENDER', 0),
            ('HANDPLANE', 'Handplane', 'Handplane', 'MESH_MONKEY', 1),
        ]
    )
    devices: bpy.props.PointerProperty(type=devices.EZB_Devices)

    real_path: bpy.props.StringProperty(default="")
    path: bpy.props.StringProperty(
        name="Output Path",
        default="",
        description="",
        subtype='DIR_PATH',
        get=get_path,
        set=set_path
    )

    height: bpy.props.IntProperty(default=1024)
    width: bpy.props.IntProperty(default=1024)
    padding: bpy.props.IntProperty(default=16)
    supersampling: bpy.props.EnumProperty(
        items=[
            ('x1', 'x1', 'x1'),
            ('x4', 'x4', 'x4'),
            ('x16', 'x16', 'x16'),
        ],
        default= 'x1'
    )
    image_format: bpy.props.EnumProperty(
       items=[
           ('TARGA', 'TGA', 'Export images as .tga'),
           ('PNG', 'PNG', 'Export images as .png'),
           ('TIFF', 'TIFF', 'Export images as .tiff'),
       ],
       default='PNG',
       name='Format'
    )
    color_mode: bpy.props.EnumProperty(
       items=[
           ('BW', 'BW', 'Black and white'),
           ('RGB', 'RGB', 'Red, green, blue'),
           ('RGBA', 'RGBA', 'Red, green, blue, alpha'),
       ],
       default='RGB',
       name='Mode'
    )
    color_depth: bpy.props.EnumProperty(
       items=[
           ('8', '8', '8'),
           ('16', '16', '16'),
       ],
       default='8',
       name='Depth'
    )

    materials: bpy.props.CollectionProperty(type=EZB_Stored_Material)

    def get_image(self, map, material):
        found_material = None
        found_image = None
        for x in self.materials:
            if x.material == material:
                found_material = x
        if not found_material:
            found_material = self.materials.add()
            found_material.material = material
        
        for image in found_material.images:
            if image.map_name == map.id:
                found_image = image

        if not found_image:
            found_image = found_material.images.add()
            found_image.map_name = map.id
        
        old_image = found_image.image
        if old_image not in bake_textures:
            if old_image:
                old_image.name = '__delete'
            new_name = material.name + map.suffix
            existing_image = bpy.data.images.get(new_name)
            supersampling = self.get_supersampling
            new_image = bpy.data.images.new(new_name, width = self.width*supersampling, height = self.height*supersampling)
            pixels = [map.background_color for i in range(0, self.width*supersampling*self.height*supersampling)]
            pixels = [chan for px in pixels for chan in px]
            new_image.pixels = pixels

            if existing_image:
                existing_image.name = '___TEMP___'
                old_name = new_image.name
                new_image.name = new_name
                existing_image.name = old_name
            # new_image.source = 'GENERATED'
            if old_image:
                old_image.user_remap(new_image)
                bpy.data.images.remove(old_image, do_unlink=True)
            found_image.image = new_image
            bake_textures.append(new_image)

            return found_image
        return found_image


    def get_troublesome_objects(self):
        ans = set()
        for group in self.bake_groups:
            for x in group.objects_low:
                if not x.material_slots:
                    ans.add(x.name)
                    continue
                for slot in x.material_slots:
                    if not slot.material:
                        ans.add(x.name)
                        continue
        return ans


    @property
    def get_supersampling(self):
        supersampling = 1
        if self.supersampling == 'x1':
            supersampling = 1
        elif self.supersampling == 'x4':
            supersampling = 2
        elif self.supersampling == 'x16':
            supersampling = 4
        return supersampling

    @property
    def get_device(self):
        if self.device_type == 'BLENDER':
            return self.devices.blender
        elif self.device_type == 'HANDPLANE':
            return self.devices.handplane
        
    def bake(self):
        bake_textures.clear()
        print('BAKING: {}'.format(self.key))
        self.get_device.bake(self)

    def export(self):
        textures = []
        for x in self.materials:
            for y in x.images:
                if y.image:
                    textures.append(y.image)

        with Custom_Render_Settings():
            bpy.context.scene.view_settings.view_transform = 'Standard'

            bpy.context.scene.render.image_settings.image_format = self.image_format
            bpy.context.scene.render.image_settings.color_mode = self.color_mode
            bpy.context.scene.render.image_settings.color_depth = self.color_depth
            bpy.context.scene.render.image_settings.compression = 0
            bpy.context.scene.render.image_settings.tiff_codec = 'DEFLATE'

            
            for x in textures:
                path_full = os.path.join(bpy.path.abspath(self.path), x.name) + file_formats_enum[orig_file_format]
                directory = os.path.dirname(path_full)
                pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

                x.save_render(path_full, scene=bpy.context.scene)

classes = [
    EZB_Baker
    ]

def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
