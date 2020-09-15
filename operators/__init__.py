import bpy
import os
import importlib

tree = [x[:-3] for x in os.listdir(os.path.dirname(__file__)) if x.endswith('.py') and x != '__init__.py']

for i in tree:
    importlib.import_module('.' + i, package=__package__)

__globals = globals().copy()

classes = []

for num_id, x in enumerate([x for x in __globals if x.startswith('op_')]):
    for y in [item for item in dir(__globals[x]) if item.startswith('EZB_OT_')]:
        classes.append(getattr(__globals[x], y))


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
