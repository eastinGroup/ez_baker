import subprocess
import pathlib
import os

import bpy

from . import handlers
from . import bake_maps
from . import bake_settings

from .bake_group import EZB_Bake_Group
from .bake_maps import EZB_Maps
from .contexts import Scene_Visible, Custom_Render_Settings, Bake_Setup
from .settings import mode_group_types, file_formats_enum


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


class EZB_Stored_Image(bpy.types.PropertyGroup):
    map_name: bpy.props.StringProperty()
    image: bpy.props.PointerProperty(type=bpy.types.Image)

class EZB_Stored_Material(bpy.types.PropertyGroup):
    # stored the original material
    material: bpy.props.PointerProperty(type=bpy.types.Material)
    temp_material: bpy.props.PointerProperty(type=bpy.types.Material)

    images: bpy.props.CollectionProperty(type=EZB_Stored_Image)

    show_info:bpy.props.BoolProperty(default=True)

    def draw(self, layout, context):
        box = layout.box()
        row = box.row(align=True)
        row.prop(
            self,
            'show_info',
            icon="TRIA_DOWN" if self.show_info else "TRIA_RIGHT",
            icon_only=True,
            text='',
            emboss=False
        )
        row.label(text="{}".format(self.material.name), icon='MATERIAL')
        if self.show_info:
            row = box.row()
            row.separator()
            col = row.column()
            for x in self.images:
                row = col.row()
                row.label(text='{}:'.format(x.map_name))
                row.operator('ezb.show_image', text='{}'.format(x.image.name), icon='FILE_IMAGE').image = x.image.name

class EZB_Baker(bpy.types.PropertyGroup):
    key: bpy.props.StringProperty(default='')

    mode_group: bpy.props.EnumProperty(items=mode_group_types, name="Group By", default='NAME')

    bake_groups: bpy.props.CollectionProperty(type=EZB_Bake_Group)
    bake_group_index: bpy.props.IntProperty(update=handlers.update_group_objects_on_index_change)

    maps: bpy.props.PointerProperty(type=EZB_Maps)

    real_path: bpy.props.StringProperty(default="")
    path: bpy.props.StringProperty(
        name="Output Path",
        default="",
        description="",
        subtype='DIR_PATH',
        get=get_path,
        set=set_path
    )

    materials: bpy.props.CollectionProperty(type=EZB_Stored_Material)

    settings:bpy.props.PointerProperty(type=bake_settings.bake_settings)

    height: bpy.props.IntProperty(default=1024)
    width: bpy.props.IntProperty(default=1024)

    padding: bpy.props.IntProperty(default=16)

    def draw(self, layout, context):
        ezb_settings = bpy.context.scene.EZB_Settings

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator_menu_enum('ezb.select_texture_size', 'size', text='', icon='DOWNARROW_HLT')
        row.prop(self, 'width', text='width')
        row.prop(self, 'height', text='height')
        row = col.row(align=True)
        row.prop(self, 'padding', text='padding')
        
        row = layout.row(align=True)
        if self.path == "":
            row.alert = True
        row.prop(self, "path", text="")
        if self.path != "":
            row = row.row(align=True)
            row.operator("wm.path_open", text="", icon='FILE_TICK').filepath = self.path

        row=layout.split(factor=0.75, align=True)
        row.operator('ezb.bake', text = 'Bake', icon='IMPORT')
        row.operator('ezb.export', text = 'Export', icon='EXPORT')
        

    def get_active_maps(self):
        ans = []
        for bake_map in bake_maps.maps:
            map = getattr(self.maps, bake_map.id)
            if map.active:
                ans.append(map)

        return ans

    

    def create_bake_material(self, material):
        temp_material = None
        found_material = None
        was_created = False
        for x in self.materials:
            if x.material == material:
                found_material = x
                if x.temp_material:
                    temp_material = x.temp_material
        if not found_material:
            found_material = self.materials.add()
            found_material.material = material

        if not temp_material:
            temp_material = bpy.data.materials.new(material.name + '__temp')

            found_material.temp_material = temp_material
            temp_material.use_nodes = True
            

        for bake_map in bake_maps.maps:
            map = getattr(self.maps, bake_map.id)
            found_image = None
            for image in found_material.images:
                if image.map_name == map.id:
                    found_image = image

            if map.active:
                if not found_image:
                    found_image = found_material.images.add()
                    found_image.map_name = map.id
                
                old_image = found_image.image
                if old_image not in bake_textures:
                    if old_image:
                        old_image.name = '__delete'
                    new_name = material.name + map.suffix
                    existing_image = bpy.data.images.get(new_name)

                    new_image = bpy.data.images.new(new_name, width = self.width, height = self.height)
                    pixels = [map.background_color for i in range(0, self.width*self.height)]
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
                    was_created = True

                material_nodes = temp_material.node_tree.nodes
                node = material_nodes.get(map.id)
                if not node:
                    node = material_nodes.new("ShaderNodeTexImage")
                    node.name = map.id
                    node.image = found_image.image
                    #temp_material.node_tree.links.new(texture.outputs[0], material_nodes['Principled BSDF'].inputs[map.material_slot])
            
            # if there was a stored image for a map that is inactive, remove it from the output
            if not map.active and found_image:
                for i in reversed(range(0, len(found_material.images))):
                    if found_material.images[i] == found_image:
                        found_material.images.remove(i)
        return temp_material
    
    def clear_temp_materials(self):
        for i in reversed(range(0, len(self.materials))):
            x = self.materials[i]
            if x.temp_material:
                bpy.data.materials.remove(x.temp_material, do_unlink=True)
            # if a material was not found during the bake, remove it from the results
            else:
               self.materials.remove(i)

    def setup_bake_material(self, object, current_map):
        for mat_slot in object.material_slots:
            temp_mat = self.create_bake_material(mat_slot.material)

            active_node = temp_mat.node_tree.nodes.get(current_map.id)
            temp_mat.node_tree.nodes.active = active_node
            mat_slot.material = temp_mat

    def restore_original_materials(self, object):
        for mat_slot in object.material_slots:
            for x in self.materials:
                if x.temp_material == mat_slot.material:
                    mat_slot.material = x.material

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


    def setup_settings(self):
        bake_options = bpy.context.scene.render.bake
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.progressive = 'PATH'
        bake_options.use_selected_to_active = True
        #bpy.context.scene.cycles.use_adaptive_sampling = False
        #bpy.context.scene.cycles.sampling_pattern = 'SOBOL'

        bake_options.margin = self.padding
        bake_options.use_clear = False

    def bake(self):
        #args = [bpy.app.binary_path, "-b",]
        #subprocess.call(args)
        print('BAKING: {}'.format(self.key))
        bake_textures.clear()

        with Scene_Visible():
            with Custom_Render_Settings():
                for map in self.get_active_maps():
                    self.setup_settings()
                    map.setup_settings()
                    for group in self.bake_groups:
                        group.setup_settings()
                        high = group.objects_high
                        low = group.objects_low
                        for x in low:
                            with Bake_Setup(self, map, high, x) as map_id:
                                print('{} :: {}'.format(x.name, map_id))
                                bpy.ops.object.bake(type=map_id)

                    for x in bake_textures:
                        x.pack()
                        #save() 3 if filepathh is set
                    self.clear_temp_materials()

    def export(self):
        textures = []
        for x in self.materials:
            for y in x.images:
                if y.image:
                    textures.append(y.image)

        with Custom_Render_Settings():
            bpy.context.scene.view_settings.view_transform = 'Standard'
            
            for x in textures:
                path_full = os.path.join(bpy.path.abspath(self.path), x.name) + file_formats_enum[orig_file_format]
                directory = os.path.dirname(path_full)
                pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

                x.save_render(path_full, scene=bpy.context.scene)

classes = [
    EZB_Stored_Image, 
    EZB_Stored_Material, 
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
