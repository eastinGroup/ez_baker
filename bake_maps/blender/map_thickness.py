import bpy
from .map import EZB_Map_Blender, Map_Context
from .map_curvature import Map_Context_Custom_Material


class Map_Context_Thickness(Map_Context_Custom_Material):
    def create_mat(self):
        thickness_mat = bpy.data.materials.new('BAKETHICKNESS')
        thickness_mat.use_nodes = True
        ao_node = thickness_mat.node_tree.nodes.new('ShaderNodeAmbientOcclusion')
        ao_node.inside = True
        ao_node.only_local = True
        ao_node.samples = self.map.samples

        bsdf = thickness_mat.node_tree.nodes['Material Output']
        thickness_mat.node_tree.links.new(ao_node.outputs['AO'], bsdf.inputs['Surface'])

        return thickness_mat


class EZB_Map_Thickness(bpy.types.PropertyGroup, EZB_Map_Blender):
    id = 'THICKNESS'
    pass_name = 'EMIT'
    label = 'Thickness'
    icon = 'META_DATA'
    category = 'Mesh'

    suffix: bpy.props.StringProperty(default='_THCK')

    background_color = [0.5, 0.5, 0.5, 1.0]

    context = Map_Context_Thickness

    samples: bpy.props.IntProperty(name='Samples', default=6)

    def _draw_info(self, layout):
        self.draw_prop_with_warning(layout, self, 'samples', 16)
