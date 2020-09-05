import subprocess
import pathlib
import os

import bpy

from . import handlers
from . import devices

from .bake_group import EZB_Bake_Group
from .contexts import Custom_Render_Settings
from .settings import mode_group_types, file_formats_enum
from .outputs import EZB_Stored_Material
from .utilities import log

print('baker')


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

    height: bpy.props.IntProperty(default=512)
    width: bpy.props.IntProperty(default=512)
    padding: bpy.props.IntProperty(default=16)
    supersampling: bpy.props.EnumProperty(
        items=[
            ('x1', 'x1', 'x1'),
            ('x4', 'x4', 'x4'),
            ('x16', 'x16', 'x16'),
        ],
        default='x1'
    )
    image_format: bpy.props.EnumProperty(
        items=[
            ('TGA', 'TGA', 'Export images as .tga'),
            ('PNG', 'PNG', 'Export images as .png'),
            ('TIF', 'TIF', 'Export images as .tif'),
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

    run_in_background: bpy.props.BoolProperty(default=True, name='Run in background')

    materials: bpy.props.CollectionProperty(type=EZB_Stored_Material)

    use_low_to_low: bpy.props.BoolProperty(default=False, name='Use Low as High', description='Uses the object with all modifiers applied as the "high" and the same object without modifiers as the "low"')

    is_baking: bpy.props.BoolProperty()
    cancel_current_bake: bpy.props.BoolProperty()
    baking_map_name: bpy.props.StringProperty()
    current_baking_progress: bpy.props.FloatProperty(min=0, max=1)

    def get_abs_export_path(self):
        return os.path.abspath(bpy.path.abspath(self.path))

    def get_image(self, map, material_name):
        found_material = None
        found_image = None
        for x in self.materials:
            if x.material_name == material_name:
                found_material = x
        if not found_material:
            found_material = self.materials.add()
            found_material.material_name = material_name

        for image in found_material.images:
            if image.map_name == map.id:
                found_image = image

        if not found_image:
            found_image = found_material.images.add()
            found_image.map_name = map.id

        new_image = found_image.image
        new_name = material_name + map.suffix
        supersampling = self.get_supersampling

        if not new_image:
            existing_image = bpy.data.images.get(new_name)
            if existing_image:
                new_image = existing_image
            else:
                new_image = bpy.data.images.new(new_name, width=self.width * supersampling, height=self.height * supersampling)
                new_image.colorspace_settings.name = map.color_space

        if new_image not in bake_textures:
            new_image.name = new_name
            new_image.source = 'GENERATED'
            new_image.pack()
            new_image.use_generated_float = True

            new_image.scale(self.width * supersampling, self.height * supersampling)
            pixels = [map.background_color for i in range(0, self.width * supersampling * self.height * supersampling)]
            pixels = [chan for px in pixels for chan in px]
            new_image.pixels = pixels

            # new_image.source = 'GENERATED'
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

    def check_for_errors(self):
        troublesome_objects = self.get_troublesome_objects()
        if troublesome_objects:
            ans = 'Some objects have incorrect or missing materials:\n'
            for x in troublesome_objects:
                ans += x
                ans += '\n'
            return ans
        for group in self.bake_groups:
            if not group.objects_low:
                return 'Some bake groups have no low objects assigned'
        for group in self.bake_groups:
            if not group.objects_high and not self.use_low_to_low:
                return 'Some bake groups have no high objects assigned'
        if not self.bake_groups:
            return 'You need to create a bake group first\nMake sure you have one object (or collection) named "example_low" and another one named "example_high"\nYou will now be able to add the bake group with the dropdown'

        if not self.path:
            return 'No export path set in the Baker Settings panel'

        if self.is_baking:
            return 'Baking is currently in progress'

        for group in self.bake_groups:
            if group.key == '' or ' ' in group.key or ',' in group.key:
                return 'Invalid bake group name {}'.format(group.key)

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
    def child_device(self):
        if self.device_type == 'BLENDER':
            return self.devices.blender
        elif self.device_type == 'HANDPLANE':
            return self.devices.handplane

    def bake(self):
        log('BAKING: {}'.format(self.key))

        os.makedirs(self.get_abs_export_path(), exist_ok=True)

        self.is_baking = True
        self.cancel_current_bake = False
        self.baking_map_name = ''
        self.current_baking_progress = 0.0

        bake_textures.clear()
        self.materials.clear()

        if self.run_in_background:
            self.child_device.bake_multithread()
        else:
            self.child_device.bake_local()

    def bake_cleanup(self):
        self.is_baking = False

    def draw_maps(self, layout, context):
        col = layout.column()

        maps_to_draw = []
        for x in self.child_device.maps.maps:
            map = getattr(self.child_device.maps, x.id)
            if map.active:
                maps_to_draw.append(map)
        #maps_to_draw = sorted(maps_to_draw)
        for x in maps_to_draw:
            box = col.box()
            x.draw(box)


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
