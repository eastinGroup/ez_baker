import bpy
from .map import EZB_Map_Blender, Map_Context
from ....utilities import log


class Map_Context_ID(Map_Context):
    def __init__(self, map, high, low):
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')

        self.colors = [
            (1, 0, 0, 1),
            (0, 1, 0, 1),
            (0, 0, 1, 1),

            (1, 1, 0, 1),
            (0, 1, 1, 1),
            (1, 0, 1, 1),

            (0.3, 1, 0, 1),
            (0, 0.3, 1, 1),
            (1, 0, 0.3, 1),
            (1, 0.3, 0, 1),
            (0, 1, 0.3, 1),
            (0.3, 0, 1, 1),

            (0.5, 0.5, 0, 1),
            (0, 0.5, 0.5, 1),
            (0.5, 0, 0.5, 1),

            (1, 0.5, 0.5, 1),
            (0.5, 1, 0.5, 1),
            (0.5, 0.5, 1, 1),

            (0.4, 0.8, 0, 1),
            (0, 0.4, 0.8, 1),
            (0.8, 0, 0.4, 1),
            (0.8, 0.4, 0, 1),
            (0, 0.8, 0.4, 1),
            (0.4, 0, 0.8, 1),
        ]

        self.mat_index = 0

        self.dup_objects = [x.copy() for x in high]
        self.dup_meshes = [x.data.copy() for x in self.dup_objects]

        self.materials = {}
        for i, obj in enumerate(self.dup_objects):
            obj.data = self.dup_meshes[i]
            for mat_slot in obj.material_slots:
                log(mat_slot)
                if mat_slot.material not in self.materials:
                    self.materials[mat_slot.material] = self.create_mat()
                mat_slot.material = self.materials[mat_slot.material]

        super().__init__(map, self.dup_objects, low)

    def create_mat(self):
        log('newmat')
        id_mat = bpy.data.materials.new('BAKETHICKNESS')
        id_mat.use_nodes = True
        color_node = id_mat.node_tree.nodes.new('ShaderNodeRGB')
        color_node.outputs[0].default_value = self.colors[self.mat_index % len(self.colors)]

        output = id_mat.node_tree.nodes['Material Output']
        id_mat.node_tree.links.new(color_node.outputs['Color'], output.inputs['Surface'])
        self.mat_index += 1
        return id_mat

    def __exit__(self, type, value, traceback):
        super().__exit__(type, value, traceback)

        for x in self.dup_objects:
            bpy.data.objects.remove(x, do_unlink=True)
        for x in self.dup_meshes:
            bpy.data.meshes.remove(x, do_unlink=True)

        for mat, id_mat in self.materials.items():
            bpy.data.materials.remove(id_mat, do_unlink=True)


class EZB_Map_ID(bpy.types.PropertyGroup, EZB_Map_Blender):
    id = 'ID'
    pass_name = 'EMIT'
    label = 'Material ID'
    icon = 'RNA'
    category = 'Mesh'

    suffix: bpy.props.StringProperty(default='_ID')
    active: bpy.props.BoolProperty(default=True)
    bake: bpy.props.BoolProperty(default=False)

    background_color = [0.0, 0.0, 0.0, 1.0]

    context = Map_Context_ID

    def _draw_info(self, layout):
        pass
