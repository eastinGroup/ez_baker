import bpy
from .map import EZB_Map_Blender, Map_Context


class Map_Context_Custom_Material(Map_Context):

    def create_mat(self):
        pass

    def __init__(self, map, high, low):
        super().__init__(map, high, low)

        if not self.device.use_low_to_low:
            self.mat = self.create_mat()

            objects = self.high

            for obj in objects:
                for mat_slot in obj.material_slots:
                    mat_slot.material = self.mat
        else:
            self.materials_map = {}

            for mat_slot in self.low.material_slots:
                if mat_slot.material in self.materials_map:
                    mat_slot.material = self.materials_map[mat_slot.material]
                else:
                    orig_name = mat_slot.material.name
                    mat_slot.material.name = f'{orig_name}__old'
                    mat = self.create_mat()
                    mat.name = orig_name
                    self.materials_map[mat_slot.material] = mat
                    mat_slot.material = mat

    def __exit__(self, type, value, traceback):
        super().__exit__(type, value, traceback)
        if not self.device.use_low_to_low:
            bpy.data.materials.remove(self.mat, do_unlink=True)
        else:
            for orig, new in self.materials_map.items():
                name = new.name
                new.name = 'ASDF'
                orig.name = name


class Map_Context_Curvature(Map_Context_Custom_Material):
    def create_mat(self):
        curv_mat = bpy.data.materials.new('BAKECURV')
        curv_mat.use_nodes = True
        node = curv_mat.node_tree.nodes.new('ShaderNodeNewGeometry')
        ramp_node = curv_mat.node_tree.nodes.new('ShaderNodeValToRGB')
        ramp_node.color_ramp.elements[0].position = 0.45
        ramp_node.color_ramp.elements[1].position = 0.55

        bsdf = curv_mat.node_tree.nodes['Material Output']
        curv_mat.node_tree.links.new(node.outputs['Pointiness'], ramp_node.inputs['Fac'])
        curv_mat.node_tree.links.new(ramp_node.outputs['Color'], bsdf.inputs['Surface'])

        return curv_mat


class EZB_Map_Curvature(bpy.types.PropertyGroup, EZB_Map_Blender):
    id = 'CURVATURE'
    pass_name = 'EMIT'
    label = 'Curvature'
    icon = 'IPO_EASE_IN_OUT'
    category = 'Mesh'

    suffix: bpy.props.StringProperty(default='_CURV')
    active: bpy.props.BoolProperty(default=True)
    bake: bpy.props.BoolProperty(default=False)

    background_color = [0.5, 0.5, 0.5, 1.0]

    context = Map_Context_Curvature

    color_space = 'Non-Color'

    def _draw_info(self, layout):
        # TODO: add contrast prop
        pass
