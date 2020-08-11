# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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