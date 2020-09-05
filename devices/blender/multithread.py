import bpy

baker = bpy.context.scene.EZB_Settings.bakers[bpy.context.scene.EZB_Settings.baker_index]
baker['is_subprocess'] = True

baker.child_device.bake_local()
