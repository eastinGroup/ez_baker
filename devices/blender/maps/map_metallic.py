import bpy
from .map import EZB_Map_Blender, Map_Context


class Map_Context_Property_Switcher(Map_Context):
    from_socket = 'Metallic'
    to_socket = 'Emission'
    set_value = None

    def create_material(self, material, from_input, to_input):
        if material in self.materials:
            return self.materials[material]
        new_material = material.copy()
        tree = new_material.node_tree
        bsdf_nodes = [x for x in tree.nodes if x.bl_rna.identifier == 'ShaderNodeBsdfPrincipled']

        for bsdf in bsdf_nodes:
            input = bsdf.inputs[from_input]
            new_input = bsdf.inputs[to_input]
            link = input.links[0] if input.links else None
            if link:
                tree.links.new(link.from_socket, new_input)
                tree.links.remove(link)
            else:
                if (type(new_input.default_value)) == (type(input.default_value)):
                    new_input.default_value = input.default_value
                else:
                    new_input.default_value = input.default_value, input.default_value, input.default_value, 1
            if self.set_value is not None:
                input.default_value = self.set_value

        self.materials[material] = new_material
        return new_material

    def __init__(self, map, high, low):
        super().__init__(map, high, low)

        self.materials = dict()
        if self.device.use_low_to_low:
            for mat_slot in low.material_slots:
                mat_slot.material = self.create_material(mat_slot.material, self.from_socket, self.to_socket)
        else:
            for obj in high:
                for mat_slot in obj.material_slots:
                    mat_slot.material = self.create_material(mat_slot.material, self.from_socket, self.to_socket)

    def __exit__(self, type, value, traceback):
        super().__exit__(type, value, traceback)

        for orig_mat, temp_mat in self.materials.items():
            bpy.data.materials.remove(temp_mat, do_unlink=True)


class Map_Context_Metallic(Map_Context_Property_Switcher):
    from_socket = 'Metallic'
    to_socket = 'Emission'


class EZB_Map_Metallic(bpy.types.PropertyGroup, EZB_Map_Blender):
    id = 'METALLIC'
    pass_name = 'EMIT'
    label = 'Metallic'
    icon = 'COLOR'
    category = 'Surface'

    suffix: bpy.props.StringProperty(default='_M')

    background_color = [0.0, 0.0, 0.0, 1.0]

    context = Map_Context_Metallic

    color_space = 'Non-Color'
