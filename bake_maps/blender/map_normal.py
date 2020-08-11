import bpy
from .map import EZB_Map_Blender, Map_Context

class Map_Context_Normal(Map_Context):
    def __init__(self, baker, map, high, low):
        super().__init__(baker, map, high, low)

    def __enter__(self):
        if self.map.triangulate_low:
            self.mod = self.low.modifiers.new('TRIANGULATE', 'TRIANGULATE')
            self.mod.quad_method = self.map.quad_method
            self.mod.ngon_method = self.map.ngon_method
        
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
    triangulate_low: bpy.props.BoolProperty(default=True)
    quad_method: bpy.props.EnumProperty(
        items=[(y.identifier, y.name, y.description) for y in bpy.types.TriangulateModifier.bl_rna.properties['quad_method'].enum_items],
        default='BEAUTY'
        )
    ngon_method: bpy.props.EnumProperty(
        items=[(y.identifier, y.name, y.description) for y in bpy.types.TriangulateModifier.bl_rna.properties['ngon_method'].enum_items],
        default='BEAUTY'
        )
    #TODO: add triangulation options (beauty or whatever)

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
        bpy.context.scene.render.bake.normal_space = self.normal_space
        bpy.context.scene.render.bake.normal_r = self.normal_r
        bpy.context.scene.render.bake.normal_g = self.normal_g
        bpy.context.scene.render.bake.normal_b = self.normal_b


    def _draw_info(self, layout):
        layout.prop(self, "normal_space", text="Space")
        
        sub = layout.column(align=True)
        sub.prop(self, "normal_r", text="R")
        sub.prop(self, "normal_g", text="G")
        sub.prop(self, "normal_b", text="B")
        layout.prop(self, "samples", text="Samples")

        layout.prop(self, 'triangulate_low', text='Triangulate')
        if self.triangulate_low:
            row = layout.row(align=True)
            row.separator(factor=8)
            sub = row.column(align=True)
            sub.prop(self, 'quad_method', text='Quad Method')
            sub.prop(self, 'ngon_method', text='Polygon Method')