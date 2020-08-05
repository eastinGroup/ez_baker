import bpy
from .map import EZB_Map_Handplane

tangent_space_enum =[
    ('UNREAL_4', 'Unreal Engine 4', ''), 
    ('UNREAL_3', 'Unreal Engine 3', ''), 
    ('UNITY_5_3', 'Unity 5.3', ''), 
    ('UNITY', 'Unity', ''), 
    ('SOURCE', 'Source Engine', ''), 
    ('SOURCE_2', 'Source 2 Engine', ''), 
    ('MAYA_2013_14', 'Autodesk Maya 2013/14', ''), 
    ('MAYA_2012', 'Autodesk Maya 2012', ''), 
    ('3DMAX', 'Autodesk 3DS Max', ''), 
    ('STARCRAFT_II', 'Starcraft II', ''), 
    ('INPUT_TANGENT_AND_BINORMAL', 'Input Tangent and Binormal', ''), 
    ('INPUT_TANGENT_WITH_COMPUTED_BINORMAL', 'Input Tangent with Computed Binormal', '')
]

class EZB_Map_Normal(bpy.types.PropertyGroup, EZB_Map_Handplane):
    id = 'NORMAL'
    pass_name = 'normal_ts'
    label = 'Normal'
    icon = 'NORMALS_FACE'

    suffix: bpy.props.StringProperty(default='_N')
    active: bpy.props.BoolProperty(default=True)

    tangent_space: bpy.props.EnumProperty(items=tangent_space_enum, default='UNITY_5_3')

    background_color = [0.5, 0.5, 1.0, 1.0]

    def _draw_info(self, layout):
        layout.prop(self, 'tangent_space', text='')

        