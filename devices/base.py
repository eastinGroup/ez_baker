import bpy

class EZB_Device:
    name = "Default"

    def draw(self, layout, context):
        pass

    def get_active_maps(self):
        for bake_map in self.maps.maps:
            map = getattr(self.maps, bake_map.id)
            if map.active:
                yield map

    def get_bakeable_maps(self):
        for bake_map in self.maps.maps:
            map = getattr(self.maps, bake_map.id)
            if map.active and map.bake:
                yield map


    def get_all_maps(self):
        for bake_map in self.maps.maps:
            map = getattr(self.maps, bake_map.id)
            yield map


    def get_inactive_maps(self):
        for bake_map in self.maps.maps:
            map = getattr(self.maps, bake_map.id)
            if not map.active:
                yield map

    @property
    def parent_baker(self):
        for x in bpy.context.scene.EZB_Settings.bakers:
            if x.child_device == self:
                return x
        return None

    def bake(self, baker):
        pass


    def check_for_errors(self):
        if not any(True for x in self.get_bakeable_maps()):
            return 'No maps to bake. Add a map with the "add map" dropdown. And make sure at least one of the maps is marked to be baked (eye icon)'
        return None
