import bpy
from .map import EZB_Map_Marmoset


class EZB_Map_Bent_Normals_Object(bpy.types.PropertyGroup, EZB_Map_Marmoset):
    id = 'Bent Normals (Object)'
    label = 'Bent Normals Object'
    icon = 'SNAP_NORMAL'
    category = 'Surface'

    suffix: bpy.props.StringProperty(default='_bentnormalobj')
    active: bpy.props.BoolProperty(default=False)

    dither: bpy.props.BoolProperty(default=True, name='Dither')
    ignoreGroups: bpy.props.BoolProperty(default=False, name='Ignore Groups')
    rayCount: bpy.props.IntProperty(default=256, name='Ray Count', min=32, max=4096, subtype='FACTOR')
    flipX: bpy.props.BoolProperty(default=False, name='Flip X')
    flipY: bpy.props.BoolProperty(default=False, name='Flip Y')
    flipZ: bpy.props.BoolProperty(default=False, name='Flip Z')

    # TODO: Ray bias and search distance is not exposed to python API?

    settings_to_copy = [
        'dither',
        'ignoreGroups',
        'rayCount',
        'flipX',
        'flipY',
        'flipZ',
    ]

    def _draw_info(self, layout):
        layout.prop(self, 'dither')
        layout.prop(self, 'ignoreGroups')
        layout.prop(self, 'rayCount')

        row = layout.row(align=True)
        row.prop(self, 'flipX', toggle=True)
        row.prop(self, 'flipY', toggle=True)
        row.prop(self, 'flipZ', toggle=True)
