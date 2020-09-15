import bpy
from .map import EZB_Map_Marmoset


class EZB_Map_Ambient_Occlusion(bpy.types.PropertyGroup, EZB_Map_Marmoset):
    id = 'Ambient Occlusion'
    label = 'Ambient Occlusion'
    icon = 'SHADING_RENDERED'
    category = 'Lighting'

    suffix: bpy.props.StringProperty(default='_ao')
    active: bpy.props.BoolProperty(default=False)

    dither: bpy.props.BoolProperty(default=True, name='Dither')
    addCavity: bpy.props.BoolProperty(default=False, name='Add Cavity')
    floor: bpy.props.FloatProperty(default=0.8, name='Floor', min=0.0, max=1.0, subtype='FACTOR')
    floorOcclusion: bpy.props.BoolProperty(default=False, name='Floor Occlusion')
    ignoreGroups: bpy.props.BoolProperty(default=True, name='Ignore Groups')
    rayCount: bpy.props.IntProperty(default=256, name='Ray Count', min=32, max=4096, subtype='FACTOR')
    searchDistance: bpy.props.FloatProperty(default=0.0, name='Search Distance', min=0.0, max=100.0, subtype='FACTOR')
    twoSided: bpy.props.BoolProperty(default=False, name='Two-Sided')
    uniform: bpy.props.BoolProperty(default=True, name='Uniform')

    # TODO: Ray bias is not exposed to python API?

    settings_to_copy = [
        'dither',
        'addCavity',
        'floor',
        'floorOcclusion',
        'ignoreGroups',
        'rayCount',
        'searchDistance',
        'twoSided',
        'uniform'
    ]

    def _draw_info(self, layout):
        layout.prop(self, 'dither')
        layout.prop(self, 'uniform')
        layout.prop(self, 'twoSided')
        layout.prop(self, 'ignoreGroups')
        layout.prop(self, 'addCavity')
        row = layout.row(align=True)
        row.prop(self, 'floorOcclusion')

        subrow = row.row()
        subrow.enabled = self.floorOcclusion
        subrow.prop(self, 'floor', text='')

        layout.prop(self, 'rayCount')
        layout.prop(self, 'searchDistance')
