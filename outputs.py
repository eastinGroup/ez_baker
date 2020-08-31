import bpy


class EZB_Stored_Image(bpy.types.PropertyGroup):
    map_name: bpy.props.StringProperty()
    image: bpy.props.PointerProperty(type=bpy.types.Image)


class EZB_Stored_Material(bpy.types.PropertyGroup):
    """Stores all the images created by the baker, for easily previewing them and exporting"""
    material_name: bpy.props.StringProperty()
    images: bpy.props.CollectionProperty(type=EZB_Stored_Image)
    show_info: bpy.props.BoolProperty(default=True)

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
        if self.show_info:
            row = box.row()
            row.separator()
            col = row.column()
            for x in self.images:
                row = col.row()
                row.label(text='{}:'.format(x.map_name))
                row.operator('ezb.show_image', text='{}'.format(x.image.name), icon='FILE_IMAGE').image = x.image.name


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
