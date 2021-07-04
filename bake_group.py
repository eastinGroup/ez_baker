import bpy
from .settings import mode_group_types
from .utilities import traverse_tree


class EZB_Object_Reference(bpy.types.PropertyGroup):
    object: bpy.props.PointerProperty(type=bpy.types.Object)


class EZB_Bake_Group_Custom_Objects(bpy.types.PropertyGroup):
    objects: bpy.props.CollectionProperty(type=EZB_Object_Reference)


class EZB_Bake_Group(bpy.types.PropertyGroup):
    # group name
    # default cage info (displacement)
    key: bpy.props.StringProperty()
    mode_group: bpy.props.EnumProperty(items=mode_group_types, name="Group By")

    custom_low: bpy.props.PointerProperty(type=EZB_Bake_Group_Custom_Objects)
    custom_high: bpy.props.PointerProperty(type=EZB_Bake_Group_Custom_Objects)

    def low_added(self, context):
        if not self.object_low:
            return
        if self.object_low.type != 'MESH':
            self.object_low = None
            return
        collection = self.custom_low.objects.add()
        collection.object = self.object_low
        self.object_low = None

    def high_added(self, context):
        if not self.object_high:
            return
        if self.object_high.type != 'MESH':
            self.object_high = None
            return
        collection = self.custom_high.objects.add()
        collection.object = self.object_high
        self.object_high = None

    def get_override(self):
        return None

    object_low: bpy.props.PointerProperty(type=bpy.types.Object, update=low_added)
    object_high: bpy.props.PointerProperty(type=bpy.types.Object, update=high_added)

    def preview_cage_clicked(self, context):
        if self.preview_cage:
            self.parent_baker.start_previewing_cage(context)
        else:
            self.parent_baker.stop_previewing_cage(context)

        self.update_cage(context)

    def update_cage(self, context):

        new_context = context.copy()

        if self.preview_cage and self.objects_low:
            if self.preview_cage_object:
                mesh = self.preview_cage_object.data
                bpy.data.objects.remove(self.preview_cage_object, do_unlink=True)
                bpy.data.meshes.remove(mesh, do_unlink=True)

                del mesh

            copy_objects = [self.get_cage_copy(x, context) for x in self.objects_low]
            copy_objects_data = [x.data for x in copy_objects]

            new_context['selected_editable_objects'] = copy_objects
            new_context['selected_objects'] = copy_objects
            new_context['active_object'] = copy_objects[-1]

            #new_context['view_layer']['objects']['active'] = copy_objects[-1]

            if len(copy_objects) > 1:
                bpy.ops.object.join(new_context)

            new_context['selected_editable_objects'] = [new_context['active_object']]
            new_context['selected_objects'] = new_context['selected_editable_objects']

            self.preview_cage_object = new_context['active_object']
            self.preview_cage_object.name = self.key + '_preview_cage'
            self.preview_cage_object.data.name = self.key + '_preview_cage'
            self.preview_cage_object.color = (1, 0, 0, 0.3)
            self.preview_cage_object.display_type = 'SOLID'
            # not necessary, it was crashing blender on 2.9
            #bpy.ops.object.convert(new_context, target='MESH')
            self.preview_cage_object.hide_select = True

            for i in reversed(range(0, len(copy_objects) - 1)):
                bpy.data.meshes.remove(copy_objects_data[i], do_unlink=True)

        # if we just delete the mesh everytime we hide the cage, the memory usage piles up like crazy because of the undo system
        # so instead we just hide it until we need it again
        else:
            if self.preview_cage_object:
                collections = self.preview_cage_object.users_collection[:]
                for x in collections:
                    x.objects.unlink(self.preview_cage_object)

    cage_displacement: bpy.props.FloatProperty(
        name='Projection Cage Displacement',
        default=0.05,
        update=update_cage,
        step=0.1,
        precision=3,
        description='Cage extrusion value. It represents the distance from which the rays will be cast for the purpose of baking'
    )
    preview_cage: bpy.props.BoolProperty(update=preview_cage_clicked, name='Preview Cage', description='Creates a temporary object representing the cage used to project the rays')
    preview_cage_object: bpy.props.PointerProperty(type=bpy.types.Object)

    def _remove_numbering(self, name):
        if len(name) > 4 and name[-3:].isdigit() and name[-4] == '.':
            name = name[:-4]
        return name

    def _get_objects(self, obj_type):
        if obj_type == 'HIGH':
            suffix = self.id_data.EZB_Settings.suffix_high
        elif obj_type == 'LOW':
            suffix = self.id_data.EZB_Settings.suffix_low
        suffix = suffix.lower()

        objects = []
        if self.mode_group == 'COLLECTION':
            for x in traverse_tree(self.id_data.collection, exclude_parent=True):
                if self._remove_numbering(x.name.lower()) == self.key.lower() + suffix:
                    for y in traverse_tree(x):
                        objects.extend(y.objects[:])
                    break

        elif self.mode_group == 'NAME':
            for x in self.id_data.objects:
                if self._remove_numbering(x.name.lower()) == self.key.lower() + suffix:
                    objects.append(x)

        elif self.mode_group == 'CUSTOM':
            if obj_type == 'HIGH':
                for x in self.custom_high.objects:
                    objects.append(x.object)
            elif obj_type == 'LOW':
                for x in self.custom_low.objects:
                    objects.append(x.object)

        return objects

    def create_cage_from_object(self, obj, context):

        mod = obj.modifiers.new('DISPLACE', type='DISPLACE')
        mod.mid_level = 0
        mod.strength = self.cage_displacement

        depsgraph = context.evaluated_depsgraph_get()
        obj_evaluated = obj.evaluated_get(depsgraph)
        cage = obj.copy()

        # if evaluated, all modifiers are applied
        cage_data = bpy.data.meshes.new_from_object(obj_evaluated)
        cage.data = cage_data

        cage.modifiers.clear()

        obj.modifiers.remove(mod)

        return cage

    def get_cage_copy(self, obj, context):
        cage = context.scene.objects.get(obj.name + context.scene.EZB_Settings.suffix_cage)
        if cage:
            old_cage = cage
            cage = old_cage.copy()
            depsgraph = context.evaluated_depsgraph_get()

            obj_evaluated = old_cage.evaluated_get(depsgraph)
            cage_data = bpy.data.meshes.new_from_object(obj_evaluated, depsgraph=depsgraph)
            cage.modifiers.clear()
            cage.data = cage_data

        else:
            cage = self.create_cage_from_object(obj, context)
        context.scene.collection.objects.link(cage)
        for mat_slot in cage.material_slots:
            mat_slot.material = None

        cage.select_set(True)
        return cage

    def setup_settings(self):
        bake_options = self.id_data.render.bake
        bake_options.use_cage = True
        bake_options.cage_extrusion = self.cage_displacement

    @property
    def parent_baker(self):
        return next(x for x in self.id_data.EZB_Settings.bakers if self in x.bake_groups[:])

    @property
    def objects_high(self):
        if self.parent_baker.child_device.use_low_to_low:
            return []
        return self._get_objects('HIGH')

    @property
    def objects_low(self):
        low = self._get_objects('LOW')
        return [x for x in low if not x.name.endswith(self.id_data.EZB_Settings.suffix_cage)]


classes = [EZB_Object_Reference, EZB_Bake_Group_Custom_Objects, EZB_Bake_Group]


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
