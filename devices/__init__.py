from . import handplane
from . import blender
import bpy


devices = [blender.EZB_Device_Blender, handplane.EZB_Device_Handplane]

device_annotations = {}
for x in devices:
    device_annotations[x.name] = (bpy.props.PointerProperty, {'type': x})

EZB_Devices = type("EZB_Devices", (bpy.types.PropertyGroup,), {'__annotations__': device_annotations})

classes = [EZB_Devices]


def register():
    from bpy.utils import register_class

    blender.register()
    handplane.register()

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    blender.unregister()
    handplane.unregister()

    for cls in reversed(classes):
        unregister_class(cls)
