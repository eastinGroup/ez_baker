import bpy

from .blender import EZB_Device_Blender
from .handplane import EZB_Device_Handplane

devices = [EZB_Device_Blender, EZB_Device_Handplane]

device_annotations = {}
for x in devices:
    device_annotations[x.name] = (bpy.props.PointerProperty, {'type': x})

EZB_Devices = type("EZB_Devices", (bpy.types.PropertyGroup,), {'__annotations__': device_annotations})

classes = devices + [EZB_Devices]

def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
