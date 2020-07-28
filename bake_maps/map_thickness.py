import bpy
from .map import EZB_Map, Map_Context

class Map_Context_Thickness(Map_Context):
    def __init__(self, baker, map, high, low):
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')

        self.thickness_mat = bpy.data.materials.new('BAKETHICKNESS')
        self.thickness_mat.use_nodes = True
        ao_node = self.thickness_mat.node_tree.nodes.new('ShaderNodeAmbientOcclusion')
        ao_node.inside = True
        ao_node.only_local = True
        ao_node.samples = map.samples

        bsdf = self.thickness_mat.node_tree.nodes['Material Output']
        self.thickness_mat.node_tree.links.new(ao_node.outputs['AO'], bsdf.inputs['Surface'])

        self.dup_objects = [x.copy() for x in high]
        self.dup_meshes = [x.data.copy() for x in self.dup_objects]

        for i, mesh in enumerate(self.dup_meshes):
            bpy.context.scene.collection.objects.link(self.dup_objects[i])
            self.dup_objects[i].data = mesh

            bpy.context.view_layer.objects.active = self.dup_objects[i]
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.flip_normals()

            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)


            for i in reversed(range(0, len(self.dup_objects[i].material_slots))):
                self.dup_objects[i].active_material_index = i
                bpy.ops.object.material_slot_remove()

            bpy.ops.object.material_slot_add()

            self.dup_objects[i].material_slots[0].material = self.thickness_mat


        super().__init__(baker, map, self.dup_objects, low)

    def __enter__(self):
        return super().__enter__()

    def __exit__(self, type, value, traceback):
        for x in self.dup_objects:
            bpy.data.objects.remove(x, do_unlink=True)
        for x in self.dup_meshes:
            bpy.data.meshes.remove(x, do_unlink=True)

        bpy.data.materials.remove(self.thickness_mat, do_unlink=True)

        super().__exit__(type, value, traceback)


class EZB_Map_AO(bpy.types.PropertyGroup, EZB_Map):
    id = 'THICKNESS'
    pass_name = 'EMIT'
    label = 'Thickness'

    suffix: bpy.props.StringProperty(default='_THCK')

    samples: bpy.props.IntProperty(name='Samples', default=8)

    background_color = [0.5, 0.5, 0.5, 1.0]

    context = Map_Context_Thickness

    def _draw_info(self, layout):
        layout.prop(self, 'samples', toggle=True)