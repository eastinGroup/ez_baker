# EZ Baker

This addon was created to offer an easier alternative to blender's default bake system.

## Baker
Each baker stores the most basic bake options (texture size, output path, padding...)

## Bake Group
Bake groups are dynamically populated based on the objects or collections that are in the scene.
e.g. If you have two objects named "test_high" and "test_low", the option to create the "test" bake group will appear.
Once the bake group is created, any new object that matches the naming conditions will automatically be added to it.
Each bake group will be baked separatedly but will share the same textures with the others.
It's used for baking objects that are close together without intersecting issues, or to specify different cage settings to each one.
To use a custom cage, make sure it has the same name as the low object but with "_cage" at the end of its name. e.g. "test_low_cage"

## Maps
The desired output images are configured in this panel.
For each map, you can specify the output image suffix and some specific bake options. 

## Outputs
Once the bake process finishes, all the generated images can be viewed in this panel