import bpy
from ..utilities import traverse_tree

last_bake_groups = None


def get_possible_bake_groups(objects, context):
    objects = objects[:]
    ezb_settings = context.scene.EZB_Settings
    baker = context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
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

    for x in traverse_tree(context.scene.collection, exclude_parent=True):
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
    ans = list(get_possible_bake_groups(context.scene.objects, context))
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
        return True

    def execute(self, context):
        baker = context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
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
        ezb_settings = context.scene.EZB_Settings
        return True

    def execute(self, context):
        baker = context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        if self.gather_from == 'SELECTION':
            possible_bake_groups = get_possible_bake_groups([x for x in context.scene.objects if x.select_get()], context)
        elif self.gather_from == 'SCENE':
            possible_bake_groups = get_possible_bake_groups(context.scene.objects, context)
        for name, group, icon in possible_bake_groups:
            new_bake_group = baker.bake_groups.add()
            new_bake_group.key = name
            new_bake_group.mode_group = group

        index = len(baker.bake_groups) - 1
        baker.bake_group_index = index

        return {'FINISHED'}
