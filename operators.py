import bpy
from .utilities import traverse_tree
from . import bake_maps

class EZB_OT_new_baker(bpy.types.Operator):
    """New Baker"""
    bl_idname = "ezb.new_baker"
    bl_label = "New Baker"

    @classmethod
    def poll(cls, context):
        ezb_settings = bpy.context.scene.EZB_Settings
        return True

    def execute(self, context):
        ezb_settings = bpy.context.scene.EZB_Settings
        new_baker=ezb_settings.bakers.add()
        index=len(ezb_settings.bakers) - 1
        ezb_settings.baker_index = index
        new_baker.key='Baker {}'.format(index)
        return {'FINISHED'}

class EZB_OT_remove_baker(bpy.types.Operator):
    """Remove Baker"""
    bl_idname = "ezb.remove_baker"
    bl_label = "Remove Baker"

    @classmethod
    def poll(cls, context):
        ezb_settings = bpy.context.scene.EZB_Settings
        return len(ezb_settings.bakers) > ezb_settings.baker_index

    def execute(self, context):
        ezb_settings = bpy.context.scene.EZB_Settings
        ezb_settings.bakers.remove(ezb_settings.baker_index)
        if ezb_settings.baker_index >= len(ezb_settings.bakers):
            ezb_settings.baker_index = len(ezb_settings.bakers)-1
        return {'FINISHED'}

last_bake_groups = None

def get_possible_bake_groups(self, context):
    global last_bake_groups
    ezb_settings = bpy.context.scene.EZB_Settings
    baker = bpy.context.scene.EZB_Settings.bakers[bpy.context.scene.EZB_Settings.baker_index]
    ans = set()

    def is_group_valid(orig_name, type):
        name = orig_name.lower()
        suffix_high = ezb_settings.suffix_high.lower()
        suffix_low = ezb_settings.suffix_low.lower()
        group_name = ''
        if name.endswith(suffix_high):
            group_name = name[:-(len(suffix_high))]
        elif name.endswith(suffix_low):
            group_name = name[:-(len(suffix_low))]

        if group_name:
            for i, group in enumerate([x for x in baker.bake_groups]):
                if group_name == group.key and type == group.mode_group:
                    return ''

        return group_name
        

    for x in traverse_tree(bpy.context.scene.collection, exclude_parent=True):
        group_name = is_group_valid(x.name, 'COLLECTION')
        if group_name:
            ans.add((group_name,'COLLECTION', 'GROUP'))    

    for x in bpy.context.scene.objects:
        if x.type == 'MESH':
            group_name = is_group_valid(x.name, 'NAME')
            if group_name:
                ans.add((group_name, 'NAME', 'OUTLINER_OB_MESH'))
    ans = list(ans)
    last_bake_groups = [(x[1]+'___'+x[0],x[0],x[0],x[2],i) for i,x in enumerate(ans)]
    return last_bake_groups

class EZB_OT_new_bake_group(bpy.types.Operator):
    """Bake groups are created by searching the scene for objects or collections that match the naming patterns in the settings panel.
So you need Collections or Objects already created. 
e.g. "test_low" and "test_high" objects"""
    bl_idname = "ezb.new_bake_group"
    bl_label = "New Bake Group"
    

    name: bpy.props.EnumProperty(items=get_possible_bake_groups)

    @classmethod
    def poll(cls, context):
        ezb_settings = bpy.context.scene.EZB_Settings
        return True

    def execute(self, context):
        baker = bpy.context.scene.EZB_Settings.bakers[bpy.context.scene.EZB_Settings.baker_index]
        new_bake_group=baker.bake_groups.add()
        index=len(baker.bake_groups) - 1
        baker.bake_group_index = index
        group, name = self.name.split('___')
        new_bake_group.key = name
        new_bake_group.mode_group = group
        return {'FINISHED'}

class EZB_OT_remove_bake_group(bpy.types.Operator):
    """Remove Bake Group"""
    bl_idname = "ezb.remove_bake_group"
    bl_label = "Remove Bake Group"

    @classmethod
    def poll(cls, context):
        baker = bpy.context.scene.EZB_Settings.bakers[bpy.context.scene.EZB_Settings.baker_index]
        return len(baker.bake_groups) > baker.bake_group_index

    def execute(self, context):
        baker = bpy.context.scene.EZB_Settings.bakers[bpy.context.scene.EZB_Settings.baker_index]
        baker.bake_groups.remove(baker.bake_group_index)

        if baker.bake_group_index >= len(baker.bake_groups):
            baker.bake_group_index = len(baker.bake_groups)-1
        return {'FINISHED'}


class EZB_OT_show_high_objects(bpy.types.Operator):
    """Show High Objects"""
    bl_idname = "ezb.show_high_objects"
    bl_label = "Show High Objects"

    index: bpy.props.IntProperty(name="index")

    @classmethod
    def description(cls, context, properties):
        ans = ''
        baker = bpy.context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        bake_group = baker.bake_groups[properties.index]
        for x in bake_group.objects_high:
            ans += x.name + '\n'
        return ans

    def execute(self, context):
        baker = bpy.context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        bake_group = baker.bake_groups[self.index]
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode = 'OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')
        for x in bake_group.objects_high:
            x.select_set(True)
        return {'FINISHED'}

class EZB_OT_show_low_objects(bpy.types.Operator):
    """Show Low Objects"""
    bl_idname = "ezb.show_low_objects"
    bl_label = "Show Low Objects"

    index: bpy.props.IntProperty(name="index")

    @classmethod
    def description(cls, context, properties):
        ans = ''
        baker = bpy.context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        bake_group = baker.bake_groups[properties.index]
        for x in bake_group.objects_low:
            ans += x.name + '\n'
        return ans

    def execute(self, context):
        baker = bpy.context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        bake_group = baker.bake_groups[self.index]
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode = 'OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')
        for x in bake_group.objects_low:
            x.select_set(True)
        return {'FINISHED'}


class EZB_OT_bake(bpy.types.Operator):
    """Bake"""
    bl_idname = "ezb.bake"
    bl_label = "Bake"

    @classmethod
    def description(cls, context, properties):
        baker = bpy.context.scene.EZB_Settings.bakers[bpy.context.scene.EZB_Settings.baker_index]
        if not any(getattr(baker.maps, x.id).active for x in bake_maps.maps):
            return 'No maps to bake. Add a map with the "add map" dropdown'
        troublesome_objects = baker.get_troublesome_objects()
        if troublesome_objects:
            ans = 'Some objects have incorrect or missing materials:\n'
            for x in troublesome_objects:
                ans += x
                ans += '\n'
            return ans
        for group in baker.bake_groups:
            if not group.objects_low:
                return 'Some bake groups have no low objects assigned'
        for group in baker.bake_groups:
            if not group.objects_high:
                return 'Some bake groups have no high objects assigned'
        if not baker.bake_groups:
            return 'You need to create a bake group first\nMake sure you have one object (or collection) named "example_low" and another one named "example_high"\nYou will now be able to add the bake group with the dropdown'
        return 'Bake'

    @classmethod
    def poll(cls, context):
        baker = bpy.context.scene.EZB_Settings.bakers[bpy.context.scene.EZB_Settings.baker_index]
        available_maps = any(getattr(baker.maps, x.id).active for x in bake_maps.maps)
        if not available_maps:
            return False
        if baker.get_troublesome_objects():
            return False
        for group in baker.bake_groups:
            if not group.objects_low:
                return False
        for group in baker.bake_groups:
            if not group.objects_high:
                return False
        if not baker.bake_groups:
            return False
        return True

    def execute(self, context):
        baker = bpy.context.scene.EZB_Settings.bakers[bpy.context.scene.EZB_Settings.baker_index]
        baker.bake()
        return {'FINISHED'}

last_maps = None
def get_possible_maps(self, context):
    global last_maps
    last_maps = [(x.id, x.label, x.label, '', i) for i, x in enumerate(bake_maps.maps)]
    return last_maps


class EZB_OT_add_map(bpy.types.Operator):
    """Add Map"""
    bl_idname = "ezb.add_map"
    bl_label = "Add Map"

    map: bpy.props.EnumProperty(items=get_possible_maps)

    def execute(self, context):
        baker = bpy.context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        map = getattr(baker.maps, self.map)
        map.active=True
        map.show_info=True
        return {'FINISHED'}

class EZB_OT_show_image(bpy.types.Operator):
    """Show Image"""
    bl_idname = "ezb.show_image"
    bl_label = "Show Image"

    image: bpy.props.StringProperty()

    def execute(self, context):
        image = bpy.data.images.get(self.image)
        for area in bpy.context.screen.areas :
            if area.type == 'IMAGE_EDITOR' :
                    area.spaces.active.image = image
        return {'FINISHED'}


class EZB_OT_export(bpy.types.Operator):
    """Export"""
    bl_idname = "ezb.export"
    bl_label = "Export"

    @classmethod
    def description(cls, context, properties):
        baker = bpy.context.scene.EZB_Settings.bakers[bpy.context.scene.EZB_Settings.baker_index]
        if not baker.path:
            return 'Export Path not set'
        images_correct = False
        for x in baker.materials:
            for y in x.images:
                if y.image:
                    images_correct = True
                    break
            if images_correct:
                break
        if not images_correct:
            return 'There are no images to export, make sure you bake the textures before exporting'
        return 'Export'

    @classmethod
    def poll(cls, context):
        baker = bpy.context.scene.EZB_Settings.bakers[bpy.context.scene.EZB_Settings.baker_index]
        if not baker.path:
            return False
        images_correct = False
        for x in baker.materials:
            for y in x.images:
                if y.image:
                    images_correct = True
                    break
            if images_correct:
                break
        if not images_correct:
            return False
        return True

    def execute(self, context):
        baker = bpy.context.scene.EZB_Settings.bakers[bpy.context.scene.EZB_Settings.baker_index]
        baker.export()
        return {'FINISHED'}

class EZB_OT_select_texture_size(bpy.types.Operator):
    """Select Texture Size"""
    bl_idname = "ezb.select_texture_size"
    bl_label = "Select Texture Size"

    size: bpy.props.EnumProperty(items=[
        ('256', '256', '256'),
        ('512', '512', '512'),
        ('1024', '1k', '1024'),
        ('2048', '2k', '2048'),
        ('4096', '4k', '4096'),
        ('8192', '8k', '8192'),
    ])

    def execute(self, context):
        baker = bpy.context.scene.EZB_Settings.bakers[bpy.context.scene.EZB_Settings.baker_index]
        if self.size == '256':
            baker.width = 256
            baker.height = 256
        elif self.size == '512':
            baker.width = 512
            baker.height = 512
        elif self.size == '1024':
            baker.width = 1024
            baker.height = 1024
        elif self.size == '2048':
            baker.width = 2048
            baker.height = 2048
        elif self.size == '4096':
            baker.width = 4096
            baker.height = 4096
        elif self.size == '8192':
            baker.width = 8192
            baker.height = 8192
        return {'FINISHED'}



class EZB_OT_select_object(bpy.types.Operator):
    """Select Object"""
    bl_idname = "ezb.select_object"
    bl_label = "Select Object"

    name: bpy.props.StringProperty()

    def execute(self, context):
        obj = context.scene.objects.get(self.name)
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode = 'OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')
        if obj:
            obj.select_set(True)
        return {'FINISHED'}

classes = [
    EZB_OT_new_baker,
    EZB_OT_remove_baker,
    EZB_OT_new_bake_group,
    EZB_OT_remove_bake_group,
    EZB_OT_show_high_objects,
    EZB_OT_show_low_objects,
    EZB_OT_add_map,
    EZB_OT_bake,
    EZB_OT_export,
    EZB_OT_show_image,
    EZB_OT_select_texture_size,
    EZB_OT_select_object,
]

def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    
    for cls in reversed(classes):
        unregister_class(cls)