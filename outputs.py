import bpy


class EZB_Stored_Image(bpy.types.PropertyGroup):
    map_name: bpy.props.StringProperty()
    image: bpy.props.PointerProperty(type=bpy.types.Image)

    @property
    def parent_stored_material(self):
        path = self.path_from_id()
        parent_path = path.rsplit('.', 1)[0]
        return self.id_data.path_resolve(parent_path)

    def preview(self):
        self.parent_stored_material.setup_preview_material(self)


class EZB_Stored_Material(bpy.types.PropertyGroup):
    """Stores all the images created by the baker, for easily previewing them and exporting"""
    material_name: bpy.props.StringProperty()
    images: bpy.props.CollectionProperty(type=EZB_Stored_Image)
    show_info: bpy.props.BoolProperty(default=True)

    preview_material: bpy.props.PointerProperty(type=bpy.types.Material)
    original_material: bpy.props.PointerProperty(type=bpy.types.Material)

    def draw(self, layout, context):
        box = layout.box()
        row = box.row(align=True)
        row.prop(
            self,
            'show_info',
            icon="TRIA_DOWN" if self.show_info else "TRIA_RIGHT",
            icon_only=True,
            text='',
            emboss=False
        )
        row.label(text="{}".format(self.material_name), icon='MATERIAL')
        if self.preview_material:
            op = row.operator('ezb.clear_preview_image', text='Remove Preview', icon='X')
            op.scene = context.scene.name
            op.datapath = self.path_from_id()
        if self.show_info:
            row = box.row()
            row.separator()
            col = row.column()
            for x in self.images:
                row = col.row()
                row.label(text='{}:'.format(x.map_name))
                row.operator('ezb.show_image', text='{}'.format(x.image.name), icon='FILE_IMAGE').image = x.image.name
                op = row.operator('ezb.preview_image', text='', icon='VIS_SEL_11')
                op.scene = context.scene.name
                op.datapath = x.path_from_id()

    @property
    def parent_baker(self):
        path = self.path_from_id()
        parent_path = path.rsplit('.', 1)[0]
        return self.id_data.path_resolve(parent_path)

    def setup_preview_material(self, image_info):
        old_material = None
        if self.preview_material:
            old_material = self.preview_material
        else:
            self.original_material = bpy.data.materials.get(self.material_name)

        material_to_replace = old_material if old_material else self.original_material

        if not material_to_replace:
            return

        preview_material = bpy.data.materials.new(f'{self.material_name}_{image_info.map_name}_preview')
        preview_material.use_nodes = True
        image_node = preview_material.node_tree.nodes.new('ShaderNodeTexImage')
        image_node.image = image_info.image

        output = preview_material.node_tree.nodes['Material Output']
        preview_material.node_tree.links.new(image_node.outputs['Color'], output.inputs['Surface'])

        self.preview_material = preview_material

        for bake_group in self.parent_baker.bake_groups:
            for obj in bake_group.objects_low:
                for mat_slot in obj.material_slots:
                    if mat_slot.material and mat_slot.material == material_to_replace:
                        mat_slot.material = self.preview_material

        if old_material:
            bpy.data.materials.remove(old_material, do_unlink=True)

    def clear_preview_material(self):
        if not self.original_material:
            return
        for bake_group in self.parent_baker.bake_groups:
            for obj in bake_group.objects_low:
                for mat_slot in obj.material_slots:
                    if mat_slot.material and mat_slot.material == self.preview_material:
                        mat_slot.material = self.original_material
        self.original_material = None
        if self.preview_material:
            bpy.data.materials.remove(self.preview_material, do_unlink=True)


classes = [
    EZB_Stored_Image,
    EZB_Stored_Material,
]


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
