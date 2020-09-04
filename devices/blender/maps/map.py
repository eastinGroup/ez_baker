import bpy
from ...map import EZB_Map
from ....utilities import log


class Map_Context():
    def __init__(self, map, high, low):
        self.baker = map.parent_baker
        self.map = map
        self.high = high
        self.low = low
        self.scene = bpy.context.scene.copy()
        for obj in self.scene.collection.objects[:]:
            self.scene.collection.objects.unlink(obj)
        for collection in self.scene.collection.children[:]:
            self.scene.collection.children.unlink(collection)
        #self.scene = bpy.data.scenes.new(f'{self.baker.key}_{self.map.id}')

        self.original_materials_low = [x.material for x in low.material_slots]
        self.original_materials_high = {y: [x.material for x in y.material_slots] for y in high}

    def __enter__(self):
        context = bpy.context.copy()
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        context['object'] = self.low
        context['active_object'] = self.low
        all_objs = [self.low] + self.high

        log('gathering objects...')
        all_obj_and_lights = all_objs[:]
        for obj in bpy.context.scene.objects:
            if obj.type == 'LIGHT' and obj.visible_get():
                all_obj_and_lights.append(obj)

        log(all_obj_and_lights)

        for obj in all_obj_and_lights:
            self.scene.collection.objects.link(obj)
        log('LINKED')

        context['selected_objects'] = all_objs
        context['selected_editable_objects'] = all_objs
        context['editable_objects'] = all_obj_and_lights
        context['visible_objects'] = all_obj_and_lights
        context['selectable_objects'] = all_obj_and_lights
        context['view_layer'] = {'objects': all_obj_and_lights}

        log('Setting bake material...')
        self.baker.child_device.setup_bake_material(self.low, self.baker, self.map)
        log('Material Set')
        cage = bpy.context.scene.objects.get(self.low.name + bpy.context.scene.EZB_Settings.suffix_cage)
        bpy.context.scene.render.bake.cage_object = cage

        context['scene'] = self.scene

        return self.map.pass_name, context

    def __exit__(self, type, value, traceback):
        for i, x in enumerate(self.original_materials_low):
            self.low.material_slots[i].material = x
        for obj, mats in self.original_materials_high.items():
            for i, x in enumerate(mats):
                obj.material_slots[i].material = x

        bpy.data.scenes.remove(self.scene)


class EZB_Created_Image(bpy.types.PropertyGroup):
    material: bpy.props.PointerProperty(type=bpy.types.Material)
    image: bpy.props.PointerProperty(type=bpy.types.Image)


class EZB_Map_Blender(EZB_Map):
    pass_name = 'TEST'

    samples: bpy.props.IntProperty(default=1)

    context = Map_Context

    created_images: bpy.props.CollectionProperty(type=EZB_Created_Image)

    def setup_settings(self):
        bake_options = bpy.context.scene.render.bake
        bpy.context.scene.cycles.bake_type = self.pass_name
        bpy.context.scene.cycles.samples = self.samples

    def do_bake(self):
        self.parent_device.setup_settings()
        self.setup_settings()

        for group in self.parent_baker.bake_groups:
            group.setup_settings()

            high = group.objects_high
            low = group.objects_low

            for x in low:
                self.bake_start(high, x)

    def bake_start(self, high, low):
        with self.context(self, high, low) as tup:
            map_id, selection_context = tup
            log('{} :: {} ...'.format(low.name, self.id))
            bpy.ops.object.bake(selection_context, type=map_id)
            log('FINISHED BAKE')

        # each map should override this with more settings to setup
