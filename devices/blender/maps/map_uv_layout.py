import bpy
import os
from .map import EZB_Map_Blender


# TODO: Blender Foundation\Blender 2.83\2.83\scripts\addons\io_mesh_uv_layout
# not working in background mode
"""
class EZB_Map_Uv_Layout(bpy.types.PropertyGroup, EZB_Map_Blender):
    id = 'UV_LAYOUT'
    pass_name = 'EMIT'
    label = 'UV Layout'
    icon = 'GROUP_UVS'
    category = 'Mesh'
    suffix: bpy.props.StringProperty(default='_UVL')

    color_space = 'Non-Color'

    def do_bake(self):
        '''Starts the bake process'''
        for group in self.parent_baker.bake_groups:
            group.setup_settings()
            low = group.objects_low

            materials_dict = {}

            for x in low:
                bpy.context.view_layer.objects.active = x
                bpy.ops.object.mode_set(mode="EDIT")
                for i, mat_slot in enumerate(x.material_slots):
                    if mat_slot.material not in materials_dict:
                        materials_dict[mat_slot.material] = []
                    file_path = self.get_export_path(x.name + '_' + mat_slot.material.name)
                    materials_dict[mat_slot.material].append(file_path)
                    bpy.ops.mesh.select_all(action='DESELECT')
                    x.active_material_index = i
                    bpy.ops.object.material_slot_select()
                    bpy.ops.uv.export_layout(filepath=file_path, export_all=False, modified=False, mode='PNG', size=(self.parent_baker.width, self.parent_baker.height), opacity=0, check_existing=False)

                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode="OBJECT")

            temp_images = []
            for mat, image_paths in materials_dict.items():
                pixels = [0.0] * self.parent_baker.width * self.parent_baker.height * 4
                for image_path in image_paths:
                    temp_img = bpy.data.images.new('temp', width=self.parent_baker.width, height=self.parent_baker.height)
                    temp_img.source = 'FILE'
                    temp_img.filepath = image_path
                    temp_img.reload()

                    temp_pixels = list(temp_img.pixels)
                    for i in range(0, len(pixels)):
                        if (i + 1) % 4 == 0:
                            pixels[i] = max(pixels[i], temp_pixels[i])
                        else:
                            pixels[i] = min(pixels[i], temp_pixels[i])
                    temp_images.append(temp_img)
                final_image = self.get_image(mat)
                final_image.pixels = pixels

            for x in temp_images:
                os.remove(x.filepath)
                bpy.data.images.remove(x, do_unlink=True)

        self.postprocess_images()
"""
