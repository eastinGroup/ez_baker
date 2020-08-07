import bpy
from .base import EZB_Device
from ..bake_maps import EZB_Maps_Blender
from ..contexts import Scene_Visible, Custom_Render_Settings

temp_materials = {}
bake_textures = []

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
        row=col.row(align=True)
        row.prop(self, 'device', text='Render', expand=True)
        row=col.row(align=True)
        row.prop(self, 'tile_size', text='Tile Size', expand=True)

    def setup_settings(self, baker):
        bake_options = bpy.context.scene.render.bake
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.device = self.device
        bpy.context.scene.cycles.progressive = 'PATH'
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
    
    def clear_temp_materials(self):
        for orig_mat, temp_mat in temp_materials.items():
            bpy.data.materials.remove(temp_mat, do_unlink=True)

        temp_materials.clear()

    def create_bake_material(self, baker, map, material):
        found_image = baker.get_image(map, material.name)
        temp_material = None
        if material not in temp_materials:
            temp_material = bpy.data.materials.new(material.name + '__temp')
            temp_materials[material] = temp_material
            temp_material.use_nodes = True
        else:
            temp_material = temp_materials[material]
    
        material_nodes = temp_material.node_tree.nodes
        node = material_nodes.get(map.id)
        if not node:
            node = material_nodes.new("ShaderNodeTexImage")
            node.name = map.id
            node.image = found_image.image

        return temp_material
    
    def setup_bake_material(self, object, current_baker, current_map):
        for mat_slot in object.material_slots:
            temp_mat = self.create_bake_material(current_baker, current_map, mat_slot.material)

            active_node = temp_mat.node_tree.nodes.get(current_map.id)
            temp_mat.node_tree.nodes.active = active_node
            mat_slot.material = temp_mat

    def bake(self, baker):
        super().bake(baker)
        temp_materials.clear()
        bake_textures.clear()

        with Scene_Visible():
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
                            with map.context(baker, map, high, x) as map_id:
                                print('{} :: {} ...'.format(x.name, map.id))
                                bpy.ops.object.bake(type=map_id)
                                print('FINISHED BAKE')
                self.clear_temp_materials()
                    
        for x in bake_textures:
            x.scale(baker.width, baker.height)
            x.pack()
                    #save() 3 if filepathh is set
        baker.clear_outputs()