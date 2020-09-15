# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0](https://gitlab.com/AquaticNightmare/ez_baker/-/releases/0_3_0)
### Added
- Baking with marmoset
    - Ambient Occlusion
    - Bent Normals
    - Bent Normals (Object)
    - Concavity
    - Convexity
    - Curvature
    - Group ID
    - Height
    - Material ID
    - Normals (Object)
    - Normals
    - Object ID
    - Position
    - Thickness
    - UV island
    - Wireframe

- Descriptions to more UI properties

### Changed
- Improved UI layout
- Maps in the map selection dropdown are now sorted by name

### Fixed
- Handplane baker was not baking if the export path had spaces in it
- Baking with tiff format with handplane was not loading back the textures into blender
- Sluggish user interface while baking

## [0.3.0](https://gitlab.com/AquaticNightmare/ez_baker/-/releases/0_3_0)
### Added
- New operators:
    - Create custom cage
    - Preview image as material
- New maps:
    - UV Layout (Requires the Pillow python library to be installed, Install it in the addon preferences)
- Image compression options

### Changed
- Removed requirement to not have spaces in the bake group names

## [0.2.0](https://gitlab.com/AquaticNightmare/ez_baker/-/releases/0_2_0)
### Added
- Baking is now done in another process, making blender resposive in the meantime
- Button to cancel the current baking progress
- Option to not load images into blender after the bake

### Fixed
- Show image button in the outputs panel can now show the image in another window

### Changed
- Moved 8 bit compression options from the baker to the normal map options

## [0.1.7](https://gitlab.com/AquaticNightmare/ez_baker/-/releases/0_1_7)
### Fixed
- Baking as 16 was not working

### Added
- Experimental options for hiding artifacts due to 8 bit compression

## [0.1.6](https://gitlab.com/AquaticNightmare/ez_baker/-/releases/0_1_6)
### Fixed
- Fixed Curvature baking with handplane

## [0.1.5](https://gitlab.com/AquaticNightmare/ez_baker/-/releases/0_1_5)
### Added
- Auto updater
- New maps:
    - Alpha
    
### Fixed
- TGA and TIFF baking with blender
- 16 bit TGA baking with handplane

## [0.1.4](https://gitlab.com/AquaticNightmare/ez_baker/-/releases/0_1_4)
### Fixed
- Fixed bake group creation from collection

## [0.1.3](https://gitlab.com/AquaticNightmare/ez_baker/-/releases/0_1_3)
### Fixed
- TGA and TIFF formats were giving errors

## [0.1.2](https://gitlab.com/AquaticNightmare/ez_baker/-/releases/0_1_2)
### Changed
- UI improvements

### Fixed
- Images baked with blender are now correctly saved with selected depth and channels


## [0.1.1](https://gitlab.com/AquaticNightmare/ez_baker/-/releases/0_1_1)
### Added
- new operator to modify cage options for multiple bake groups
- more triangulation options for normal map
- samples option added to normal map

### Changed
- Images are now directly saved to disk, instead of being packed

### Fixed
- Scrolling issue in bake groups

### Removed
- Export maps button

## [0.1.0](https://gitlab.com/AquaticNightmare/ez_baker/-/releases/0_1_0)
### Added
- new maps:
    - Emission
    - Glossy
    - Metallic
    - Roughness
    - Subsurface Color
    - Base Color
    - Transmission
### Fixed
- Low to Low now only bakes itself and ignores the rest of the objects
- Better support for baking with the "low_to_low" option
- Supersampling now works with the blender baker

### Changed
- The preview cage is now unselectable and selection and active object is kept when showing/hiding it
- The low to low setting is now set per baker and not per bake_group
- some UI changes

## [0.0.3](https://gitlab.com/AquaticNightmare/ez_baker/-/releases/0_0_3)
### Fixed
- Memory leak when showing/hiding the cage of a bake group
- Low to Low baking would ignore the material setup of the low objects
### Changed
- The icon for opening the export folder has been changed
- Lowered the default cage displacement to 0.05 and made the slider more precise

## [0.0.2](https://gitlab.com/AquaticNightmare/ez_baker/-/releases/0_0_2)
### Fixed
- Missing icon making the UI unusable
### Changed
- Maps now appear in categories

## [0.0.1](https://gitlab.com/AquaticNightmare/ez_baker/-/releases/0_0_1)
### Added
- Initial release