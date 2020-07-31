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

    def bake(self, baker):
        pass
