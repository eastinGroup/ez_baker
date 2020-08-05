import os
import subprocess
import bpy

from .base import EZB_Device
from ..bake_maps import EZB_Maps_Handplane
from ..bake_maps.handplane.map_normal import tangent_space_enum

maps = [
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

def custom_write(file, line, tabs=0, end_line=True):
    ans = tabs*'\t'
    ans += line
    if end_line:
        ans += '\n'
    file.write(ans)

def write_value (file, type, name, value, tabs, end_line=True):
    line = type + ' '
    line += name + ' = '

    if type == 'bool':
        line += str.lower(str(value))
    elif type == 'String' or type == 'Filename':
        line += '"'+str(value)+'"'
    else:
        line += str(value)
    
    line += ';'
    custom_write(file, line, tabs, end_line)

class Write_Wrapper():
    def __init__(self, file, start_line, end_line, tabs=0, end=True):
        self.file = file
        self.start_line = start_line
        self.end_line = end_line
        self.tabs=tabs
        self.end=end

    def __enter__(self):
        custom_write(self.file, self.start_line, self.tabs, self.end)

    def __exit__(self, type, value, traceback):
        custom_write(self.file, self.end_line, self.tabs, self.end)

def export_obj (meshes_folder, obj, type):
    mesh_filepath = os.path.join(meshes_folder, obj.name + '.fbx')
    
    ctx = bpy.context.copy()
    ctx['selected_objects'] = [obj]

    bpy.ops.export_scene.fbx (
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
        use_mesh_modifiers=False, 
        use_mesh_modifiers_render=False, 
        mesh_smooth_type='FACE', 
        use_mesh_edges=False, 
        use_tspace= False if type == 'HP' else True, 
        use_armature_deform_only=False, 
        add_leaf_bones=False, 
        primary_bone_axis='-Y', 
        secondary_bone_axis= 'X', 
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

class EZB_Device_Handplane(bpy.types.PropertyGroup, EZB_Device):
    name = "handplane"
    maps: bpy.props.PointerProperty(type=EZB_Maps_Handplane)

    def draw(self, layout, context):
        pass

    def bake(self, baker):
        mode = 'BAKE'

        device = baker.get_device
        scene = bpy.context.scene
        prefs = bpy.context.preferences.addons[__package__.split('.')[0]].preferences

        file_name = baker.name
        root_folder = os.path.join(baker.get_abs_export_path(), file_name)
        os.makedirs(root_folder, exist_ok=True)

        project_file_path = os.path.join(root_folder, file_name + '.HPB')

        meshes_folder = os.path.join(root_folder, 'meshes')
        os.makedirs(meshes_folder, exist_ok=True)
        
        # set extention and bit depth
        texture_format = baker.image_format.lower()
        bit_depth = int(baker.color_depth)

        textures_path = os.path.join(root_folder, 'textures')
        os.makedirs(textures_path, exist_ok=True)
        
        # Write data out (2 integers)
        with open (project_file_path, "w") as file:
            file.write ('BakerConfiguration bakeConfig')
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
                                        write_value(file, 'Filename', 'model', export_obj(meshes_folder, model, 'HP'), 4) 
                                        write_value(file, 'bool', 'overrideMaterial', False, 4) 
                                        write_value(file, 'int32', 'material', 0, 4)
                                        write_value(file, 'bool', 'isFloater', False, 4)

                            # low poly               
                            custom_write(file, 'LowPolyModelConfiguration lowModels', 3)
                            with Write_Wrapper(file, '[', ']', 3):
                                models = bake_group.objects_low
                                for model in models:
                                    with Write_Wrapper(file, '{', '}', 4):
                                        cage = bpy.context.scene.objects.get(model.name + bpy.context.scene.EZB_Settings.suffix_cage)
                                        cage_path = '' if not cage else export_obj(meshes_folder, cage, 'C')
                                        write_value(file, 'Filename', 'model', export_obj(meshes_folder, model, 'LP'), 4) 
                                        write_value(file, 'Filename', 'cageModel', cage_path, 4) 
                                        write_value(file, 'bool', 'overrideCageOffset', False, 4) 
                                        write_value(file, 'float', 'autoCageOffset', bake_group.cage_displacement, 4)

                            # misc
                            write_value(file, 'int32', 'material', 0, 2)
                            write_value(file, 'bool', 'isolateAO', False, 2)
                            write_value(file, 'float', 'autoCageOffset', bake_group.cage_displacement, 2)

                ###BAKE SETTINGS
                write_value(file, 'float', 'aoSampleRadius', 1.0, 0) 
                write_value(file, 'int32', 'aoSampleCount', 20, 0)
                write_value(file, 'float', 'thicknessSampleRadius', 1.0, 0) 
                write_value(file, 'int32', 'thicknessSampleCount', 20, 0)
                write_value(file, 'bool', 'volumetricGradientCubeFit', False, 0)
                write_value(file, 'float', 'heightMapScale', 1.0, 0)
                write_value(file, 'float', 'heightMapOffset', 0.0, 0)
                write_value(file, 'bool', 'curvatureUseRaySampling', False, 0)
                write_value(file, 'float', 'curvatureSampleRadius', 0.05, 0)
                write_value(file, 'int32', 'curvatureSampleCount', 20, 0)
                write_value(file, 'int32', 'curvaturePixelRadius', 4, 0)
                write_value(file, 'bool', 'curvatureAutoNormalize', True, 0)
                write_value(file, 'float', 'curvatureMaxAngle', 100.0, 0)
                write_value(file, 'float', 'curvatureOutputGamma', 1.0, 0)
                write_value(file, 'float', 'cavitySensitivity', 0.75, 0)
                write_value(file, 'float', 'cavityBias', 0.015, 0)
                write_value(file, 'int32', 'cavityPixelRadius', 4, 0)
                write_value(file, 'float', 'cavityOutputGamma', 1.0, 0)
                write_value(file, 'KernelType', 'cavityKernelType', 'ConstantDisk', 0)
                write_value(file, 'int32', 'textureSpaceAOPixelRadius', 10, 0)
                write_value(file, 'float', 'textureSpaceAOOutputGamma', 1.0, 0)
                write_value(file, 'float', 'textureSpaceAOSampleCoveragePercentage', 100.0, 0)


                ####GLOBAL SETTINGS
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
                ###OUTPUT SETTINGS
                write_value(file, 'Filename', 'outputFolder', textures_path, 0)
                write_value(file, 'String', 'outputFilename', file_name, 0)
                write_value(file, 'String', 'outputExtension', texture_format, 0)
                write_value(file, 'ImageBitDepth', 'outputBitDepth', bit_depth, 0)

                write_value(file, 'int32', 'outputWidth', baker.width, 0)
                write_value(file, 'int32', 'outputHeight', baker.height, 0)
                write_value(file, 'int32', 'outputPadding', baker.padding, 0)
                write_value(file, 'int32', 'outputSuperSample', baker.get_supersampling, 0)
                write_value(file, 'bool', 'outputDither', True, 0)
                
                ###IMAGE OUTPUTS
                custom_write(file, 'ImageOutput outputs', 1)
                with Write_Wrapper(file, '[', ']', 1, True):
                    for map_name in maps:
                        with Write_Wrapper(file, '{', '}', 2, True):
                            enabled = True
                            suffix = '_aa'
                            try:
                                map = next(x for x in device.get_active_maps() if x.pass_name == map_name)
                                suffix = map.suffix
                            except StopIteration:
                                enabled = False
                            
                            write_value(file, 'bool', 'isEnabled', enabled, 3)
                            write_value(file, 'String', 'filenameSuffix', suffix, 3)
                
                tangent_space = next(x[1] for x in tangent_space_enum if x[0] == device.maps.NORMAL.tangent_space)
                write_value(file, 'String', 'tangentSpace', tangent_space, 0)
                      
        if mode == 'GO_TO':
            # start handplane
            handplane_user = os.path.join(prefs.handplane_path, 'handplane.exe')
            subprocess.Popen (handplane_user)
            # open explorer and select handplane file 
            subprocess.Popen (r'explorer /select,' + project_file_path)
            
        elif mode == 'BAKE':
            # bake with handplane
            handplane_cmd = os.path.join(prefs.handplane_path, 'handplaneCmd.exe')
            subprocess.run (handplane_cmd + ' /project ' + project_file_path)
            # open explorer at baked textures
            if scene.gyaz_hpb.texture_folder_popup:
                textures_folder = os.path.abspath ( bpy.path.abspath (root_folder + '/textures') )
                subprocess.Popen('explorer ' + textures_folder)

    def check_for_errors(self):
        ans = super().check_for_errors()
        if ans:
            return ans
        
        if not bpy.context.preferences.addons[__package__.split('.')[0]].preferences.handplane_path:
            return 'No Handplane path set in the addon preferences'

        return None
