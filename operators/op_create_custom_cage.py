import bpy
from .. import handlers


class EZB_OT_create_custom_cage(bpy.types.Operator):
    """Creates custom cages for the selected objects"""
    bl_idname = "ezb.create_custom_cage"
    bl_label = "Create custom cage"
    bl_options = {'UNDO'}

    name: bpy.props.StringProperty()

    def execute(self, context):
        obj = context.scene.objects.get(self.name)
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.select_all(action='DESELECT')

        baker = context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        bake_group = baker.bake_groups[baker.bake_group_index]

        cage = bake_group.create_cage_from_object(obj, context)
        cage.name = self.name + context.scene.EZB_Settings.suffix_cage
        cage.data.name = cage.name
        cage.color = (1, 0, 0, 0.3)
        cage.display_type = 'SOLID'

        context.scene.collection.objects.link(cage)

        cage.select_set(True)
        context.view_layer.objects.active = cage
        bpy.ops.object.convert(target='MESH')

        handlers.update_group_objects(context.scene)

        return {'FINISHED'}
