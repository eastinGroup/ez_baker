import bpy
from .map import EZB_Map_Marmoset


class EZB_Map_Normals(bpy.types.PropertyGroup, EZB_Map_Marmoset):
    id = 'Normals'
    label = 'Normal'
    icon = 'NORMALS_FACE'
    category = 'Surface'

    suffix: bpy.props.StringProperty(default='_normal')
    active: bpy.props.BoolProperty(default=True)

    dither: bpy.props.BoolProperty(default=True, name='Dither')
    flipX: bpy.props.BoolProperty(default=False, name='Flip X')
    flipY: bpy.props.BoolProperty(default=False, name='Flip Y')
    flipZ: bpy.props.BoolProperty(default=False, name='Flip Z')

    settings_to_copy = ['dither', 'flipX', 'flipY', 'flipZ']

    def _draw_info(self, layout):
        layout.prop(self, 'dither')
        row = layout.row(align=True)
        row.prop(self, 'flipX', toggle=True)
        row.prop(self, 'flipY', toggle=True)
        row.prop(self, 'flipZ', toggle=True)
