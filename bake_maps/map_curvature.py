import bpy
from .map import EZB_Map, Map_Context

class Map_Context_Curvature(Map_Context):
    def __init__(self, baker, map, high, low):
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')

        self.curv_mat = bpy.data.materials.new('BAKECURV')
        self.curv_mat.use_nodes = True
        node = self.curv_mat.node_tree.nodes.new('ShaderNodeNewGeometry')
        ramp_node = self.curv_mat.node_tree.nodes.new('ShaderNodeValToRGB')
        ramp_node.color_ramp.elements[0].position = 0.45
        ramp_node.color_ramp.elements[1].position = 0.55

        bsdf = self.curv_mat.node_tree.nodes['Material Output']
        self.curv_mat.node_tree.links.new(node.outputs['Pointiness'], ramp_node.inputs['Fac'])
        self.curv_mat.node_tree.links.new(ramp_node.outputs['Color'], bsdf.inputs['Surface'])

        self.dup_objects = [x.copy() for x in high]
        self.dup_meshes = [x.data.copy() for x in self.dup_objects]

        for i, mesh in enumerate(self.dup_meshes):
            bpy.context.scene.collection.objects.link(self.dup_objects[i])
            self.dup_objects[i].data = mesh

            bpy.context.view_layer.objects.active = self.dup_objects[i]
            #bpy.ops.object.mode_set(mode='EDIT', toggle=False)

            #bpy.ops.mesh.select_all(action='SELECT')
            #bpy.ops.mesh.flip_normals()

            #bpy.ops.object.mode_set(mode='OBJECT', toggle=False)


            for j in reversed(range(0, len(self.dup_objects[i].material_slots))):
                self.dup_objects[i].active_material_index = j
                bpy.ops.object.material_slot_remove()

            bpy.ops.object.material_slot_add()

            self.dup_objects[i].material_slots[0].material = self.curv_mat


        super().__init__(baker, map, self.dup_objects, low)

    def __enter__(self):
        return super().__enter__()

    def __exit__(self, type, value, traceback):
        for x in self.dup_objects:
            bpy.data.objects.remove(x, do_unlink=True)
        for x in self.dup_meshes:
            bpy.data.meshes.remove(x, do_unlink=True)

        bpy.data.materials.remove(self.curv_mat, do_unlink=True)

        super().__exit__(type, value, traceback)


class EZB_Map_AO(bpy.types.PropertyGroup, EZB_Map):
    id = 'CURVATURE'
    pass_name = 'EMIT'
    label = 'Curvature'
    icon='SPHERECURVE'

    suffix: bpy.props.StringProperty(default='_CURV')
    active: bpy.props.BoolProperty(default=True)

    background_color = [0.5, 0.5, 0.5, 1.0]

    context = Map_Context_Curvature

    def _draw_info(self, layout):
        #TODO: add contrat prop
        pass