import bpy


def update_group_objects(scene):
    """Updates the low and high objects lists when the scene changes"""
    #print('UPDATING...')
    #bpy.app.handlers.depsgraph_update_post.remove(update_group_objects)

    if scene.EZB_Settings.baker_index >= 0 and scene.EZB_Settings.baker_index < len(scene.EZB_Settings.bakers) and len(scene.EZB_Settings.bakers) > 0:
        baker = scene.EZB_Settings.bakers[scene.EZB_Settings.baker_index]
        if len(baker.bake_groups) > baker.bake_group_index and baker.bake_group_index >= 0:
            bake_group = baker.bake_groups[baker.bake_group_index]

            scene.EZB_Settings.preview_group_objects_high.clear()
            scene.EZB_Settings.preview_group_objects_low.clear()
            
            for high in bake_group.objects_high:
                item = scene.EZB_Settings.preview_group_objects_high.add()
                item.name = high.name
                item.cage = ''
            for low in bake_group.objects_low:
                item = scene.EZB_Settings.preview_group_objects_low.add()
                item.name = low.name
                cage = scene.objects.get(low.name + scene.EZB_Settings.suffix_cage)
                item.cage = cage.name if cage else ''

def update_group_objects_on_index_change(self, context):
    update_group_objects(context.scene)

def register():
    bpy.app.handlers.depsgraph_update_post.append(update_group_objects)

def unregister():
    if update_group_objects in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(update_group_objects)
