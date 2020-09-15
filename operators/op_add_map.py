import bpy

last_maps = None


def get_possible_maps(self, context):
    baker = context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
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

        def sort_key(val):
            return val[1]
        for map in sorted(list(maps), key=sort_key):
            last_maps.append(map)

    return last_maps


class EZB_OT_add_map(bpy.types.Operator):
    """Add Map"""
    bl_idname = "ezb.add_map"
    bl_label = "Add Map"

    map: bpy.props.EnumProperty(items=get_possible_maps)

    def execute(self, context):
        baker = context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        device = baker.child_device
        map = getattr(device.maps, self.map)
        map.active = True
        map.show_info = True
        return {'FINISHED'}
