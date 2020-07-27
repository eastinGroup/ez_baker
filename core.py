import bpy

from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
    PointerProperty,
)

from .settings import mode_group_types
from . import bake_settings
from . import baker
from . import bake_group
from . import operators
from . import bake_maps
from . import handlers

class EZB_preview_group_object(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    cage: bpy.props.StringProperty()

class EZB_Settings(bpy.types.PropertyGroup):
    bakers: bpy.props.CollectionProperty(type=baker.EZB_Baker)
    baker_index: bpy.props.IntProperty(update=handlers.update_group_objects_on_index_change)

    suffix_high: bpy.props.StringProperty(default="_high")
    suffix_low: bpy.props.StringProperty(default="_low")
    suffix_cage: bpy.props.StringProperty(default="_cage")

    save_type: bpy.props.EnumProperty(items=[
        ('PACK', 'Internally', 'Pack images inside the .blend file'),
        ('EXTERNAL', 'Externally', 'Save images to an external file')
    ])

    preview_group_objects_high: bpy.props.CollectionProperty(type=EZB_preview_group_object)
    preview_group_objects_low: bpy.props.CollectionProperty(type=EZB_preview_group_object)

    preview_group_objects_high_index: bpy.props.IntProperty()
    preview_group_objects_low_index: bpy.props.IntProperty()


class EZB_PT_core_panel(bpy.types.Panel):
    bl_idname = "EZB_PT_core_panel"
    bl_label = "Settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "EZ Baker"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=False)
        col.use_property_split = True
        col.use_property_decorate = False  # No animation.

        col.prop(context.scene.EZB_Settings, "suffix_high", text="High")
        col.prop(context.scene.EZB_Settings, "suffix_low", text="Low")
        col.prop(context.scene.EZB_Settings, "suffix_cage", text="Cage")

        row = col.row()
        row.enabled=False
        row.prop(context.scene.EZB_Settings, "save_type", text="Save images")

        layout.template_image_settings(bpy.context.scene.render.image_settings, color_management=False)


class EZB_UL_preview_group_objects(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        sub_row = layout.row()
        sub_row.operator('ezb.select_object', text= '', icon='RESTRICT_SELECT_OFF').name = item.name
        sub_row.label(text=item.name)
        if item.cage:
            sub_row.operator('ezb.select_object', text= '', icon='SELECT_SET').name = item.cage

class EZB_UL_bakers(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.prop(item, 'key', text='', icon="RENDERLAYERS", emboss=False)


class EZB_UL_bake_groups(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        icon = next(x[3] for x in mode_group_types if x[0] == item.mode_group)
        row.prop(item, 'key', text='', icon=icon, emboss=False)
        high_objs = item.objects_high
        low_objs = item.objects_low
        row.operator('ezb.show_high_objects',text='High: {}'.format(len(high_objs)), emboss=False).index = index
        row.operator('ezb.show_low_objects',text='Low: {}'.format(len(low_objs)), emboss=False).index = index
        row.prop(
            item, 
            'preview_cage',
            text='cage',
            icon="HIDE_OFF" if item.preview_cage else "HIDE_ON",
            icon_only=True,
            emboss=False
            )


class EZB_PT_files_panel(bpy.types.Panel):
    bl_idname = "EZB_PT_files_panel"
    bl_label = "Bakers"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "EZ Baker"

    def draw(self, context):
        layout = self.layout

        ezb_settings = bpy.context.scene.EZB_Settings

        bakers = [x for x in ezb_settings.bakers]

        row = layout.row(align=False)

        row.template_list("EZB_UL_bakers", "", ezb_settings, "bakers", ezb_settings, "baker_index", rows=2)
        col=row.column(align=False)
        col.operator('ezb.new_baker',text='', icon='ADD')
        col.operator('ezb.remove_baker', text='', icon='REMOVE')

        baker_index = bpy.context.scene.EZB_Settings.baker_index

        if bpy.context.scene.EZB_Settings.baker_index < len(bakers) and len(bakers) > 0:
            baker = bpy.context.scene.EZB_Settings.bakers[bpy.context.scene.EZB_Settings.baker_index]
            baker.draw(layout, context)
            

        layout.separator()


class EZB_PT_bake_groups_panel(bpy.types.Panel):
    bl_idname = "EZB_PT_bake_groups_panel"
    bl_label = "Bake Groups"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "EZ Baker"

    def draw(self, context):
        layout = self.layout

        ezb_settings = bpy.context.scene.EZB_Settings
        if bpy.context.scene.EZB_Settings.baker_index < len(ezb_settings.bakers) and len(ezb_settings.bakers) > 0:
            baker = bpy.context.scene.EZB_Settings.bakers[bpy.context.scene.EZB_Settings.baker_index]

            col = layout.column(align=True)
            col.template_list("EZB_UL_bake_groups", "", baker, "bake_groups", baker, "bake_group_index", rows=2)
            row2 = col.row(align=True)
            row2.operator('ezb.create_possible_bake_groups', text='', icon='IMPORT')
            row2.operator_menu_enum('ezb.new_bake_group', 'name' ,text='Add Bake Group', icon='ADD')
            row2.operator('ezb.remove_bake_group', text='', icon='REMOVE')

            if len(baker.bake_groups) > baker.bake_group_index and baker.bake_group_index >= 0:
                bake_group = baker.bake_groups[baker.bake_group_index]
                bake_group.draw(layout, context)


class EZB_PT_maps_panel(bpy.types.Panel):
    bl_idname = "EZB_PT_maps_panel"
    bl_label = "Maps"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "EZ Baker"

    def draw(self, context):
        layout = self.layout

        ezb_settings = bpy.context.scene.EZB_Settings
        if bpy.context.scene.EZB_Settings.baker_index < len(ezb_settings.bakers) and len(ezb_settings.bakers) > 0:
            baker = bpy.context.scene.EZB_Settings.bakers[bpy.context.scene.EZB_Settings.baker_index]
            col = layout.column(align=True)
            col.operator_menu_enum('ezb.add_map', 'map', text='Add Map', icon='ADD')
            bake_maps.draw(col, context, baker)
        else:
            pass
            #layout.label(text='')


class EZB_PT_output_panel(bpy.types.Panel):
    bl_idname = "EZB_PT_output_panel"
    bl_label = "Output"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "EZ Baker"

    def draw(self, context):
        layout = self.layout

        ezb_settings = bpy.context.scene.EZB_Settings
        if bpy.context.scene.EZB_Settings.baker_index < len(ezb_settings.bakers) and len(ezb_settings.bakers) > 0:
            baker = bpy.context.scene.EZB_Settings.bakers[bpy.context.scene.EZB_Settings.baker_index]
            col = layout.column()
            for x in baker.materials:
                x.draw(col, context)


classes = [
    EZB_preview_group_object, 
    EZB_Settings, 
    EZB_UL_bakers,  
    EZB_UL_bake_groups, 
    EZB_PT_core_panel, 
    EZB_PT_files_panel, 
    EZB_PT_bake_groups_panel, 
    EZB_PT_maps_panel, 
    EZB_PT_output_panel,
    EZB_UL_preview_group_objects
]


def register():
    bake_settings.register()
    operators.register()
    bake_maps.register()
    bake_group.register()
    baker.register()
    
    
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.types.Scene.EZB_Settings = bpy.props.PointerProperty(type=EZB_Settings)

    handlers.register()


def unregister():
    from bpy.utils import unregister_class

    handlers.unregister()

    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.EZB_Settings

    
    baker.unregister()
    bake_group.unregister()
    operators.unregister()
    bake_maps.unregister()
    bake_settings.unregister()
