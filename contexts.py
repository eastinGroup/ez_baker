import bpy
from . utilities import traverse_tree
from . utilities import log


class Custom_Render_Settings():
    def __init__(self, scene):
        self.scene = scene

    def collect_attributes(self, obj):
        return {x.identifier: getattr(obj, x.identifier) for x in obj.bl_rna.properties if not x.is_readonly}

    def __enter__(self):
        self.bake = self.collect_attributes(self.scene.render.bake)
        self.view_settings = self.collect_attributes(self.scene.view_settings)
        self.image_settings = self.collect_attributes(self.scene.render.image_settings)
        self.render = self.collect_attributes(self.scene.render)
        self.cycles = self.collect_attributes(self.scene.cycles)

    def restore_attributes(self, obj, orig_attribs):
        for id, value in orig_attribs.items():
            setattr(obj, id, value)

    def __exit__(self, type, value, traceback):
        self.restore_attributes(self.scene.view_settings, self.view_settings)
        self.restore_attributes(self.scene.render.image_settings, self.image_settings)
        self.restore_attributes(self.scene.render, self.render)
        self.restore_attributes(self.scene.cycles, self.cycles)
        self.restore_attributes(self.scene.render.bake, self.bake)
