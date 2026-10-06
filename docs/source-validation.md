# Independent source review

Reviewed 2026-10-06. This is a source/static review, not execution of Unreal.

## Confirmed contracts

- The pinned ModdingKit headers at `e7f4d47eb368f72887dc32100600ba8ab3072184`
  declare `UItemType`, `APhysicalItem`, `UAstroMissionDataAsset`,
  `FAstroMissionData`, `FAstroMissionObjective`, `FRecipe` and
  `FItemRecipeIngredient`. Item links, custom objective tags, Sylva's `Terran`
  identifier, recipe ingredients and DLC flags used by the authoring source
  correspond to reflected declarations. Native mission spelling errors are real.
- Epic's **4.27** API documents BlueprintFactory.parent_class,
  DataAssetFactory.data_asset_class, AssetImportTask, FbxImportUI,
  FbxStaticMeshImportData, and EditorAssetLibrary. The source uses these editor
  interfaces rather than invented Blueprint graph construction calls.
- `StaticMesh.has_navigation_data` exists in the 4.27 Python API. The authoring
  script sets and checks it false, matching the modding guide's crash warning.
- Loader metadata v2 uses `schema_version`, `mod_id`, `version` and an
  `integrator` object. Our design JSON and staging manifest are separate formats.

## Explicitly unverified

Python reflection aliases, enum exposure and CDO persistence after Blueprint
compile/reopen require the real pinned Windows editor. Source inspection cannot
establish that generated default-component changes serialize correctly. Neither
an empty graph nor a custom-tag mission objective produces gameplay events.
The kit's native source is reconstructed proxy code; successful compilation or
PIE would not establish equivalent in-game behavior.

There are no generated `.uasset` files or cooked playable mod in this source
bundle. Source scripts create asset definitions when run in the editor. Gas
production/storage, site interactions/placement/save state, objective producers,
core reconciliation, catalog setup, collision and slot fit remain runtime gates.
Do not register inactive mission data or a visual shell as functioning gameplay.

## Local tests

Run `python3 -m unittest discover -s tests -v` from the repository. Progression
unit tests exercise the independent reference model. Staging tests use **synthetic
bytes, not Unreal files** and cover structural metadata, allowlisting, missing
files, path traversal, symlink escapes, non-overwrite and competing invocations.
Authoring tests, if present, are static source/input checks. None substitutes for
editor generation, Windows cooking, game rendering, multiplayer or save testing.

## Primary references

- [Pinned kit headers](https://github.com/AstroTechies/ModdingKit/tree/e7f4d47eb368f72887dc32100600ba8ab3072184/Source/Astro/Public)
- [BlueprintFactory 4.27](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/BlueprintFactory?application_version=4.27)
- [DataAssetFactory 4.27](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/DataAssetFactory?application_version=4.27)
- [FBX static mesh settings 4.27](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/FbxStaticMeshImportData?application_version=4.27)
- [StaticMesh 4.27](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/StaticMesh?application_version=4.27)
- [EditorAssetLibrary 4.27](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EditorAssetLibrary?application_version=4.27)
- [Metadata v2](https://astroneermodding.readthedocs.io/en/latest/standards/metadatav2.html)
- [Maintainer item guide](https://astroneermodding.readthedocs.io/en/latest/guides/kitModding.html)

## Independent original-mesh check

The delivered FBXs were independently imported into Blender 4.3.2, with centimetre
scene units. All five retained expected dimensions, object names, UVMap, eight
named material slots, zero object translations, unit scale, and named UCX hulls
where supplied. Every connected component had positive signed volume; every mesh
had zero nonmanifold edges and zero zero-area faces. Counts were 1,144 triangles
(lens), 262 (Echo Glass), 904 (site base), 172 (dormant), and 402 (active).

The site origin is the shared ground assembly plane; its uneven rocks extend
about 2.11 cm below that plane. State meshes sit 19–73 cm above it. This is
intentional terrain embedding, not a missing transform. The in-game item-slot
reference has not been measured, so fit remains provisional.

Four studio renders were visually inspected: lens, Echo Glass, and both assembled
site states. The meshes have readable faceted silhouettes, restrained shell/seam
colors and distinct dormant/active geometry. These are Blender renders, not
Astroneer screenshots. The accompanying generator constructs original meshes;
no proprietary mesh extraction is part of it.

Reproduce the geometry report with:

```sh
blender -b --python tools/verify_fbx.py -- /path/to/assets/resonance
```

This writes `independent_mesh_review.json` next to the asset manifest. It does not
assert absence of self-intersections or test Unreal collision/slot behavior.

The material-authoring revision was also checked against Epic's
[MaterialEditingLibrary 4.27](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/MaterialEditingLibrary?application_version=4.27):
constant RGB, roughness and metallic nodes use documented creation and connection
calls. Slot mapping uses documented imported/material slot names, and the real
artist manifest passes the offline eight-material input check. Explicit FBX unit
conversion, imported normals, and disabled automatic collision generation now
match the artist's UCX/state-mesh contract. This remains source review only.
