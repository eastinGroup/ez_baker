import bpy
from ..map import EZB_Map

class Map_Context():
    def __init__(self, baker, map, high, low):
        self.baker = baker
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

        context['active_object'] = self.low
        all_objs = [self.low] + self.high
        context['selected_objects'] = [self.low] + self.high
        context['selected_editable_objects'] = all_objs
        context['editable_objects'] = all_objs
        context['visible_objects'] = all_objs
        context['selectable_objects'] = all_objs
        context['view_layer'] = {'objects':all_objs}

        self.baker.get_device.setup_bake_material(self.low, self.baker, self.map)
        cage = bpy.context.scene.objects.get(self.low.name + bpy.context.scene.EZB_Settings.suffix_cage)
        bpy.context.scene.render.bake.cage_object = cage

        for obj in all_objs:
            self.scene.collection.objects.link(obj)

        context['scene'] = self.scene

        return self.map.pass_name, context

    def __exit__(self, type, value, traceback):
        for i, x in enumerate(self.original_materials_low):
            self.low.material_slots[i].material = x
        for obj, mats in self.original_materials_high.items():
            for i, x in enumerate(mats):
                obj.material_slots[i].material = x
        
        #bpy.data.scenes.remove(self.scene)

class EZB_Map_Blender(EZB_Map):
    pass_name = 'TEST'

    samples: bpy.props.IntProperty(default=1)
    
    context = Map_Context

    def setup_settings(self):
        bake_options = bpy.context.scene.render.bake
        bpy.context.scene.cycles.bake_type = self.pass_name
        bpy.context.scene.cycles.samples = self.samples

        #each map should override this with more settings to setup
