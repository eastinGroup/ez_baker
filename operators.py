import bpy
from .utilities import traverse_tree
from . import bake_group


class EZB_OT_new_baker(bpy.types.Operator):
    """Create a new Baker"""
    bl_idname = "ezb.new_baker"
    bl_label = "New Baker"

    @classmethod
    def poll(cls, context):
        ezb_settings = bpy.context.scene.EZB_Settings
        return True

    def execute(self, context):
        ezb_settings = bpy.context.scene.EZB_Settings
        new_baker = ezb_settings.bakers.add()
        index = len(ezb_settings.bakers) - 1
        ezb_settings.baker_index = index
        new_baker.key = 'Baker_{}'.format(index)
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

        baker = ezb_settings.bakers[ezb_settings.baker_index]
        for bake_group in baker.bake_groups:
            bake_group.preview_cage = False

        ezb_settings.bakers.remove(ezb_settings.baker_index)
        if ezb_settings.baker_index >= len(ezb_settings.bakers):
            ezb_settings.baker_index = len(ezb_settings.bakers) - 1
        return {'FINISHED'}


last_bake_groups = None


def get_possible_bake_groups(objects):
    objects = objects[:]
    ezb_settings = bpy.context.scene.EZB_Settings
    baker = bpy.context.scene.EZB_Settings.bakers[bpy.context.scene.EZB_Settings.baker_index]
    ans = set()

    def is_group_valid(orig_name, type):
        name = orig_name.lower()
        if name[-3:].isdigit() and name[-4] == '.':
            name = name[:-4]

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
        if group_name and any(obj in objects for obj in x.objects):
            ans.add((group_name, 'COLLECTION', 'GROUP'))

    for x in objects:
        if x.type == 'MESH':
            group_name = is_group_valid(x.name, 'NAME')
            if group_name:
                ans.add((group_name, 'NAME', 'OUTLINER_OB_MESH'))

    return ans


def get_possible_bake_groups_enums(self, context):
    global last_bake_groups
    ans = list(get_possible_bake_groups(bpy.context.scene.objects))
    last_bake_groups = [(x[1] + '___' + x[0], x[0], x[0], x[2], i) for i, x in enumerate(ans)]
    return last_bake_groups


class EZB_OT_new_bake_group(bpy.types.Operator):
    """Bake groups are created by searching the scene for objects or collections that match the naming patterns in the settings panel.
So you need Collections or Objects already created. 
e.g. "test_low" and "test_high" objects"""
    bl_idname = "ezb.new_bake_group"
    bl_label = "New Bake Group"

    name: bpy.props.EnumProperty(items=get_possible_bake_groups_enums)

    @classmethod
    def poll(cls, context):
        ezb_settings = bpy.context.scene.EZB_Settings
        return True

    def execute(self, context):
        baker = bpy.context.scene.EZB_Settings.bakers[bpy.context.scene.EZB_Settings.baker_index]
        new_bake_group = baker.bake_groups.add()
        index = len(baker.bake_groups) - 1
        baker.bake_group_index = index
        group, name = self.name.split('___')
        new_bake_group.key = name
        new_bake_group.mode_group = group
        return {'FINISHED'}


class EZB_OT_create_possible_bake_groups(bpy.types.Operator):
    """Create all possible bake groups"""
    bl_idname = "ezb.create_possible_bake_groups"
    bl_label = "Create Bake Groups"

    gather_from: bpy.props.EnumProperty(
        items=[
            ('SELECTION', 'From Selection', 'Add all posible bake groups from the selected objects'),
            ('SCENE', 'From Scene', 'Add all posible bake groups from the current scene'),
        ]
    )

    @classmethod
    def poll(cls, context):
        ezb_settings = bpy.context.scene.EZB_Settings
        return True

    def execute(self, context):
        baker = bpy.context.scene.EZB_Settings.bakers[bpy.context.scene.EZB_Settings.baker_index]
        if self.gather_from == 'SELECTION':
            possible_bake_groups = get_possible_bake_groups([x for x in bpy.context.scene.objects if x.select_get()])
        elif self.gather_from == 'SCENE':
            possible_bake_groups = get_possible_bake_groups(bpy.context.scene.objects)
        for name, group, icon in possible_bake_groups:
            new_bake_group = baker.bake_groups.add()
            new_bake_group.key = name
            new_bake_group.mode_group = group

        index = len(baker.bake_groups) - 1
        baker.bake_group_index = index

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

        baker.bake_groups[baker.bake_group_index].preview_cage = False
        baker.bake_groups.remove(baker.bake_group_index)

        if baker.bake_group_index >= len(baker.bake_groups):
            baker.bake_group_index = len(baker.bake_groups) - 1
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
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
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
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
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
        if not (bpy.context.scene.EZB_Settings.baker_index >= 0 and len(bpy.context.scene.EZB_Settings.bakers) > bpy.context.scene.EZB_Settings.baker_index):
            return 'No baker selected'
        baker = bpy.context.scene.EZB_Settings.bakers[bpy.context.scene.EZB_Settings.baker_index]
        device = baker.child_device
        ans = baker.check_for_errors()
        if ans:
            return ans
        ans = device.check_for_errors()
        if ans:
            return ans
        return 'Bake'

    @classmethod
    def poll(cls, context):
        if not (bpy.context.scene.EZB_Settings.baker_index >= 0 and len(bpy.context.scene.EZB_Settings.bakers) > bpy.context.scene.EZB_Settings.baker_index):
            return False
        baker = bpy.context.scene.EZB_Settings.bakers[bpy.context.scene.EZB_Settings.baker_index]
        device = baker.child_device
        ans = baker.check_for_errors()
        if ans:
            return False
        ans = device.check_for_errors()
        if ans:
            return False
        return True

    def execute(self, context):
        baker = bpy.context.scene.EZB_Settings.bakers[bpy.context.scene.EZB_Settings.baker_index]
        baker.bake()
        return {'FINISHED'}


class EZB_OT_cancel_bake(bpy.types.Operator):
    """Cancel Bake"""
    bl_idname = "ezb.cancel_bake"
    bl_label = "Cancel Bake"

    @classmethod
    def poll(cls, context):
        if not (bpy.context.scene.EZB_Settings.baker_index >= 0 and len(bpy.context.scene.EZB_Settings.bakers) > bpy.context.scene.EZB_Settings.baker_index):
            return False
        return True

    def execute(self, context):
        baker = bpy.context.scene.EZB_Settings.bakers[bpy.context.scene.EZB_Settings.baker_index]
        baker.cancel_current_bake = True
        baker.is_baking = False
        return {'FINISHED'}


last_maps = None


def get_possible_maps(self, context):
    baker = bpy.context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
    device = baker.child_device
    global last_maps
    ordered_maps = {}
    for i, x in enumerate(device.get_inactive_maps()):
        if x.category not in ordered_maps:
            ordered_maps[x.category] = set()
        ordered_maps[x.category].add((x.id, x.label, x.label, x.icon, i + 1))
    last_maps = []
    for category in sorted([x for x in ordered_maps.keys()]):
        maps = ordered_maps[category]
        last_maps.append(("", category, "description", "NONE", 0))
        for map in maps:
            last_maps.append(map)

    return last_maps


class EZB_OT_add_map(bpy.types.Operator):
    """Add Map"""
    bl_idname = "ezb.add_map"
    bl_label = "Add Map"

    map: bpy.props.EnumProperty(items=get_possible_maps)

    def execute(self, context):
        baker = bpy.context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        device = baker.child_device
        map = getattr(device.maps, self.map)
        map.active = True
        map.show_info = True
        return {'FINISHED'}


class EZB_OT_show_image(bpy.types.Operator):
    """Show Image"""
    bl_idname = "ezb.show_image"
    bl_label = "Show Image"

    image: bpy.props.StringProperty()

    def execute(self, context):
        image = bpy.data.images.get(self.image)
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'IMAGE_EDITOR':
                    area.spaces.active.image = image
                    return {'FINISHED'}
        return {'FINISHED'}

# for not storing the undo step, but it can crash blender, so it's not being used


class EZB_OT_show_cage(bpy.types.Operator):
    """Show/Hide Cage"""
    bl_idname = "ezb.show_cage"
    bl_label = "Show Cage"
    bl_options = {'INTERNAL'}

    index: bpy.props.IntProperty()

    def execute(self, context):
        baker = bpy.context.scene.EZB_Settings.bakers[bpy.context.scene.EZB_Settings.baker_index]
        bg = baker.bake_groups[self.index]
        bg.preview_cage = not bg.preview_cage

        bake_group.update_cage(bg, context)
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
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')
        if obj:
            obj.select_set(True)
        return {'FINISHED'}


class EZB_OT_edit_bake_groups(bpy.types.Operator):
    """Edit selected bake groups"""
    bl_idname = "ezb.edit_bake_groups"
    bl_label = "Edit Selected Bake Groups"

    def update_cage(self, context):
        baker = bpy.context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        for x in baker.bake_groups:
            if any(y.select_get() for y in x.objects_high) or any(y.select_get() for y in x.objects_low):
                x.cage_displacement = self.cage_displacement

    def update_cage_visible(self, context):
        baker = bpy.context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        for x in baker.bake_groups:
            if any(y.select_get() for y in x.objects_high) or any(y.select_get() for y in x.objects_low):
                x.preview_cage = self.preview_cage

    cage_displacement: bpy.props.FloatProperty(name='Cage Displacement', default=0.05, step=0.1, precision=3, update=update_cage)
    preview_cage: bpy.props.BoolProperty(update=update_cage_visible, default=True)

    @classmethod
    def poll(cls, context):
        if not context.selected_objects:
            return False
        return True

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.prop(
            self,
            'preview_cage',
            text='',
            icon="HIDE_OFF" if self.preview_cage else "HIDE_ON",
            icon_only=True,
            emboss=False
        )
        row.prop(self, 'cage_displacement')

    def invoke(self, context, event):
        wm = context.window_manager
        self.preview_cage = True
        return wm.invoke_props_dialog(self)

    def execute(self, context):

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
    EZB_OT_cancel_bake,
    EZB_OT_show_image,
    EZB_OT_select_texture_size,
    EZB_OT_select_object,
    EZB_OT_create_possible_bake_groups,
    EZB_OT_show_cage,
    EZB_OT_edit_bake_groups,
]


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
