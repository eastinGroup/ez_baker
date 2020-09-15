from multiprocessing.connection import Client
import os
import mset
import time
import math

debug = False

address = ('localhost', 1605)
connection = Client(address, authkey=bytes('ezbaker', encoding='utf8'))

baker = mset.BakerObject()


baker.edgePadding = 'Custom'

baker_info = connection.recv()
bake_groups = connection.recv()
maps = connection.recv()

# only the AO dither seems to no be properly set


def close_enough(a, b):
    if type(a) == float:
        return math.isclose(a, b, rel_tol=1e-03)
    else:
        return a == b


def custom_set_attribute(obj, key, value):
    print(key)
    if debug:
        if key != 'multipleTextureSets':
            if type(value) == bool:
                value = not getattr(obj, key)
            elif type(value) == float:
                value = getattr(obj, key) + 0.1
            elif type(value) == int:
                value = getattr(obj, key) + 1

    setattr(obj, key, value)

    if not close_enough(getattr(obj, key), value):
        error_msg = f'\n!!!!!{obj.__class__}__{key} not set correctly ({getattr(obj, key)}->{value})\n'
        connection.send(error_msg)
        print(error_msg)


for key, value in baker_info.items():
    if key != 'tangentSpace':
        custom_set_attribute(baker, key, value)

connection.send(f'INFO:::Loading models...')
for bake_group_name, bake_group_info in bake_groups.items():
    bake_group = baker.addGroup(bake_group_name)
    bake_group.collapsed = True
    for obj_path in bake_group_info['high']:
        model = mset.importModel(obj_path)
        for mesh in model.getChildren():
            custom_set_attribute(mesh, 'tangentSpace', baker_info['tangentSpace'])

        model.parent = bake_group.getChildren()[0]
    for obj_path, cage_path in bake_group_info['low']:
        low_group = bake_group.getChildren()[1]
        model = mset.importModel(obj_path)
        model.parent = low_group

        for mesh in model.getChildren():
            custom_set_attribute(mesh, 'tangentSpace', baker_info['tangentSpace'])

        if cage_path:
            pass

        low_group.maxOffset = bake_group_info['cage_displacement'] * 100
        low_group.minOffset = bake_group_info['cage_displacement'] * 100

# IF MULTIPLE TEXTURE SETS
# baker.multipleTextureSets = True
# print(baker.multipleTextureSets)
# print(baker.getTextureSetCount())
if baker.multipleTextureSets:
    for i in range(0, baker.getTextureSetCount()):
        baker.setTextureSetHeight(i, baker_info['outputHeight'])
        baker.setTextureSetWidth(i, baker_info['outputWidth'])

for map_name, map_info in maps.items():
    connection.send(f'WORKING:::{map_name}')
    for map in baker.getAllMaps():
        map.enabled = False
    # print(map.__class__.__dict__.keys())
    map = baker.getMap(map_name)
    map.enabled = True
    for setting, value in map_info.items():
        custom_set_attribute(map, setting, value)

    baker.bake()
    if baker.multipleTextureSets:
        for i in range(0, baker.getTextureSetCount()):
            name = baker.getTextureSetName(i)

            image_path_split = os.path.splitext(baker.outputPath)
            image_path = image_path_split[0] + '_' + name + '_' + map_info['suffix'] + image_path_split[1]

            connection.send(f'{map_name}:::{name}:::{image_path}')
    else:
        image_path_split = os.path.splitext(baker.outputPath)
        image_path = image_path_split[0] + '_' + map_info['suffix'] + image_path_split[1]

        connection.send(f'{map_name}:::{baker_info["name"]}:::{image_path}')


connection.send('INFO:::Finished')
exit()
