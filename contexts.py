import bpy
from . utilities import traverse_tree

class Scene_Visible():
    def __init__(self):
        pass

    def __enter__(self):
        self.active_obj = bpy.context.view_layer.objects.active
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        if bpy.context.space_data.local_view:
            bpy.ops.view3d.localview()
        

        # we need to traverse the tree from child to parent or else the exclude property can be missed
        layers_in_hierarchy = reversed(list(traverse_tree(bpy.context.view_layer.layer_collection, exclude_parent=True)))
        for layer_collection in layers_in_hierarchy:
            bpy.data.collections[layer_collection.name]['__orig_exclude__'] = layer_collection.exclude
            bpy.data.collections[layer_collection.name]['__orig_hide_lc__'] = layer_collection.hide_viewport
            layer_collection.exclude = False
            layer_collection.hide_viewport = False

        for collection in bpy.data.collections:
            collection['__orig_hide__'] = collection.hide_viewport
            collection['__orig_hide_select__'] = collection.hide_select

            collection.hide_select = False
            collection.hide_viewport = False

        for obj in bpy.data.objects:
            obj['__orig_hide__'] = obj.hide_viewport
            obj['__orig_hide_select__'] = obj.hide_select
            obj['__orig_collection__'] = obj.users_collection[0].name if obj.users_collection else '__NONE__'
            obj['__orig_hide_vl__'] = obj.hide_get()
            obj['__orig_select__'] = obj.select_get()

            obj.hide_viewport = False
            obj.hide_select = False
            obj.hide_set(False)
        
        bpy.ops.object.select_all(action='DESELECT')

    def __exit__(self, type, value, traceback):
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')
        # now restore original values
        for obj in bpy.data.objects:
            obj.hide_viewport = obj['__orig_hide__']
            obj.hide_select = obj['__orig_hide_select__']
            obj.hide_set(bool(obj['__orig_hide_vl__']))
            obj.select_set(bool(obj['__orig_select__']))

            del obj['__orig_hide__']
            del obj['__orig_hide_select__']
            del obj['__orig_hide_vl__']
            del obj['__orig_collection__']
            del obj['__orig_select__']

        for collection in bpy.data.collections:
            collection.hide_viewport = collection['__orig_hide__']
            collection.hide_select = collection['__orig_hide_select__']

            del collection['__orig_hide__']
            del collection['__orig_hide_select__']

        layers_in_hierarchy = reversed(list(traverse_tree(bpy.context.view_layer.layer_collection, exclude_parent=True)))
        for layer_collection in layers_in_hierarchy:
            layer_collection.exclude = bpy.data.collections[layer_collection.name]['__orig_exclude__']
            layer_collection.hide_viewport = bpy.data.collections[layer_collection.name]['__orig_hide_lc__']
            del bpy.data.collections[layer_collection.name]['__orig_exclude__']
            del bpy.data.collections[layer_collection.name]['__orig_hide_lc__']
        
        bpy.context.view_layer.objects.active = self.active_obj

class Custom_Render_Settings():
    def __init__(self):
        pass

    def collect_attributes(self, obj):
        return {x.identifier: getattr(obj, x.identifier) for x in obj.bl_rna.properties if not x.is_readonly}

    def __enter__(self):
        self.bake = self.collect_attributes(bpy.context.scene.render.bake)
        self.view_settings = self.collect_attributes(bpy.context.scene.view_settings)
        self.image_settings = self.collect_attributes(bpy.context.scene.render.image_settings)
        self.render = self.collect_attributes(bpy.context.scene.render)
        self.cycles = self.collect_attributes(bpy.context.scene.cycles)

    def restore_attributes(self, obj, orig_attribs):
        for id, value in orig_attribs.items():
            setattr(obj, id, value)

    def __exit__(self, type, value, traceback):
        self.restore_attributes(bpy.context.scene.view_settings, self.view_settings)
        self.restore_attributes(bpy.context.scene.render.image_settings, self.image_settings)
        self.restore_attributes(bpy.context.scene.render, self.render)
        self.restore_attributes(bpy.context.scene.cycles, self.cycles)
        self.restore_attributes(bpy.context.scene.render.bake, self.bake)

class Bake_Setup():
    def __init__(self, baker, map, high, low):
        self.baker = baker
        self.map = map
        self.high = high
        self.low = low

        self.original_materials = [x.material for x in low.material_slots]

    def __enter__(self):
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')
        self.low.select_set(True)
        bpy.context.view_layer.objects.active = self.low
        for x in self.high:
            x.select_set(True)

        self.baker.setup_bake_material(self.low, self.map)
        cage = bpy.context.scene.objects.get(self.low.name + bpy.context.scene.EZB_Settings.suffix_cage)
        bpy.context.scene.render.bake.cage_object = cage

        return self.map.id

    def __exit__(self, type, value, traceback):
        for i, x in enumerate(self.original_materials):
            self.low.material_slots[i].material = x