import bpy
from .map import EZB_Map_Blender, Map_Context
from .map_curvature import Map_Context_Custom_Material


class Map_Context_Position(Map_Context_Custom_Material):
    def create_mat(self):
        position_mat = bpy.data.materials.new('BAKEPOSITION')
        position_mat.use_nodes = True
        geom = position_mat.node_tree.nodes.new('ShaderNodeNewGeometry')

        pos_offset = position_mat.node_tree.nodes.new('ShaderNodeVectorMath')
        pos_offset.operation = 'ADD'
        pos_offset.inputs[1].default_value[0] = self.map.offset[0]
        pos_offset.inputs[1].default_value[1] = self.map.offset[1]
        pos_offset.inputs[1].default_value[2] = self.map.offset[2]

        scale = position_mat.node_tree.nodes.new('ShaderNodeVectorMath')
        scale.operation = 'MULTIPLY'
        scale.inputs[1].default_value[0] = self.map.scale
        scale.inputs[1].default_value[1] = self.map.scale
        scale.inputs[1].default_value[2] = self.map.scale

        bsdf = position_mat.node_tree.nodes['Material Output']
        position_mat.node_tree.links.new(geom.outputs[0], pos_offset.inputs[0])
        position_mat.node_tree.links.new(pos_offset.outputs[0], scale.inputs[0])
        position_mat.node_tree.links.new(scale.outputs[0], bsdf.inputs['Surface'])

        return position_mat


class EZB_Map_Position(bpy.types.PropertyGroup, EZB_Map_Blender):
    id = 'POSITION'
    pass_name = 'EMIT'
    label = 'Position'
    icon = 'IPO_EASE_IN_OUT'
    category = 'Mesh'

    suffix: bpy.props.StringProperty(default='_POS')
    active: bpy.props.BoolProperty(default=False)
    bake: bpy.props.BoolProperty(default=False)

    background_color = [0.0, 0.0, 0.0, 1.0]

    context = Map_Context_Position

    offset: bpy.props.FloatVectorProperty()
    scale: bpy.props.FloatProperty(default=1)

    color_space = 'Non-Color'

    def _draw_info(self, layout):
        # TODO: add contrast prop
        layout.prop(self, 'offset')
        layout.prop(self, 'scale')
        pass
