import bpy
import pathlib
import os
from .base import EZB_Device
from ..bake_maps import EZB_Maps_Blender
from ..contexts import Scene_Visible, Custom_Render_Settings
from ..settings import file_formats_enum

temp_materials = {}


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

    def draw(self, layout, context):
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(self, 'device', text='Render', expand=True)
        row = col.row(align=True)
        row.prop(self, 'tile_size', text='Tile Size', expand=True)

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
            temp_mat = self.create_bake_material(
                current_baker, current_map, mat_slot.material)

            active_node = temp_mat.node_tree.nodes.get(f'__{current_map.id}__')
            temp_mat.node_tree.nodes.active = active_node
            mat_slot.material = temp_mat

    def bake(self, baker):
        super().bake(baker)
        temp_materials.clear()

        with Custom_Render_Settings():
            for map in self.get_bakeable_maps():
                print('SETUP: {}'.format(map.id))
                self.setup_settings(baker)
                map.setup_settings()
                for group in baker.bake_groups:
                    group.setup_settings()
                    high = group.objects_high
                    low = group.objects_low
                    for x in low:
                        with map.context(baker, map, high, x) as tup:
                            map_id, selection_context = tup
                            print('{} :: {} ...'.format(x.name, map.id))
                            bpy.ops.object.bake(selection_context, type=map_id)
                            print('FINISHED BAKE')

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
                    img.image.file_format = file_format
                    path_full = os.path.normpath(os.path.join(bpy.path.abspath(baker.path), img.image.name) + file_formats_enum[file_format])
                    directory = os.path.dirname(path_full)
                    try:
                        pathlib.Path(directory).mkdir(
                            parents=True, exist_ok=True)
                        img.image.filepath = path_full
                        img.image.save_render(
                            path_full, scene=bpy.context.scene)
                        img.image.source = 'FILE'
                        img.image.unpack(method='REMOVE')

                    except OSError:
                        print('The image could not be saved to the path')
                        pass
