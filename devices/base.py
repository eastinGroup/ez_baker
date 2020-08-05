import bpy

class EZB_Device:
    name = "Default"

    def draw(self, layout, context):
        pass

    def get_active_maps(self):
        ans = []
        for bake_map in self.maps.maps:
            map = getattr(self.maps, bake_map.id)
            if map.active:
                ans.append(map)

        return ans

    def get_all_maps(self):
        ans = []
        for bake_map in self.maps.maps:
            map = getattr(self.maps, bake_map.id)
            ans.append(map)

        return ans

    def bake(self, baker):
        pass

    def check_for_errors(self):
        if not any(getattr(self.maps, x.id).active for x in self.maps.maps):
            return 'No maps to bake. Add a map with the "add map" dropdown'
        return None
