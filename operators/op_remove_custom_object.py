import bpy
from ..handlers import update_group_objects


class EZB_OT_remove_custom_object(bpy.types.Operator):
    """Remove a custom object from a bake group"""
    bl_idname = "ezb.remove_custom_object"
    bl_label = "Remove Custom Object"

    scene: bpy.props.StringProperty()
    datapath: bpy.props.StringProperty()
    is_high: bpy.props.BoolProperty()
    index: bpy.props.IntProperty()

    def execute(self, context):
        scene = bpy.data.scenes.get(self.scene)
        bake_group = scene.path_resolve(self.datapath)
        collection = bake_group.custom_high if self.is_high else bake_group.custom_low
        collection.objects.remove(self.index)
        update_group_objects(scene)
        return {'FINISHED'}
