from . import blender
from . import handplane

EZB_Maps_Blender = blender.EZB_Maps_Blender
EZB_Maps_Handplane = handplane.EZB_Maps_Handplane


def register():
    blender.register()
    handplane.register()


def unregister():
    blender.unregister()
    handplane.unregister()
