# Toy Story 3 Importer
This Blender add-on allows you to import meshes extracted from the PSP release of Toy Story 3.

## Installation
1. Download the latest version of this add-on from the [releases](https://github.com/jmancoder/toy-story-3-importer/releases) page. Blender 4.2 and newer is supported.
2. In Blender, open *Edit->Preferences->Add-ons*.
3. Expand the dropdown arrow on the top right, click *Install from Disk*, and select the add-on file.

## Usage
1. Extract the desired DPP file with BigFile Friend (bff): <https://github.com/widberg/bff/releases/tag/v0.1.0>.
2. Click *File->Import->TS3 Skinned Mesh (.Skin_Z)*.
3. Select the Skin_Z file and click *Import Skin_Z*. Associated Skel_Z and Mesh_Z files will be imported automatically.

## Features
- Import vertex positions and attributes from Mesh_Z files
- Generate triangles from vertex positions using triangle strip-style ordering
- Import vertex groups and bone weights
- Import bones from Skel_Z files
- Import multiple meshes at once

## TODO
- Determine the purpose of the int-float pairs in Skin_Z files
- Import Material_Z files
