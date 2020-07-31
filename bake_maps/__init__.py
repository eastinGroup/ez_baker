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

def draw(layout, context, baker):
    col = layout.column()

    maps_to_draw = []
    for x in baker.get_device.maps.maps:
        map = getattr(baker.get_device.maps, x.id)
        if map.active:
            maps_to_draw.append(map)
    #maps_to_draw = sorted(maps_to_draw)
    for x in maps_to_draw:
        box = col.box()
        x.draw(box)