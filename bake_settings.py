import bpy

settings_annotations = {}
for x in bpy.types.BakeSettings.bl_rna.properties:
    if x.type == 'STRING':
        default = ''
        settings_annotations[x.identifier] = (bpy.props.StringProperty, {'name':x.name, 'default': default})
    elif x.type == 'POINTER':
        if x.fixed_type.identifier == 'Object':
            settings_annotations[x.identifier] = (bpy.props.PointerProperty, {'name':x.name,'type': bpy.types.Object})
        else:
            print(x.fixed_type)
        # bpy.types.BakeSettings.bl_rna.properties['cage_object'].fixed_type
        
    elif x.type == 'INT':
        default=0
        settings_annotations[x.identifier] = (bpy.props.IntProperty, {'name':x.name, 'default': default})
    elif x.type == 'FLOAT':
        default = 0.0
        settings_annotations[x.identifier] = (bpy.props.FloatProperty, {'name':x.name, 'default': default})
    elif x.type == 'BOOLEAN':
        default = False
        if x.identifier == 'use_pass_direct':
            default = True
        elif x.identifier == 'use_pass_indirect':
            default = True
        elif x.identifier == 'use_pass_color':
            default = True
        settings_annotations[x.identifier] = (bpy.props.BoolProperty, {'name':x.name, 'default': default})
    elif x.type == 'ENUM':
        default = x.default if x.default else x.enum_items[0].identifier

        if x.identifier == 'normal_space':
            default = 'TANGENT'
        elif x.identifier =='normal_r':
            default = 'POS_X'
        elif x.identifier =='normal_g':
            default = 'POS_Y'
        elif x.identifier =='normal_b':
            default = 'POS_Z'
        
        
        print('{} -- {} || {}'.format(x.identifier, x.default, default))
        settings_annotations[x.identifier] = (bpy.props.EnumProperty, {'name':x.name,'items': [(y.identifier, y.name, y.description) for y in x.enum_items], 'default': default})
    else:
        print(x.type)
print(settings_annotations.keys())
bake_settings = type("bake_settings", (bpy.types.PropertyGroup,), {'__annotations__': settings_annotations})


classes = [bake_settings]

def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)