import bpy
from .settings import mode_group_types
from .utilities import traverse_tree

class EZB_Bake_Group(bpy.types.PropertyGroup):
    # group name
    # default cage info (displacement)
    key: bpy.props.StringProperty()
    mode_group: bpy.props.EnumProperty(items=mode_group_types, name="Group By", default=bpy.context.preferences.addons[__name__.split('.')[0]].preferences.mode_group)
    
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
        
        row.prop(
            ezb_settings,
            'show_bake_group_objects',
            icon="TRIA_DOWN" if ezb_settings.show_bake_group_objects else "TRIA_RIGHT",
            icon_only=True,
            text='',
            emboss=False
        )
        row.prop(self, 'cage_displacement')

        if ezb_settings.show_bake_group_objects:
            row = layout.row(align=True)
            box1 = row.box()
            box1.label(text= 'HIGH')
            col1 = box1.column(align=True)
            high = self.objects_high
            for x in high:
                sub_row = col1.row()
                sub_row.operator('ezb.select_object', text= '', icon='RESTRICT_SELECT_OFF').name = x.name
                sub_row.label(text=x.name)
                
            box2 = row.box()
            box2.label(text= 'LOW')
            col2 = box2.column(align=True)
            low = self.objects_low
            for x in low:
                sub_row = col2.row()
                sub_row.operator('ezb.select_object', text= '', icon='RESTRICT_SELECT_OFF').name = x.name
                sub_row.label(text=x.name)
                cage = context.scene.objects.get(x.name + ezb_settings.suffix_cage)
                if cage:
                    sub_row.operator('ezb.select_object', text= '', icon='SELECT_SET').name = cage.name

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
