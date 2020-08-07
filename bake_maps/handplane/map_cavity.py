import bpy
from .map import EZB_Map_Handplane

class EZB_Map_Cavity(bpy.types.PropertyGroup, EZB_Map_Handplane):
    id = 'CAVITY'
    pass_name = 'cavity'
    label = 'Cavity'
    icon = 'IPO_ELASTIC'

    suffix: bpy.props.StringProperty(default='_CAV')
    active: bpy.props.BoolProperty(default=False)

    sensitivity: bpy.props.FloatProperty(name='Sensitivity', default=0.75)
    bias: bpy.props.FloatProperty(name='Bias', default=0.015)
    gamma: bpy.props.FloatProperty(name='Gamma', default=1.0)
    pixel_radius: bpy.props.IntProperty(name='Pixel Radius', default=4)
    kernel_type: bpy.props.EnumProperty(
        items=[
            ('ConstantBox', 'Constant Box', ''), 
            ('ConstantDisk', 'Constant Disk', ''), 
            ('LinearBox', 'Linear Box', ''), 
            ('LinearDisk', 'Linear Disk', ''), 
            ('Gaussian', 'Gaussian', '')
        ], 
        default='ConstantDisk'
    )

    background_color = [0.5, 0.5, 1.0, 1.0]

    def _draw_info(self, layout):
        layout.prop(self, 'sensitivity')
        layout.prop(self, 'bias')
        layout.prop(self, 'gamma')
        layout.prop(self, 'pixel_radius')
        layout.prop(self, 'kernel_type')

        