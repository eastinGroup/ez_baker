import bpy
import os
import importlib

from .map import EZB_Map


tree = [x[:-3] for x in os.listdir(os.path.dirname(__file__)) if x.endswith('.py') and x != '__init__.py']

for i in tree:
    importlib.import_module('.' + i, package=__package__)

__globals = globals().copy()

maps = []

for num_id, x in enumerate([x for x in __globals if x.startswith('map_')]):
    for y in [item for item in dir(__globals[x]) if item.startswith('EZB_Map_')]:
        maps.append(getattr(__globals[x], y))

map_annotations = {}
for x in maps:
    map_annotations[x.id] = (bpy.props.PointerProperty, {'type': x})

EZB_Maps = type("EZB_maps", (bpy.types.PropertyGroup,), {'__annotations__': map_annotations})

classes = maps + [EZB_Maps]

def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)


def draw(layout, context, baker):
    col = layout.column()

    maps_to_draw = []
    for x in maps:
        map = getattr(baker.maps, x.id)
        if map.active:
            maps_to_draw.append(map)
    #maps_to_draw = sorted(maps_to_draw)
    for x in maps_to_draw:
        box = col.box()
        x.draw(box)