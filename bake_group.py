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
        for mat_slot in cage.material_slots:
            mat_slot.material = None

        cage.select_set(True)
        return cage

    new_context = context.copy()
    
    if self.preview_cage and self.objects_low:
        if self.preview_cage_object:
            mesh = self.preview_cage_object.data
            bpy.data.objects.remove(self.preview_cage_object, do_unlink=True)
            bpy.data.meshes.remove(mesh, do_unlink=True)

            del mesh
        bpy.context.space_data.shading.type = 'SOLID'
        bpy.context.space_data.shading.color_type = 'OBJECT'

        copy_objects = [get_copy_cage(x) for x in self.objects_low]
        copy_objects_data = [x.data for x in copy_objects]

        new_context['selected_editable_objects'] = copy_objects
        new_context['selected_objects'] = copy_objects
        new_context['active_object'] = copy_objects[-1]
        #new_context['view_layer']['objects']['active'] = copy_objects[-1]

        if len(copy_objects) >1:
            bpy.ops.object.join(new_context)
        
        new_context['selected_editable_objects'] = [new_context['active_object']]
        new_context['selected_objects'] = new_context['selected_editable_objects']

        self.preview_cage_object = new_context['active_object']
        self.preview_cage_object.name = self.key + '_preview_cage'
        self.preview_cage_object.data.name = self.key + '_preview_cage'
        self.preview_cage_object.color = (1, 0, 0, 0.3)
        self.preview_cage_object.display_type='SOLID'
        #not necessary, it was crashing blender on 2.9
        #bpy.ops.object.convert(new_context, target='MESH')
        self.preview_cage_object.hide_select=True

        for i in reversed(range(0, len(copy_objects) - 1)):
            bpy.data.meshes.remove(copy_objects_data[i], do_unlink=True)

    # if we just delete the mesh everytime we hide the cage, the memory usage piles up like crazy because of the undo system
    # so instead we just hide it until we need it again
    else:
        if self.preview_cage_object:
            collections = self.preview_cage_object.users_collection[:]
            for x in collections:
                x.objects.unlink(self.preview_cage_object)

'''

I created 20 groups of 1k triangles each. My scene is at 30mb. After checking and unchecking all of them multiple times I get to 60mb. 

After that I add a 16 million mesh. Its now at 3.19gb .I do the same, it gets to 5.18gb. 

I completely remove the high poly and after flushing the undo it gets down to 2.13gb. So yes, literally 2gb came out of nowhere. 

I unlink manually all the cages from the file and after flushing the undo again, it gets down to 33mb. 

So yes, those cages somehow waste more memory the more the scene weighs. B
ut I just found out that's default blender behaviour, not something I missed. 
Because the same thing can be reproduced if you do this manually. e.g.

I create the 16 milion mesh and the file is at 3.19gb, I now select all the low poly objects (20 of them), duplicate them, delete them and suddenly we get to 5.24gb

solution: uncheck global undo in the system settings
'''


class EZB_Bake_Group(bpy.types.PropertyGroup):
    # group name
    # default cage info (displacement)
    key: bpy.props.StringProperty()
    mode_group: bpy.props.EnumProperty(items=mode_group_types, name="Group By")
    
    cage_displacement: bpy.props.FloatProperty(name='Cage Displacement', default=0.05, update=update_cage, step=0.1, precision=3)

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

    def setup_settings(self):
        bake_options = bpy.context.scene.render.bake
        bake_options.use_cage = True
        bake_options.cage_extrusion = self.cage_displacement
    
    @property
    def parent_baker(self):
        return next(x for x in bpy.context.scene.EZB_Settings.bakers if self in x.bake_groups[:])

    @property
    def objects_high(self):
        if self.parent_baker.use_low_to_low:
            return []
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
