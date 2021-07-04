mode_group_types = [
    ('NAME', 'Name', 'Group low and high by object names', 'OUTLINER_OB_MESH', 0),
    ('COLLECTION', 'Collection', 'Group low and high by their collection names', 'GROUP', 1),
    ('CUSTOM', 'Custom', 'Manually add high and low objects', 'MODIFIER_DATA', 2),
]

devices_enum = [
    ('BLENDER', 'Blender', 'Blender', 'BLENDER', 0),
    ('HANDPLANE', 'Handplane', 'Handplane', 'AXIS_TOP', 1),
    ('MARMOSET', 'Marmoset Toolbag', 'Marmoset Toolbag', 'MESH_MONKEY', 2),
]

file_formats_enum_blender = {
    'PNG': '.png',
    'TARGA': '.tga',
    'TIFF': '.tiff',
}

file_formats_enum_handplane = {
    'PNG': '.png',
    'TGA': '.tga',
    'TIF': '.tif',
}

file_formats_enum_marmoset = {
    'PNG': '.png',
    'TGA': '.tga',
}
