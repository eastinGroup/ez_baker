import bpy
import textwrap

from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
    PointerProperty,
)

from .settings import mode_group_types, devices_enum
from . import outputs
from . import baker
from . import bake_group
from . import operators
from . import devices
from . import handlers
from .addon_updater import ops

open_folder_icon = 'FILE_FOLDER'
if bpy.app.version >= (2, 83, 0):
    open_folder_icon = 'FOLDER_REDIRECT'

is_baking = False


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
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=False)
        col.use_property_split = True
        col.use_property_decorate = False  # No animation.

        col.prop(context.scene.EZB_Settings, "suffix_high", text="High")
        col.prop(context.scene.EZB_Settings, "suffix_low", text="Low")
        col.prop(context.scene.EZB_Settings, "suffix_cage", text="Cage")


class EZB_UL_preview_group_objects(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        sub_row = layout.row()
        sub_row.operator('ezb.select_object', text='', icon='RESTRICT_SELECT_OFF').name = item.name
        sub_row.label(text=item.name, icon='MESH_CUBE')


class EZB_UL_preview_group_objects_low(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        sub_row = layout.row()
        sub_row.operator('ezb.select_object', text='', icon='RESTRICT_SELECT_OFF').name = item.name
        sub_row.label(text=item.name, icon='MESH_CUBE')
        if item.cage:
            sub_row.operator('ezb.select_object', text='', icon='SELECT_SET').name = item.cage
        else:
            sub_row.operator('ezb.create_custom_cage', text='', icon='ADD').name = item.name


class EZB_UL_bakers(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.prop(item, 'key', text='', icon=next(x[3] for x in devices_enum if x[0] == item.device_type), emboss=False)


class EZB_UL_bake_groups(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        icon = next(x[3] for x in mode_group_types if x[0] == item.mode_group)

        selected = any(y.select_get() for y in item.objects_high) or any(y.select_get() for y in item.objects_low)
        selected_icon = 'RESTRICT_SELECT_ON' if not selected else 'RESTRICT_SELECT_OFF'

        row.label(text='', icon=selected_icon)
        row.prop(item, 'key', text='', icon=icon, emboss=False)

        high_objs = item.objects_high
        low_objs = item.objects_low
        if not data.child_device.use_low_to_low:
            row.operator('ezb.show_high_objects', text='High: {}'.format(len(high_objs)), emboss=False).index = index
        row.operator('ezb.show_low_objects', text='Low: {}'.format(len(low_objs)), emboss=False).index = index

        if not data.child_device.use_low_to_low:
            row.prop(
                item,
                'preview_cage',
                text='cage',
                icon="HIDE_OFF" if item.preview_cage else "HIDE_ON",
                icon_only=True,
                emboss=False
            )


class EZB_PT_baker_panel(bpy.types.Panel):
    bl_idname = "EZB_PT_baker_panel"
    bl_label = "Bakers"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "EZ Baker"

    def draw(self, context):
        ops.check_for_update_background()
        ops.update_notice_box_ui(self, context)

        layout = self.layout

        ezb_settings = context.scene.EZB_Settings

        bakers = [x for x in ezb_settings.bakers]

        main_col = layout.column(align=True)
        row = main_col.row(align=True)

        row.template_list("EZB_UL_bakers", "", ezb_settings, "bakers", ezb_settings, "baker_index", rows=2)
        col = row.column(align=True)
        col.operator('ezb.new_baker', text='', icon='ADD')
        col.operator('ezb.remove_baker', text='', icon='REMOVE')

        row = main_col.split(factor=0.8, align=True)
        #split=row.split(factor=0.75, align=True)
        row.scale_y = 1.5

        baker = None
        if (context.scene.EZB_Settings.baker_index < len(context.scene.EZB_Settings.bakers) and len(context.scene.EZB_Settings.bakers) > 0):
            baker = context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        rub_row = row.row(align=True)
        bake_button_text = 'Bake'
        if baker and baker.is_baking:
            rub_row.operator('ezb.cancel_bake', text='', icon='X')
            bake_button_text = baker.child_device.show_progress()
        bake_op = rub_row.operator('ezb.bake', text=bake_button_text, icon='IMPORT')

        path = ''
        row = row.row(align=True)
        row.enabled = False
        if baker:
            row.enabled = bool(baker.path)
            path = baker.path

        row.operator("wm.path_open", text="Open", icon=open_folder_icon).filepath = path

        if baker and baker.is_baking:
            layout.label(text=f'Baking: {baker.baking_map_name}...')

            row = layout.row()
            row.enabled = False

        if False:
            tooltip = operators.EZB_OT_bake.description(context, bake_op)
            if tooltip != 'Bake':
                text_wrap = textwrap.TextWrapper(width=50)  # 50 = maximum length
                text_list = text_wrap.wrap(text=tooltip)

                # Now in the panel:
                for text in text_list:
                    row = layout.row(align=True)
                    row.alignment = 'CENTER'
                    row.label(text=text)


class EZB_PT_baker_settings_panel(bpy.types.Panel):
    bl_idname = "EZB_PT_baker_settings_panel"
    bl_label = "Settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "EZ Baker"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "EZB_PT_baker_panel"

    def draw(self, context):
        layout = self.layout
        ezb_settings = context.scene.EZB_Settings
        bakers = [x for x in ezb_settings.bakers]
        baker_index = context.scene.EZB_Settings.baker_index

        if not(context.scene.EZB_Settings.baker_index < len(bakers) and len(bakers) > 0):
            layout.label(text='Select or create a Baker in the "Bakers" panel')
            return
        baker = context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        layout.enabled = not baker.is_baking

        col = layout.column(align=False)

        baker.draw(col, context)


class EZB_PT_bake_groups_panel(bpy.types.Panel):
    bl_idname = "EZB_PT_bake_groups_panel"
    bl_label = "Bake Groups"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "EZ Baker"

    def draw(self, context):
        layout = self.layout

        ezb_settings = context.scene.EZB_Settings
        if not(context.scene.EZB_Settings.baker_index < len(ezb_settings.bakers) and len(ezb_settings.bakers) > 0):
            layout.label(text='Select or create a Baker in the "Bakers" panel')
            return
        baker = context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]

        #layout.enabled = not baker.is_baking

        col = layout.column(align=True)
        col.template_list("EZB_UL_bake_groups", "", baker, "bake_groups", baker, "bake_group_index", rows=2)
        row2 = col.row(align=True)
        row2.operator_menu_enum('ezb.create_possible_bake_groups', 'gather_from', text='', icon='IMPORT')
        row2.operator_menu_enum('ezb.new_bake_group', 'name', text='Add Bake Group', icon='ADD')
        row2.operator('ezb.remove_bake_group', text='', icon='REMOVE')

        if len(baker.bake_groups) > baker.bake_group_index and baker.bake_group_index >= 0:
            bake_group = baker.bake_groups[baker.bake_group_index]
            if not baker.child_device.use_low_to_low:
                col = layout.column(align=True)
                row = col.row(align=True)
                row.prop(
                    bake_group,
                    'preview_cage',
                    text='',
                    icon="HIDE_OFF" if bake_group.preview_cage else "HIDE_ON",
                    icon_only=True,
                    emboss=False
                )
                row.prop(bake_group, 'cage_displacement')
                row.operator('ezb.edit_bake_groups', text='', icon='SHADERFX')

                layout = layout.split(factor=0.5, align=True)
                layout.template_list(
                    "EZB_UL_preview_group_objects",
                    "",
                    ezb_settings,
                    "preview_group_objects_high",
                    ezb_settings,
                    "preview_group_objects_high_index",
                    rows=2,
                )
            layout.template_list(
                "EZB_UL_preview_group_objects_low",
                "",
                ezb_settings,
                "preview_group_objects_low",
                ezb_settings,
                "preview_group_objects_low_index",
                rows=2,
            )


class EZB_PT_maps_panel(bpy.types.Panel):
    bl_idname = "EZB_PT_maps_panel"
    bl_label = "Maps"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "EZ Baker"

    def draw(self, context):
        layout = self.layout

        ezb_settings = context.scene.EZB_Settings
        if not(context.scene.EZB_Settings.baker_index < len(ezb_settings.bakers) and len(ezb_settings.bakers) > 0):
            layout.label(text='Select or create a Baker in the "Bakers" panel')
            return
        baker = context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]
        col = layout.column(align=True)
        col.operator_menu_enum('ezb.add_map', 'map', text='Add Map', icon='ADD')
        baker.draw_maps(col, context)


class EZB_PT_output_panel(bpy.types.Panel):
    bl_idname = "EZB_PT_output_panel"
    bl_label = "Output"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "EZ Baker"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        ezb_settings = context.scene.EZB_Settings
        if not(context.scene.EZB_Settings.baker_index < len(ezb_settings.bakers) and len(ezb_settings.bakers) > 0):
            layout.label(text='Select or create a Baker in the "Bakers" panel')
            return

        baker = context.scene.EZB_Settings.bakers[context.scene.EZB_Settings.baker_index]

        if not baker.materials:
            layout.label(text='Bake in the "Bakers" panel to see the output images in this panel')
            return
        col = layout.column()
        for x in baker.materials:
            x.draw(col, context)


classes = [
    EZB_preview_group_object,
    EZB_Settings,
    EZB_UL_bakers,
    EZB_UL_bake_groups,
    EZB_PT_core_panel,
    EZB_PT_baker_panel,
    EZB_PT_baker_settings_panel,
    EZB_PT_bake_groups_panel,
    EZB_PT_maps_panel,
    EZB_PT_output_panel,
    EZB_UL_preview_group_objects,
    EZB_UL_preview_group_objects_low
]


def register():
    outputs.register()
    operators.register()
    devices.register()
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
    devices.unregister()
    outputs.unregister()
