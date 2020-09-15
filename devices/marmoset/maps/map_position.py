import bpy
from .map import EZB_Map_Marmoset


class EZB_Map_Position(bpy.types.PropertyGroup, EZB_Map_Marmoset):
    id = 'Position'
    label = 'Position'
    icon = 'ORIENTATION_LOCAL'
    category = 'Surface'

    suffix: bpy.props.StringProperty(default='_position')
    active: bpy.props.BoolProperty(default=False)

    normalization: bpy.props.EnumProperty(items=[
        ('Bounding Sphere', 'Bounding Sphere', ''),
        ('Bounding Box', 'Bounding Box', ''),
        ('Disabled', 'Disabled', '')
    ], name='Normalization')

    settings_to_copy = [
        'normalization',
    ]

    def _draw_info(self, layout):
        layout.prop(self, 'normalization')
