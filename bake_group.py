import bpy
from .settings import mode_group_types
from .utilities import traverse_tree

def update_cage(self, context):

    def get_copy_cage(obj):
        cage = bpy.context.scene.objects.get(obj.name + bpy.context.scene.EZB_Settings.suffix_cage)
        if cage:
            cage = cage.copy()
            cage_data = cage.data.copy()
            cage.data = cage_data
        else:
            cage = obj.copy()
            cage_data = cage.data.copy()
            cage.data = cage_data

            mod = cage.modifiers.new('DISPLACE', type='DISPLACE')
            mod.mid_level = 0
            mod.strength = self.cage_displacement
        bpy.context.scene.collection.objects.link(cage)
        return cage

    if self.preview_cage_object:
        mesh = self.preview_cage_object.data
        bpy.data.objects.remove(self.preview_cage_object, do_unlink=True)
        bpy.data.meshes.remove(mesh, do_unlink=True)

    if self.preview_cage:
        bpy.context.space_data.shading.type = 'SOLID'
        bpy.context.space_data.shading.color_type = 'OBJECT'

        copy_objects = [get_copy_cage(x) for x in self.objects_low]
        copy_objects_data = [x.data for x in copy_objects]

        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')
        for x in copy_objects:
            x.select_set(True)
            bpy.context.view_layer.objects.active=x
        if len(copy_objects) >1:
            bpy.ops.object.join()
            

        self.preview_cage_object = bpy.context.view_layer.objects.active
        self.preview_cage_object.name = self.key + '_preview_cage'
        self.preview_cage_object.data.name = self.key + '_preview_cage'
        self.preview_cage_object.color = (1, 0, 0, 0.3)
        self.preview_cage_object.display_type='SOLID'
        bpy.ops.object.convert(target='MESH')

        for i in reversed(range(0, len(copy_objects) - 1)):
            bpy.data.meshes.remove(copy_objects_data[i], do_unlink=True)

        bpy.context.view_layer.objects.active = None


class EZB_Bake_Group(bpy.types.PropertyGroup):
    # group name
    # default cage info (displacement)
    key: bpy.props.StringProperty()
    mode_group: bpy.props.EnumProperty(items=mode_group_types, name="Group By")
    
    cage_displacement: bpy.props.FloatProperty(name='Cage Displacement', default=1, update=update_cage)

    preview_cage: bpy.props.BoolProperty(update=update_cage)
    preview_cage_object: bpy.props.PointerProperty(type=bpy.types.Object)


    def _remove_numbering(self, name):
        if name[-3:].isdigit() and name[-4] == '.':
            name = name[:-4]
        return name


    def _get_objects(self, suffix):
        suffix = suffix.lower()

        objects = []
        if self.mode_group == 'COLLECTION':
            for x in traverse_tree(bpy.context.scene.collection, exclude_parent=True):
                if self._remove_numbering(x.name.lower()) == self.key.lower() + suffix:
                    for y in traverse_tree(x):
                        objects.extend(y.objects[:])
                    break

        elif self.mode_group == 'NAME':
            for x in bpy.context.scene.objects:
                if self._remove_numbering(x.name.lower()) == self.key.lower() + suffix:
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
