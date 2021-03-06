import os
import sys
import subprocess
import bpy
import tempfile

from ..device import EZB_Device
from ...settings import file_formats_enum_handplane
from ...utilities import log
from . import maps
from .maps.map_normal import tangent_space_enum

map_names = [
    'normal_ts',
    'normal_os',
    'ao',
    'ao_floaters',
    'vert_color',
    'mat_psd',
    'mat_id',
    'curve',
    'vol_gradient',
    'cavity',
    'height',
    'tsao',
    'thickness'
]


class EZB_OT_run_handplane_background(bpy.types.Operator):
    """Updates UI based on handplane progress"""
    bl_idname = "ezb.run_handplane_background"
    bl_label = "Updates UI with handplane information"

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

            self.stop_early = True
            self.process.terminate()
            self.device.bake_cancelled()
            print('MODAL CANCELLED')
            self.redraw_region(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            # update progress widget here

            if self.process.poll() != None:
                print('MODAL FINISHED')
                self.device.bake_finish()
                self.redraw_region(context)
                return {'FINISHED'}
        self.redraw_region(context)
        return {'PASS_THROUGH'}

    def execute(self, context):
        import subprocess
        path, command_argument = self.device.get_commandline_argument()
        self.process = subprocess.Popen(command_argument, cwd=path)

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


def custom_write(file, line, tabs=0, end_line=True):
    ans = tabs * '\t'
    ans += line
    if end_line:
        ans += '\n'
    file.write(ans)


def write_value(file, type, name, value, tabs, end_line=True):
    line = type + ' '
    line += name + ' = '

    if type == 'bool':
        line += str.lower(str(value))
    elif type == 'String' or type == 'Filename':
        line += '"' + str(value) + '"'
    else:
        line += str(value)

    line += ';'
    custom_write(file, line, tabs, end_line)


class Write_Wrapper():
    def __init__(self, file, start_line, end_line, tabs=0, end=True):
        self.file = file
        self.start_line = start_line
        self.end_line = end_line
        self.tabs = tabs
        self.end = end

    def __enter__(self):
        custom_write(self.file, self.start_line, self.tabs, self.end)

    def __exit__(self, type, value, traceback):
        custom_write(self.file, self.end_line, self.tabs, self.end)


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
    if sys.platform == 'linux':
        mesh_filepath = 'z:'+mesh_filepath

    return mesh_filepath


class EZB_Device_Handplane(bpy.types.PropertyGroup, EZB_Device):
    name = "handplane"
    maps: bpy.props.PointerProperty(type=maps.EZB_Maps_Handplane)
    use_dither: bpy.props.BoolProperty(default=True)

    image_format: bpy.props.EnumProperty(
        items=[
            ('TGA', 'TGA', 'Export images as .tga'),
            ('PNG', 'PNG', 'Export images as .png'),
            ('TIF', 'TIFF', 'Export images as .tif'),
        ],
        default='PNG',
        name='Format'
    )

    use_low_to_low = False

    def draw(self, layout, context):
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(self, 'use_dither', text='Use Dither', expand=True)

    def write_handplane_file(self, baker):
        device = baker.child_device

        file_name = baker.key
        export_folder = baker.get_abs_export_path()
        if sys.platform == 'linux':
            export_folder = 'z:'+export_folder

        root_folder = os.path.join(baker.get_abs_export_path(), file_name)
        os.makedirs(root_folder, exist_ok=True)

        temp_folder = root_folder
        if ' ' in temp_folder:
            temp_folder = tempfile.gettempdir()
        if ' ' in temp_folder:
            temp_folder = tempfile.mkdtemp(dir="c:/ezbaker_temp")
        project_file_path = os.path.join(temp_folder, '__temp_baker__.HPB')

        meshes_folder = os.path.join(root_folder, 'meshes')
        os.makedirs(meshes_folder, exist_ok=True)

        # set extention and bit depth
        texture_format = self.image_format.lower()

        bit_depth = int(baker.color_depth)
        if texture_format == 'tga':
            bit_depth = '8'

        # Write data out (2 integers)
        with open(project_file_path, "w") as file:
            file.write('BakerConfiguration bakeConfig')
            with Write_Wrapper(file, '{', '}', 0, True):
                custom_write(file, 'int32 version = 1;', 1)
                custom_write(file, 'ProjectionGroup groups', 1)
                with Write_Wrapper(file, '[', ']', 1, True):
                    for bake_group in baker.bake_groups:
                        with Write_Wrapper(file, '{', '}', 2, True):
                            custom_write(file, 'String name = "{}";'.format(bake_group.key), 3)
                            custom_write(file, 'HighPolyModelConfiguration highModels', 3)
                            with Write_Wrapper(file, '[', ']', 3):
                                models = bake_group.objects_high
                                for model in models:
                                    with Write_Wrapper(file, '{', '}', 4):
                                        name = model.name
                                        write_value(file, 'Filename', 'model', export_obj(meshes_folder, model, name, t_space=False, modifiers=True), 4)
                                        write_value(file, 'bool', 'overrideMaterial', False, 4)
                                        write_value(file, 'int32', 'material', 0, 4)
                                        write_value(file, 'bool', 'isFloater', False, 4)

                            # low poly
                            custom_write(file, 'LowPolyModelConfiguration lowModels', 3)
                            with Write_Wrapper(file, '[', ']', 3):
                                models = bake_group.objects_low
                                for model in models:
                                    with Write_Wrapper(file, '{', '}', 4):
                                        cage = self.id_data.objects.get(model.name + self.id_data.EZB_Settings.suffix_cage)
                                        cage_path = '' if not cage else export_obj(meshes_folder, cage, cage.name, t_space=True, modifiers=True)
                                        write_value(file, 'Filename', 'model', export_obj(meshes_folder, model, model.name, t_space=True, modifiers=True), 4)
                                        write_value(file, 'Filename', 'cageModel', cage_path, 4)
                                        write_value(file, 'bool', 'overrideCageOffset', False, 4)
                                        write_value(file, 'float', 'autoCageOffset', bake_group.cage_displacement, 4)

                            # misc
                            write_value(file, 'int32', 'material', 0, 2)
                            write_value(file, 'bool', 'isolateAO', False, 2)
                            write_value(file, 'float', 'autoCageOffset', bake_group.cage_displacement * 100, 2)

                # BAKE SETTINGS
                write_value(file, 'float', 'aoSampleRadius', device.maps.AO.sample_radius, 0)
                write_value(file, 'int32', 'aoSampleCount', device.maps.AO.sample_count, 0)
                write_value(file, 'float', 'thicknessSampleRadius', device.maps.THICKNESS.sample_radius, 0)
                write_value(file, 'int32', 'thicknessSampleCount', device.maps.THICKNESS.sample_count, 0)
                write_value(file, 'bool', 'volumetricGradientCubeFit', False, 0)
                write_value(file, 'float', 'heightMapScale', device.maps.HEIGHT.scale, 0)
                write_value(file, 'float', 'heightMapOffset', device.maps.HEIGHT.offset, 0)
                write_value(file, 'bool', 'curvatureUseRaySampling', device.maps.CURVATURE.use_ray_sampling, 0)
                write_value(file, 'float', 'curvatureSampleRadius', device.maps.CURVATURE.sample_radius, 0)
                write_value(file, 'int32', 'curvatureSampleCount', device.maps.CURVATURE.sample_count, 0)
                write_value(file, 'int32', 'curvaturePixelRadius', device.maps.CURVATURE.pixel_radius, 0)
                write_value(file, 'bool', 'curvatureAutoNormalize', device.maps.CURVATURE.auto_normalize, 0)
                write_value(file, 'float', 'curvatureMaxAngle', device.maps.CURVATURE.max_angle, 0)
                write_value(file, 'float', 'curvatureOutputGamma', device.maps.CURVATURE.gamma, 0)
                write_value(file, 'float', 'cavitySensitivity', device.maps.CAVITY.sensitivity, 0)
                write_value(file, 'float', 'cavityBias', device.maps.CAVITY.bias, 0)
                write_value(file, 'int32', 'cavityPixelRadius', device.maps.CAVITY.pixel_radius, 0)
                write_value(file, 'float', 'cavityOutputGamma', device.maps.CAVITY.gamma, 0)
                write_value(file, 'KernelType', 'cavityKernelType', device.maps.CAVITY.kernel_type, 0)
                write_value(file, 'int32', 'textureSpaceAOPixelRadius', 10, 0)
                write_value(file, 'float', 'textureSpaceAOOutputGamma', 1.0, 0)
                write_value(file, 'float', 'textureSpaceAOSampleCoveragePercentage', 100.0, 0)

                # GLOBAL SETTINGS
                write_value(file, 'int32', 'threadCount', 0, 0)
                write_value(file, 'float', 'backRayOffsetScale', 5.0, 0)
                write_value(file, 'bool', 'downsampleInGeneratorSpace', True, 0)
                write_value(file, 'bool', 'buildSmoothedNormalsForHighRes', True, 0)
                write_value(file, 'bool', 'suppressTriangulationWarning', True, 0)

                custom_write(file, 'MaterialLibrary materialLibrary', 1)
                with Write_Wrapper(file, '{', '}', 1):
                    custom_write(file, 'String channelNames', 2)
                    with Write_Wrapper(file, '[', ']', 2):
                        custom_write(file, '"_",', 3)
                        custom_write(file, '"_",', 3)
                        custom_write(file, '"_",', 3)
                    custom_write(file, 'MaterialConfiguration materials', 2)
                    with Write_Wrapper(file, '[', ']', 2):
                        with Write_Wrapper(file, '{', '}', 3):
                            custom_write(file, 'String name = "{}";'.format('0'), 4)
                            custom_write(file, 'Color matIDColor = {};'.format('0xFFFFFFFF'), 4)
                            custom_write(file, 'Color channelColors', 4)
                            with Write_Wrapper(file, '[', ']', 4):
                                custom_write(file, '0xFF000000,', 4)
                                custom_write(file, '0xFF000000,', 4)
                                custom_write(file, '0xFF000000,', 4)
                # OUTPUT SETTINGS
                write_value(file, 'Filename', 'outputFolder', export_folder, 0)
                write_value(file, 'String', 'outputFilename', file_name, 0)
                write_value(file, 'String', 'outputExtension', texture_format, 0)
                write_value(file, 'ImageBitDepth', 'outputBitDepth', bit_depth, 0)

                write_value(file, 'int32', 'outputWidth', baker.width, 0)
                write_value(file, 'int32', 'outputHeight', baker.height, 0)
                write_value(file, 'int32', 'outputPadding', baker.padding, 0)
                write_value(file, 'int32', 'outputSuperSample', baker.get_supersampling * baker.get_supersampling, 0)
                write_value(file, 'bool', 'outputDither', device.use_dither, 0)

                # IMAGE OUTPUTS
                custom_write(file, 'ImageOutput outputs', 1)
                with Write_Wrapper(file, '[', ']', 1, True):
                    for map_name in map_names:
                        with Write_Wrapper(file, '{', '}', 2, True):
                            enabled = True
                            suffix = '_'
                            try:
                                map = next(x for x in device.get_bakeable_maps() if x.pass_name == map_name)
                                suffix = map.suffix
                            except StopIteration:
                                enabled = False

                            write_value(file, 'bool', 'isEnabled', enabled, 3)
                            write_value(file, 'String', 'filenameSuffix', suffix, 3)

                tangent_space = next(x[1] for x in tangent_space_enum if x[0] == device.maps.NORMAL.tangent_space)
                write_value(file, 'String', 'tangentSpace', tangent_space, 0)
        return project_file_path

    def get_commandline_argument(self):
        baker = self.parent_baker

        prefs = bpy.context.preferences.addons[__package__.split('.')[0]].preferences

        project_file_path = self.write_handplane_file(baker)

        # bake with handplane
        handplane_cmd = os.path.join(prefs.handplane_path, 'handplaneCmd.exe')
        project_file_path = project_file_path.replace('\\', '/')
        command_argument = [ handplane_cmd , "/project", project_file_path ]
        if sys.platform == 'linux':
            command_argument.insert(0, "wine")
        return os.path.split(project_file_path)[0], command_argument

    def bake_local(self):
        path, command_argument = self.get_commandline_argument()

        subprocess.run(command_argument, cwd=path)
        self.bake_finish()

    def bake_multithread(self):
        bpy.ops.ezb.run_handplane_background(
            baker_scene=self.parent_baker.id_data.name,
            baker_datapath=self.parent_baker.path_from_id(),
            device_datapath=self.path_from_id()
        )

    def bake_finish(self):
        if self.parent_baker.load_images:
            baker = self.parent_baker
            export_folder = baker.get_abs_export_path()
            # open explorer at baked textures
            for map in self.get_bakeable_maps():
                img_path = os.path.join(export_folder, baker.key + map.suffix + file_formats_enum_handplane[self.image_format])
                img = baker.get_image(map, baker.key)
                img.image.source = 'FILE'
                img.image.filepath = img_path
                img.image.reload()
                pass

        super().bake_finish()

    def check_for_errors(self, context):
        ans = super().check_for_errors(context)
        if ans:
            return ans

        prefs = bpy.context.preferences.addons[__package__.split('.')[0]].preferences

        if not prefs.handplane_path:
            return 'No Handplane path set in the addon preferences'

        handplane_path = os.path.join(prefs.handplane_path, 'handplaneCmd.exe')

        if not os.path.isfile(handplane_path):
            return 'Handplane path in the addon preferences is incorrect'

        return None

    def show_progress(self):
        return f'Baking...'


classes = [EZB_OT_run_handplane_background, EZB_Device_Handplane]


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
