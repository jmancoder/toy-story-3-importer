# Toy Story 3 Importer
This Blender add-on allows you to import meshes from the PSP and PS2 versions of Toy Story 3. These versions of the game use Zouna Engine and were developed by Asobo Studio.

## Installation
1. Download the latest release of this add-on. Blender versions 4.2 and above are supported.
2. In Blender, open *Edit->Preferences->Add-ons*.
3. Expand the dropdown arrow on the top right and click *Install from Disk*.
4. Select the add-on file and click *Install from Disk*

## Usage
1. Extract the desired .dps file with BigFile Friend (bff): <https://github.com/widberg/bff/releases/tag/v0.1.0>.
2. If a .Skin_Z file is present:
    1. Click *File->Import->TS3 Skinned Mesh (.Skin_Z)*.
    2. Set the *Game Platform* option to match the game you extracted the asset from.
    3. Select the .Skin_Z file and click *Import Skin_Z*.
    4. Corresponding .Skel_Z and .Mesh_Z files will be imported automatically
3. If a .Skin_Z file is not present:
    1. Click *File->Import->TS3 Static Mesh (.Mesh_Z)*.
    2. Set the *Game Platform* option to match the game you extracted the asset from.
    3. Select the .Mesh_Z file and click *Import Mesh_Z*.