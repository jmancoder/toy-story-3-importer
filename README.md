# Toy Story 3 Importer
This Blender add-on allows you to import meshes from the PSP and PS2 versions of Toy Story 3. These versions of the game use Zouna Engine and were developed by Asobo Studio.

## Installation
1. Download the latest version of this add-on from the [releases](https://github.com/jmancoder/toy-story-3-importer/releases) page. Blender 4.2 and newer is supported.
2. In Blender, open *Edit->Preferences->Add-ons*.
3. Expand the dropdown arrow on the top right, click *Install from Disk*, and select the add-on file.

## Usage
1. Extract the desired .dps file with BigFile Friend (bff): <https://github.com/widberg/bff/releases/tag/v0.1.0>.
2. If a Skin_Z file is present:
    1. Click *File->Import->TS3 Skinned Mesh (.Skin_Z)*.
    2. Set the *Game Platform* option to match the game you extracted the asset from.
    3. Select the Skin_Z file and click *Import Skin_Z*. Corresponding Skel_Z and Mesh_Z files will be imported automatically.
3. If a Skin_Z file is not present:
    1. Click *File->Import->TS3 Static Mesh (.Mesh_Z)*.
    2. Set the *Game Platform* option to match the game you extracted the asset from.
    3. Select the Mesh_Z file and click *Import Mesh_Z*.

## Features
### Shared:
- Import bones from Skel_Z files
### PSP:
- Import vertex positions and attributes from Mesh_Z files
- Generate triangles from vertex positions using triangle strip-style ordering
- Import vertex groups and bone weights
### PS2:
- Import vertex positions and triangle indices from Mesh_Z files

## TODO
### PSP:
- Bind high-quality UV and normal attribute pools to vertices in Mesh_Z files
- Read additional data before and after vertex chunks
- Determine how morph packets in Skin_Z files are used
- Import Material_Z files
### PS2:
- Locate and import UVs
- Locate and import bone weights
- Finish analyzing Skin_Z files
