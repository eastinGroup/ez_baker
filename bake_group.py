import bpy
from .settings import mode_group_types
from .utilities import traverse_tree

class EZB_Bake_Group(bpy.types.PropertyGroup):
    # group name
    # default cage info (displacement)
    key: bpy.props.StringProperty()
    mode_group: bpy.props.EnumProperty(items=mode_group_types, name="Group By")
    
    cage_displacement: bpy.props.FloatProperty(name='Cage Displacement',default=1)

    def _get_objects(self, suffix):
        suffix = suffix.lower()

        objects = []
        if self.mode_group == 'COLLECTION':
            for x in traverse_tree(bpy.context.scene.collection, exclude_parent=True):
                if x.name.lower() == self.key.lower() + suffix:
                    for y in traverse_tree(x):
                        objects.extend(y.objects[:])
                    break

        elif self.mode_group == 'NAME':
            for x in bpy.context.scene.objects:
                if x.name.lower() == self.key.lower() + suffix:
                    objects.append(x)
                
        return objects

    def draw(self, layout, context):
        ezb_settings = bpy.context.scene.EZB_Settings
        row = layout.row(align=True)
        
        row.prop(self, 'cage_displacement')

        row = layout.split(factor=0.5,align=True)
        row.template_list(
            "EZB_UL_preview_group_objects", 
            "", 
            ezb_settings, 
            "preview_group_objects_high", 
            ezb_settings, 
            "preview_group_objects_high_index", 
            rows=2, 
            sort_lock = False
        )
        row.template_list(
            "EZB_UL_preview_group_objects", 
            "", ezb_settings, 
            "preview_group_objects_low", 
            ezb_settings, 
            "preview_group_objects_low_index", 
            rows=2, 
            sort_lock = False
        )

    def setup_settings(self):
        bake_options = bpy.context.scene.render.bake
        bake_options.use_cage = True
        bake_options.cage_extrusion = self.cage_displacement

    @property
    def objects_high(self):
        return self._get_objects(bpy.context.scene.EZB_Settings.suffix_high)

    @property
    def objects_low(self):
        low = self._get_objects(bpy.context.scene.EZB_Settings.suffix_low)
        return [x for x in low if not x.name.endswith(bpy.context.scene.EZB_Settings.suffix_cage)]


classes = [EZB_Bake_Group]

def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    
    for cls in reversed(classes):
        unregister_class(cls)
