import bpy
from .map import EZB_Map_Blender, Map_Context, postprocess_enum


class Map_Context_Normal(Map_Context):
    def __init__(self, map, high, low):
        super().__init__(map, high, low)

    def __enter__(self):
        if self.map.triangulate_low:
            self.mod = self.low.modifiers.new('TRIANGULATE', 'TRIANGULATE')

            self.mod.quad_method = self.map.quad_method
            self.mod.ngon_method = self.map.ngon_method
            self.mod.keep_custom_normals = self.map.keep_custom_normals

        return super().__enter__()

    def __exit__(self, type, value, traceback):
        super().__exit__(type, value, traceback)

        if self.map.triangulate_low:
            self.low.modifiers.remove(self.mod)


class EZB_Map_Normal(bpy.types.PropertyGroup, EZB_Map_Blender):
    id = 'NORMAL'
    pass_name = 'NORMAL'
    label = 'Normal'
    icon = 'NORMALS_FACE'
    category = 'Mesh'

    color_space = 'Non-Color'

    suffix: bpy.props.StringProperty(default='_N')
    active: bpy.props.BoolProperty(default=True)
    triangulate_low: bpy.props.BoolProperty(default=False)
    quad_method: bpy.props.EnumProperty(
        items=[(y.identifier, y.name, y.description) for y in bpy.types.TriangulateModifier.bl_rna.properties['quad_method'].enum_items],
        default='SHORTEST_DIAGONAL'
    )
    ngon_method: bpy.props.EnumProperty(
        items=[(y.identifier, y.name, y.description) for y in bpy.types.TriangulateModifier.bl_rna.properties['ngon_method'].enum_items],
        default='BEAUTY'
    )
    keep_custom_normals: bpy.props.BoolProperty(default=False, name='Keep Normals')

    background_color = [0.5, 0.5, 1.0, 1.0]

    normal_space: bpy.props.EnumProperty(
        items=[(y.identifier, y.name, y.description) for y in bpy.types.BakeSettings.bl_rna.properties['normal_space'].enum_items],
        default='TANGENT'
    )
    normal_r: bpy.props.EnumProperty(
        items=[(y.identifier, y.name, y.description) for y in bpy.types.BakeSettings.bl_rna.properties['normal_r'].enum_items],
        default='POS_X'
    )
    normal_g: bpy.props.EnumProperty(
        items=[(y.identifier, y.name, y.description) for y in bpy.types.BakeSettings.bl_rna.properties['normal_g'].enum_items],
        default='POS_Y'
    )
    normal_b: bpy.props.EnumProperty(
        items=[(y.identifier, y.name, y.description) for y in bpy.types.BakeSettings.bl_rna.properties['normal_b'].enum_items],
        default='POS_Z'
    )

    context = Map_Context_Normal

    def setup_settings(self):
        super().setup_settings()
        scene = self.id_data
        scene.render.bake.normal_space = self.normal_space
        scene.render.bake.normal_r = self.normal_r
        scene.render.bake.normal_g = self.normal_g
        scene.render.bake.normal_b = self.normal_b

    def _draw_info(self, layout):
        if self.parent_baker.color_depth == '8':
            layout.prop(self, 'postprocess', text='Postprocess')
        layout.separator(factor=0.5)
        layout.prop(self, "normal_space", text="Space")

        sub = layout.column(align=True)
        sub.prop(self, "normal_r", text="R")
        sub.prop(self, "normal_g", text="G")
        sub.prop(self, "normal_b", text="B")
        layout.separator(factor=0.5)
        layout.prop(self, "samples", text="Samples")
        layout.separator(factor=0.5)
        layout.prop(self, 'triangulate_low', text='Triangulate Low')
        if self.triangulate_low:
            box = layout.box()
            row = box.row(align=True)
            row.separator(factor=8)
            sub = row.column(align=True)
            sub.prop(self, 'quad_method', text='Quad Method')
            sub.prop(self, 'ngon_method', text='Polygon Method')
            sub.prop(self, 'keep_custom_normals')
