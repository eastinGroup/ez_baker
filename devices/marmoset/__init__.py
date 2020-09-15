import os
import subprocess
import bpy
import threading
import queue
from multiprocessing.connection import Listener

from ..device import EZB_Device
from ...utilities import log
from ...settings import file_formats_enum_marmoset
from . import maps


class EZB_OT_run_marmoset_background(bpy.types.Operator):
    """Updates UI based on marmoset progress"""
    bl_idname = "ezb.run_marmoset_background"
    bl_label = "Updates UI with marmoset information"

    baker_scene: bpy.props.StringProperty()
    baker_datapath: bpy.props.StringProperty()
    device_datapath: bpy.props.StringProperty()

    _timer = None
    th = None
    prog = 0
    stop_early = False

    @property
    def baker(self):
        return bpy.data.scenes[self.baker_scene].path_resolve(self.baker_datapath)

    @property
    def device(self):
        return bpy.data.scenes[self.baker_scene].path_resolve(self.device_datapath)

    def redraw_region(self, context):
        for region in context.area.regions:
            if region.type == "UI":
                region.tag_redraw()

    def modal(self, context, event):
        if self.baker.cancel_current_bake:
            self.cancel(context)

            self.process.terminate()
            print('MODAL CANCELLED')
            self.device.bake_cancelled()
            return {'CANCELLED'}

        if event.type == 'TIMER':
            try:
                msg = self.messages.get_nowait()

                if msg[0] == 'BAKED':
                    self.device.texture_baked(msg[1][0], msg[1][1], msg[1][2])
                if msg[0] == 'WORKING':
                    self.baker.baking_map_name = msg[1]
                    self.current_bake += 1
                    self.baker.baked_maps += 1
                    self.baker.current_baking_progress = float(self.current_bake) / self.total_bakes
                if msg[0] == 'INFO':
                    self.baker.baking_map_name = msg[1]

                self.redraw_region(context)

                print(f'received: {msg}')
            except queue.Empty:
                pass
            if self.process.poll() is not None and self.messages.empty():

                print('MODAL FINISHED')
                self.device.bake_finish()
                self.redraw_region(context)
                return {'FINISHED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        import subprocess

        self.process = subprocess.Popen(self.device.get_commandline_argument())
        self.total_bakes = len(list(self.device.get_active_maps()))
        self.current_bake = -1

        address = ('localhost', 1605)
        listener = Listener(address, authkey=bytes('ezbaker', encoding='utf8'))
        listener._listener._socket.settimeout(3)
        connection = listener.accept()
        print(f'connection accepted from {listener.last_accepted}')

        export_folder = self.baker.get_abs_export_path()

        meshes_folder = os.path.join(export_folder, 'meshes')
        os.makedirs(meshes_folder, exist_ok=True)

        bake_groups = {}
        for bake_group in self.baker.bake_groups:
            bake_group_dict = {}
            bake_group_dict['high'] = []
            bake_group_dict['low'] = []
            bake_group_dict['cage_displacement'] = bake_group.cage_displacement
            # high
            models = bake_group.objects_high
            for model in models:
                name = model.name
                bake_group_dict['high'].append(export_obj(meshes_folder, model, name, t_space=False, modifiers=True))
            models = bake_group.objects_low
            for model in models:
                name = model.name
                obj_path = export_obj(meshes_folder, model, name, t_space=False, modifiers=True)
                cage_path = ''
                bake_group_dict['low'].append((obj_path, cage_path))

            bake_groups[bake_group.key] = bake_group_dict

        maps = {}
        for map in self.device.get_bakeable_maps():
            map_info = {}
            suffix = map.suffix
            if suffix.startswith('_'):
                suffix = suffix[1:]
            map_info['suffix'] = suffix

            for setting in map.settings_to_copy:
                map_info[setting] = getattr(map, setting)

            maps[map.id] = map_info

        # send data to bake

        path = os.path.join(self.baker.get_abs_export_path(), self.baker.key + file_formats_enum_marmoset[self.device.image_format])
        path = path.replace('\\', '/')
        baker_info = {
            'name': self.baker.key,
            'outputPath': path,
            'outputBits': int(self.baker.color_depth),
            'outputHeight': self.baker.height,
            'outputWidth': self.baker.width,
            'outputSamples': self.baker.get_supersampling * self.baker.get_supersampling,
            'edgePaddingSize': self.baker.padding,
            'multipleTextureSets': self.device.multipleTextureSets,
            'smoothCage': self.device.smoothCage,
            'ignoreTransforms': self.device.ignoreTransforms,
            'ignoreBackfaces': self.device.ignoreBackfaces,
            'fixMirroredTangents': self.device.fixMirroredTangents,
            'tangentSpace': self.device.tangentSpace,
            'outputSoften': self.device.outputSoften,
        }

        connection.send(baker_info)
        connection.send(bake_groups)
        connection.send(maps)

        self.messages = queue.Queue()

        def receive_messages(connection, messages):
            while True:
                try:
                    msg = connection.recv()
                    print(msg)
                    messages.put(msg)
                except EOFError:
                    print('Connection Ended')
                    break
                except ConnectionResetError:
                    print('Connection Ended')
                    break

        self.server_thread = threading.Thread(target=receive_messages, args=(connection, self.messages))
        self.server_thread.start()

        listener.close()

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


def export_obj(meshes_folder, obj, name, t_space, modifiers):
    mesh_filepath = os.path.join(meshes_folder, name + '.fbx')

    ctx = bpy.context.copy()
    ctx['selected_objects'] = [obj]

    bpy.ops.export_scene.fbx(
        ctx,
        filepath=mesh_filepath,
        use_selection=True,
        use_active_collection=False,
        global_scale=1,
        apply_unit_scale=False,
        apply_scale_options='FBX_SCALE_NONE',
        axis_forward='-Z',
        axis_up='Y',
        object_types={'EMPTY', 'MESH', 'OTHER', 'ARMATURE'},
        bake_space_transform=False,
        use_custom_props=False,
        path_mode='STRIP',
        batch_mode='OFF',
        use_mesh_modifiers=modifiers,
        use_mesh_modifiers_render=modifiers,
        mesh_smooth_type='FACE',
        use_mesh_edges=False,
        use_tspace=t_space,
        use_armature_deform_only=False,
        add_leaf_bones=False,
        primary_bone_axis='-Y',
        secondary_bone_axis='X',
        armature_nodetype='NULL',
        bake_anim=False,
        bake_anim_use_all_bones=False,
        bake_anim_use_nla_strips=False,
        bake_anim_use_all_actions=False,
        bake_anim_force_startend_keying=False,
        bake_anim_step=1,
        bake_anim_simplify_factor=1
    )

    return mesh_filepath


class EZB_Device_Marmoset(bpy.types.PropertyGroup, EZB_Device):
    name = "marmoset"
    maps: bpy.props.PointerProperty(type=maps.EZB_Maps_Marmoset)

    smoothCage: bpy.props.BoolProperty(default=True, name='Smooth Cage', description='Smooths low poly cage normals for baking purposes')
    ignoreTransforms: bpy.props.BoolProperty(default=False, name='Ignore Transforms', description='Mesh transforms, such as rotation and position will be ignored for the purpose of baking')
    ignoreBackfaces: bpy.props.BoolProperty(default=True, name='Ignore Back Faces', description='Ignores the back sides if triangles on the high-poly mesh when baking')
    fixMirroredTangents: bpy.props.BoolProperty(default=False, name='Fix Mirrored Tangents', description='Attempts to fix any issues arising from mirrored tangents in low poly meshes')
    tangentSpace: bpy.props.EnumProperty(
        items=[
            ('Mikk', 'Mikk / xNormal', ''),
            ('Marmoset', 'Marmoset', ''),
            ('Maya', 'Maya', ''),
            ('3D Studio Max', '3D Studio Max', ''),
            ('Unity', 'Unity 4.x', ''),
        ],
        name='Tangent Space',
        description='Selects a tangent-space convention for all low-poly meshes'
    )
    outputSoften: bpy.props.FloatProperty(
        default=0.0,
        name='Soften',
        description='Applies a softening filter to the baked surface. This might be useful for smoothing borders around floaters or other hard edges',
        min=0.0,
        max=1.0,
        subtype='FACTOR'
    )

    multipleTextureSets: bpy.props.BoolProperty(
        default=False,
        name='Multiple Texture Sets',
        description='Creates separate textures for each material it finds in the low poly objects\n(Not supported right now due to limitations in the python API)'
    )

    image_format: bpy.props.EnumProperty(
        items=[
            ('TGA', 'TGA', 'Export images as .tga'),
            ('PNG', 'PNG', 'Export images as .png'),
        ],
        default='PNG',
        name='Format'
    )

    use_low_to_low = False

    def draw(self, layout, context):

        row = layout.row()
        row.prop(self, 'multipleTextureSets')
        row.enabled = False
        layout.prop(self, 'smoothCage')
        layout.prop(self, 'ignoreTransforms')
        layout.prop(self, 'ignoreBackfaces')
        layout.prop(self, 'fixMirroredTangents')

        layout.prop(self, 'outputSoften')
        layout.prop(self, 'tangentSpace')
        layout.separator()
        layout.label(text='Custom cages not supported in Marmoset due to API limitations')

    def get_commandline_argument(self):
        prefs = bpy.context.preferences.addons[__package__.split('.')[0]].preferences

        # bake with handplane
        marmoset_cmd = os.path.join(prefs.marmoset_path, 'toolbag.exe')
        communication_scripts = os.path.join(os.path.split(__file__)[0], 'marmoset_comm.py')
        commands = [marmoset_cmd, '-hide', communication_scripts]

        return commands

    def texture_baked(self, map_id, material_name, image_path):
        if self.parent_baker.load_images:
            map = next(x for x in self.get_all_maps() if x.id == map_id)

            img = self.parent_baker.get_image(map, material_name)
            img.image.source = 'FILE'
            img.image.filepath = image_path
            img.image.reload()

    def bake_local(self):
        self.bake_multithread()

    def bake_multithread(self):
        bpy.ops.ezb.run_marmoset_background(
            baker_scene=self.parent_baker.id_data.name,
            baker_datapath=self.parent_baker.path_from_id(),
            device_datapath=self.path_from_id()
        )

    def check_for_errors(self, context):
        ans = super().check_for_errors(context)
        if ans:
            return ans

        prefs = bpy.context.preferences.addons[__package__.split('.')[0]].preferences

        if not prefs.marmoset_path:
            return 'No Marmoset path set in the addon preferences'

        marmoset_path = os.path.join(prefs.marmoset_path, 'toolbag.exe')

        if not os.path.isfile(marmoset_path):
            return 'Marmoset path in the addon preferences is incorrect'

        return None

    def show_progress(self):
        return f'Baking... {max(0, self.parent_baker.baked_maps)}/{self.parent_baker.total_maps_to_bake}'


classes = [EZB_OT_run_marmoset_background, EZB_Device_Marmoset]


def register():
    from bpy.utils import register_class

    maps.register()

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    maps.unregister()

    for cls in reversed(classes):
        unregister_class(cls)
