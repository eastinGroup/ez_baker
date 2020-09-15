import bpy
from .map import EZB_Map_Handplane


class EZB_Map_Curvature(bpy.types.PropertyGroup, EZB_Map_Handplane):
    id = 'CURVATURE'
    pass_name = 'curve'
    label = 'Curvature'
    icon = 'SPHERECURVE'

    suffix: bpy.props.StringProperty(default='_CURV')
    active: bpy.props.BoolProperty(default=True)
    bake: bpy.props.BoolProperty(default=False)

    use_ray_sampling: bpy.props.BoolProperty(name='Use Ray Sampling', default=False)
    sample_radius: bpy.props.FloatProperty(name='Sample Radius', default=0.05)
    sample_count: bpy.props.IntProperty(name='Sample Count', default=20)
    pixel_radius: bpy.props.IntProperty(name='Pixel Radius', default=4)
    auto_normalize: bpy.props.BoolProperty(name='Auto Normalize', default=True)

    max_angle: bpy.props.FloatProperty(name='Max Angle', default=100.0)
    gamma: bpy.props.FloatProperty(name='Gamma', default=1.0)

    background_color = [0.5, 0.5, 1.0, 1.0]

    def _draw_info(self, layout):
        layout.prop(self, 'use_ray_sampling')
        layout.prop(self, 'sample_radius')
        layout.prop(self, 'sample_count')
        layout.prop(self, 'pixel_radius')
        layout.prop(self, 'auto_normalize')

        layout.prop(self, 'max_angle')
        layout.prop(self, 'gamma')
