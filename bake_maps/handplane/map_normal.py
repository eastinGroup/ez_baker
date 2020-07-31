import bpy
from .map import EZB_Map_Handplane


class EZB_Map_Normal(bpy.types.PropertyGroup, EZB_Map_Handplane):
    id = 'NORMAL'
    pass_name = 'NORMAL'
    label = 'Normal'
    icon = 'NORMALS_FACE'

    suffix: bpy.props.StringProperty(default='_N')
    active: bpy.props.BoolProperty(default=True)
    triangulate_low: bpy.props.BoolProperty(default=True)
    #TODO: add triangulation options (beauty or whatever)

    background_color = [0.5, 0.5, 1.0, 1.0]

    def _draw_info(self, layout):
        layout.prop(self, 'triangulate_low', text='Triangulate')

        