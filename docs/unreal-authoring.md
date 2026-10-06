# Real Unreal authoring, with the untested boundary visible

This revision supplies an **editor authoring program**, not a playable expansion.
The program creates genuine Unreal assets when run in the supported editor. None
of those generated assets, their cook, or gameplay has been executed here.
The cloud has Python but not UE 4.27.2 Windows. Local unit tests exercise input
validation and naming contracts only; they are not Unreal integration tests.

## What is implemented in source

`authoring/build_resonance.py` uses Epic's UE 4.27 Python editor API:

- Imports five original FBX meshes, assigning original materials by their imported slot names;
  sets centimetre conversion, scale 1, imported normals, authored UCX collision
  and lightmap UV generation explicitly; disables **Has Navigation Data** on every mesh
- Builds eight opaque Unreal materials with real color/roughness/metallic nodes
  from the artist manifest, avoiding FBX/PBR color translation ambiguities
- Creates `EchoGlass_IT` / `EchoGlass_BP` and `TuningLens_IT` / `TuningLens_BP`,
  native-parent Blueprint assets (`ItemType` / `PhysicalItem`), and connects each
  IT's `PickupActor`, BP's `ItemComponent.ItemType`, and native mesh component
- Authors the lens's actual `FRecipe`: one Echo Glass. No printer registration
  is emitted; this avoids making the unfinished Echo Glass free to print
- Creates an explicitly unbound `ResonantVapour_IT` descriptor, with no gas
  container inheritance, pickup actor, storage patch or production claim
- Creates `ResonanceSite_BP`, a StaticMeshActor visual shell with the base mesh
- Creates `DA_ResonanceMissions` using `AstroMissionDataAsset`, containing all six
  named mission rows, dependencies, next-mission links and real custom objectives
- Sets item DLC locks to None and both mission entitlement requirements false
- Saves only this mod's generated content and writes an inventory/report under
  the kit's Saved directory. The report always says `runtime_ready: false`

Asset namespace: `/Game/Mods/deltadasher/AstroneerReimagined/Resonance`.
The script refuses a nonempty destination rather than overwriting hand-edited
Blueprints. On a partial failure, inspect the failure and restore a clean copy
of the destination from source control before retrying. It does not delete or
roll back content. Do not run while PIE is active.

## Run later on the Windows authoring machine

1. Use the community ModdingKit at commit
   `e7f4d47eb368f72887dc32100600ba8ab3072184` and **UE 4.27.2**. Follow the kit's
   documented build/setup procedure. This commit's declared game target is not
   proof of compatibility with the user's installed Astroneer build
2. Enable Python Editor Script Plugin and Editor Scripting Utilities in the kit
   and restart as required. Open `Astro.uproject`; do not run these scripts in
   system Python or the shipped game
3. Place this repository anywhere, with the five supplied models under `assets/`
   retaining their `SM_*.fbx` names. There must be exactly one of each and one `asset_manifest.json`. Do not
   substitute the concept PNGs or a third-party/base-game mesh
4. Open Unreal's Python console and run (adjust the source path):

   ```python
   import sys
   sys.path.insert(0, r'C:/src/Astroneer-Reimagined/authoring')
   import build_resonance
   build_resonance.build(r'C:/src/Astroneer-Reimagined')
   ```

5. Inspect the resulting assets, compile each generated Blueprint in its editor,
   and save. Native properties are probed by their exact reflected SDK names and
   expected Python aliases; if reflection fails, capture the exact error rather
   than substituting an unrelated field
6. Close and reopen the editor, then run `import verify_resonance;
   verify_resonance.verify()`. This checks that references and recipe survived
   serialization, six missions exist, and mesh navigation remains disabled.
   It does not certify Blueprint graph compilation or gameplay
7. Check FBX material import in Lit view, centimetre scale against T1 slots,
   lens orientation, grip placement, collision, and lighting. The supplied UCX collision is
   provisional and must be checked for fit; dormant/active rings intentionally
   have no collision

The current script creates no event graph, body-slot override, persistence,
network RPC, item icon, research catalog entry or site placement. Python is an
editor-only tool here. There is no supported claim that UE4.27's built-in Python
API can construct the required K2 graphs, so no guessed graph API is called.

## Bounded remaining Blueprint work

These are implementation tasks, not steps already completed by the generator.
The exact content implementation and event timing must be inspected in-editor
and exercised in the actual game before registration/packaging.

### Items and visual shell

- For each item BP, verify `ItemComponent` values (discrete, capacity 1, starting
  amount 1), inherited slots and collision. Follow the kit's permitted
  `Content/Mods/ExampleAuthor/InteractableItemMod` example to implement the
  actual body-slot override and native interaction pattern. Do not inherit its
  tutorial behavior accidentally or merely rename its assets
- Add original inventory icons. Add `ItemCatalogData` as an instanced property,
  choosing a valid existing base-game category/row, non-DLC base IT and unlock
  cost. Keep generated resources unregistered until an actual production path
  exists; do not expose the empty Echo Glass construction recipe
- In the site BP, add two Static Mesh Components with the dormant and active
  ring meshes. Keep identity transforms: the model parts share one ground-center
  origin. Make one visible according to authoritative saved site state, and
  leave the base visible. This visual shell is not a save-persistent site actor;
  choose the supported save/actor ownership approach before placing it

### Event contract for the six real mission rows

All rows are intentionally `Auto Activate = false` and not registered in metadata.
Each has a Custom objective, `Value=1`, `ProgressType=HighWater`, and
`Planet=Terran` (SDK identifier for Sylva). Exact tags:

| Mission ID | Custom tag | Raise only after |
| --- | --- | --- |
| AR_Resonance_discover | AR.Resonance.discover | The one specific Sylva site is genuinely discovered |
| AR_Resonance_experiment | AR.Resonance.experiment | An experiment successfully delivers a sample |
| AR_Resonance_craft | AR.Resonance.craft | A lens is actually crafted from its valid recipe |
| AR_Resonance_restore | AR.Resonance.restore | Site restoration succeeds with a valid lens |
| AR_Resonance_awaken | AR.Resonance.awaken | Authoritative current Sylva engine state is active |
| AR_Resonance_retune | AR.Resonance.retune | Restored site successfully retunes after awakening |

The verified native endpoint is `AstroMissionsManager.AuthorityRaiseMissionEvent`
with arguments `(ObjectiveType, TargetType, SecondaryTargetType, Count, Planet,
CustomTag)`. For these tag-only objectives the proposed emitter uses Custom,
no target type, no secondary type, Count 1, Terran and the corresponding tag.
Confirm the game's target filtering, progress interpretation, activation and
prerequisite behavior before relying on it. `HighWater` expresses an intended
idempotent 0/1 objective, but does not make item grants or native completion safe.

Build emitters only on authority. Validate success first, persist the irreversible
resource/state transition, and then report its completion. Guard duplicate client
RPCs; do not use mission completion alone to mint a repeatable resource. Sample
production must remain repeatable after restoration/retuning and after core
awakening, with deliberate full-storage behavior and no consumed lens.

The awaken row deliberately uses a custom state observation rather than only
`ActivateGateEngine`: an already-awakened save must not wait for an event that
cannot recur. Inspect `GatesGameState.ReplicationData` and
`PlanetaryGateObjectsState.bEngineActivated` plus planet identity. The kit exposes
these declarations, but its C++ method bodies are stubs. Establish an authoritative
state source, ready timing, persisted latch and reload reconciliation in the game.
Other planets must never satisfy this objective.

### Gas, world persistence and deployment remain blockers

- Establish real gas subtype, canister units and transfer semantics from the
  permitted `atenfyr/PortableMachines` example and actual game dependencies.
  No atmospheric override is needed for this site-produced gas. The current IT
  alone is **not** a usable gas. Do not register its storage whitelist yet
- Establish Echo Glass's real recipe station and gas-unit consumption, atomic
  delivery/inventory updates, power/rate, failure and retry behavior
- Implement exactly one site's placement on Sylva, including existing worlds,
  multiplayer ownership, migration, save/load, duplicate prevention and removal
- Register missions only after reliable event producers/initialization exist;
  enable intended activation then. Register only playable items, and cook on
  Windows. Staging instructions separately require a reviewed runtime manifest

## Evidence and licensing

SDK headers were inspected at the pinned commit, including `ItemType.h`,
`PhysicalItem.h`, `ItemComponent.h`, `ItemRecipeIngredient.h`, `Recipe.h`,
`AstroMissionDataAsset.h`, `AstroMissionData.h`, `AstroMissionObjective.h`,
`AstroMissionsManager.h`, and the enum headers. Important genuine field typos are
`MissionCatagory`, `Decription`, `PrerequisitMissions`; the builder preserves them.
Kit C++ is reconstruction/authoring scaffolding, not replacement game runtime.

- [Pinned kit](https://github.com/AstroTechies/ModdingKit/tree/e7f4d47eb368f72887dc32100600ba8ab3072184)
- [BlueprintFactory](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/BlueprintFactory?application_version=4.27), [DataAssetFactory](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/DataAssetFactory?application_version=4.27), [EditorAssetLibrary](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EditorAssetLibrary?application_version=4.27)
- [FBX import data](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/FbxStaticMeshImportData?application_version=4.27), [StaticMesh](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/StaticMesh?application_version=4.27)
- [Custom-item guide](https://astroneermodding.readthedocs.io/en/latest/guides/kitModding.html), [mission guide](https://astroneermodding.readthedocs.io/en/latest/guides/addingMissions.html)
- [Kit license by directory](https://github.com/AstroTechies/ModdingKit/blob/e7f4d47eb368f72887dc32100600ba8ab3072184/LICENSE.md)

The permitted interaction and PortableMachines example folders are declared
public-domain in that license. They were inspected as references; this revision
copies no third-party `.uasset`, game model or SDK source implementation into the
repository. Other kit content must not be assumed redistributable just because
the kit is public. Original mesh sources are delivered separately under assets.
