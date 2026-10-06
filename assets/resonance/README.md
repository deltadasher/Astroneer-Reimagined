# Resonance: original low-poly asset pack

Original meshes for the **Astroneer Reimagined** first-slice prototype. This is a source asset deliverable, **not a cooked or game-tested mod**. No game geometry, palette textures or proprietary shaders have been copied.

## Deliverables

- `source/ResonanceAssets.blend`: editable Blender 4.3.2 source with shared assembly origins
- `source/build_models.py`: deterministic procedural geometry builder and optional studio renderer
- `exports/*.fbx`: five individually exported, triangulated static meshes
- `asset_manifest.json`: measured authored bounds, mesh counts, material colors, UVs and assembly contract
- `renders/`: front/rear instrument views, nugget and dormant/active site previews

Rebuild using `blender -b --python source/build_models.py -- --render`. Omit `-- --render` to export geometry only. No external assets or Python packages are required by the builder. Render camera, floor and lights are added **after** saving the clean source and are never exported.

## Design and interaction

**Tuning Lens:** a compact white protective shell, dark inner optical housing, mint solid lens, orange calibration wheel and orange rear grip. The flat low heel suggests slot attachment. The wheel and grip are physical affordances; actual interactions require Blueprint logic.

**Echo Glass:** a mint faceted grown-material nugget with a modest manufactured heel and three retention tabs. Opaque flat color is intentional: readability does not depend on glass transparency or emissive materials.

**Resonance Site:** a low, uneven lithic cradle with three small probe targets. Three closed stone shutters conceal a dark core when dormant. The responsive variant opens those shutters outward and exposes a taller mint crystal and two resonator rings. The silhouette itself communicates the state, even without shader animation. It is an original ancient-looking field structure, not a copied gateway or EXO research pod.

The three site meshes share one origin. Place Base plus **either** Dormant **or** Active at the same transform. Do not display both state meshes at once. The two rings intentionally levitate around the exposed core; they are static geometry and require no rigging or shader effect. The three bright inserts are embedded in the shutters. “Active” may represent restored or retuned visually until more states are authored.

No new gas canister mesh is included. A new gas definition should use a verified native container integration rather than duplicating proprietary canister geometry.

## Scale, axes and sockets

- Geometry is authored numerically in **centimetres**, Blender unit scale **0.01 m**
- Authoring coordinates: **+Z up**, instrument viewing face **+Y**
- Export: FBX forward **-Y**, up **Z**, `apply_unit_scale=True`, `FBX_SCALE_UNITS`, global scale **1**
- Initial UE import uniform scale: **1.0**, exposed/configurable by importer
- Tuning Lens bounds: approximately **26.3 × 19.4 × 35.6 cm**
- Echo Glass bounds: approximately **17.9 × 19.0 × 23 cm**
- Full site footprint approximately **84 × 82 cm**, top at **73 cm**
- Every mesh pivot is `(0, 0, 0)`; lens/nugget pivot is heel contact center; all site pivots are shared ground center. A few stone vertices sit slightly below ground to help terrain seating

**These are provisional design dimensions, not measured vanilla Tier1 dimensions.** The ModdingKit contains `/Game/Models/scale_ref/slot_tier1_collision` and socket references but no accessible source FBX/Blend in the inspected tree. Measure that asset and verify backpack and storage clearance in the Windows editor before approving scale. Visual heel geometry is not a functional slot.

The modding FAQ documents a `ChildSlotComponent` attached to the static mesh, with its blue/Z axis normal to the surface: down for the body's attachment point and up for the receiving slot. Implement the relevant body slot and `GetBodySlotLegacy` in Blueprint; check the exact class in the installed kit. No unsupported FBX socket empties are invented here.

## Unreal import and materials

Import each FBX separately as one static mesh. There are no textures. Eight shared material names are provided in stable source order; map by **name**, since importers may drop unused slots:

1. `M_Shell`: warm off-white polymer
2. `M_Seam`: blue-black recesses
3. `M_Signal`: teal accent
4. `M_Control`: orange controls
5. `M_Echo`: mint material/core
6. `M_Stone`: dark blue-green geology
7. `M_StoneLight`: lighter stone facets
8. `M_EchoLight`: pale mint facet/ring

All are opaque Principled base colors, roughness 0.55, metallic 0.05. Exact **linear** values are in `asset_manifest.json`. Recreate them as simple UE materials or deliberately map to verified game-compatible material parents; Blender shaders are not expected to transfer identically. Do not imply these colors use the vanilla palette UV layout.

Meshes have explicit triangles, flat normals, UV0 smart-projected islands, applied render transforms and no texture dependencies. Import normals. Generate a separate lightmap UV1 if static lighting requires it. No LODs or lightmap UV1 are supplied; modest triangle counts suit a first slice, not a performance certification.

### Collision and navigation

- Lens: two coarse convex UCX boxes
- Nugget: one coarse convex UCX box
- Site base: one coarse convex UCX box
- Dormant and active parts: **no authored collision**; disable auto-generated collision for those cosmetic pieces

`UCX_<RenderMeshName>_00` naming follows Epic's static-mesh FBX convention, **not an independently verified Astroneer-specific collision contract**. Each collider is a closed box. Import authored collision; inspect it in the Static Mesh Editor. The site's intentionally simplified base collision does not match every stone edge. If its shutters should physically block players, author additional non-overlapping convex hulls after runtime testing.

**Disable Has Navigation Data on every imported mesh.** Do not enable complex-as-simple physics by default. Use dedicated interaction components rather than assuming the coarse collision doubles as usable cursor targets.

## Verification boundary

Geometry exports and Blender renders can be checked in this environment. **Windows editor import, UE4 asset serialization, cooking, packaging, registration, runtime behavior, sockets, physics, save/load and in-game fit remain UNTESTED.** This folder does not contain `.uasset` or `.pak` outputs and is not presented as an installable mod.

## Reference/provenance

Used for public visual design context only:

- System Era, official [Update 1.26 post](https://blog.astroneer.space/p/update-1-26/) and its [promotional screenshot](https://blog.astroneer.space/wp-content/uploads/2022/09/UPDATE26.1.png): bold color accents, pale equipment shells, dark joints and purposeful low-poly forms. The reference image is not part of the export or redistributable asset pack
- [ModdingKit model tree](https://github.com/AstroTechies/ModdingKit/tree/master/Content/Models): scale/socket asset names, without assuming reconstructed `.uasset` proxies contain measured mesh geometry
- [Astroneer Modding FAQ](https://astroneermodding.readthedocs.io/en/latest/guides/faq.html): socket directions and navigation-data warning
- [Epic UE4 FBX Static Mesh Pipeline](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-static-mesh-pipeline?application_version=4.27): UV, triangulation and custom collision conventions

The original authored meshes/material values/builder in this pack can be added to the user's project. This statement does not grant rights to Astroneer trademarks, reference screenshots, ModdingKit contents or other third-party content. Keep `reference/` out of the repository/published package.
