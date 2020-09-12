import bpy
import os
from .map import EZB_Map_Blender

try:
    import PIL

    from PIL import Image, ImageDraw

    class EZB_Map_Uv_Layout(bpy.types.PropertyGroup, EZB_Map_Blender):
        id = 'UV_LAYOUT'
        pass_name = 'EMIT'
        label = 'UV Layout'
        icon = 'GROUP_UVS'
        category = 'Mesh'
        suffix: bpy.props.StringProperty(default='_UVL')

        color_space = 'Non-Color'

        def iter_polygon_data_to_draw(self, objects, material):
            for obj in objects:
                uv_layer = obj.data.uv_layers.active.data
                for polygon in obj.data.polygons:
                    if obj.material_slots[polygon.material_index].material == material:
                        start = polygon.loop_start
                        end = start + polygon.loop_total
                        uvs = tuple(tuple(uv.uv) for uv in uv_layer[start:end])
                        yield uvs

        def draw_lines(self, image, imagedraw, poligon_uvs):
            coords = []
            width, height = image.size
            for i in range(len(poligon_uvs)):
                start = poligon_uvs[i]
                end = poligon_uvs[(i + 1) % len(poligon_uvs)]
                coords.append((start[0] * width, start[1] * height))
                coords.append((end[0] * width, end[1] * height))

            for i in range(0, len(coords)):
                coord1 = coords[i]
                coord2 = coords[(i + 1) % len(coords)]
                imagedraw.line([coord1, coord2], width=1)

            # PIL draw

        def do_bake(self):
            '''Starts the bake process'''
            self.pre_bake()
            materials_dict = {}

            for group in self.parent_baker.bake_groups:
                group.setup_settings()
                low = group.objects_low

                for x in low:
                    bpy.context.view_layer.objects.active = x
                    bpy.ops.object.mode_set(mode="EDIT")
                    for mat_slot in x.material_slots:
                        if mat_slot.material not in materials_dict:
                            materials_dict[mat_slot.material] = []
                        materials_dict[mat_slot.material].append(x)

                    bpy.ops.mesh.select_all(action='DESELECT')
                    bpy.ops.object.mode_set(mode="OBJECT")

            for mat, objects in materials_dict.items():
                img = Image.new("RGB", (self.parent_baker.width * self.parent_baker.get_supersampling, self.parent_baker.height * self.parent_baker.get_supersampling))
                imagedraw = ImageDraw.Draw(img)
                pixels = []

                for uvs in self.iter_polygon_data_to_draw(objects, mat):
                    self.draw_lines(img, imagedraw, uvs)

                final_image = self.get_image(mat)

                print('image done')
                for pixel in iter(img.getdata()):
                    pixels.append(float(pixel[0]) / 255)
                    pixels.append(float(pixel[1]) / 255)
                    pixels.append(float(pixel[2]) / 255)
                    pixels.append(1.0)

                print('pixels created')

                final_image.pixels = pixels
                print('pixels set')
                final_image.pack()

            self.postprocess_images()
except ModuleNotFoundError:
    pass
