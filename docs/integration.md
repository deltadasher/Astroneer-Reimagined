# Runtime integration matrix

Evidence reviewed 2026-10-06 UTC. Astroneer modding is community-supported, not an
official game SDK: [community documentation](https://astroneermodding.readthedocs.io/en/latest/).
Documented facilities establish a direction, **not working support for this mod**.
Every runtime row below remains unimplemented and untested here.

## Compatibility gates
- Kit README names Astroneer **1.36.42.0 (MEGATECH)** as its last update target:
  [ModdingKit](https://github.com/AstroTechies/ModdingKit)
- Authoring guide selects **UE 4.27.2**:
  [kit setup](https://astroneermodding.readthedocs.io/en/latest/guides/kitSetup.html)
- Maintainer warns Linux-cooked meshes/materials may fail and recommends Windows
  cooking: [Linux usage](https://github.com/AstroTechies/ModdingKit#linux-usage)
- User's installed game build, loader version and Proton version are **unknown**.
  Do not infer current game compatibility from kit metadata.

## Required adapters/assets
| Feature | Verified starting point | Still to establish in game |
| --- | --- | --- |
| Solid material and lens | `ItemType` and `PhysicalItem` classes, linked through the item's component; [custom item guide](https://astroneermodding.readthedocs.io/en/latest/guides/kitModding.html) | Appropriate resource subtype, icons/meshes, storage, construction recipe, printer/catalog registration and real costs |
| Custom gas | Maintainer [FAQ](https://astroneermodding.readthedocs.io/en/latest/guides/faq.html) covers gas-canister eligibility and planetary gases; no gas implementation supplied here | Container capacity, transfer behavior, recipe units, site production, save/load and visuals |
| Mission chain | `AstroMissionDataAsset`, prerequisite/next mission fields, `integrator.mission_trailheads`; [mission guide](https://astroneermodding.readthedocs.io/en/latest/guides/addingMissions.html) | Objective producers for custom interactions, completion synchronization, durable progress, unique IDs and failure recovery |
| Core awakening | Inspect [GatesGameState](https://github.com/AstroTechies/ModdingKit/blob/master/Source/Astro/Public/GatesGameState.h) and [PlanetaryGateObjectsState](https://github.com/AstroTechies/ModdingKit/blob/master/Source/Astro/Public/PlanetaryGateObjectsState.h); no bound function assumed here | Exact Sylva core-state API, initialization timing, already-awakened saves, authoritative state and callback lifetime |
| Site and lens interaction | Custom item/actor authoring is documented in the item guide | Placement on existing worlds, discovery signaling, interruption handling and no duplicate spawn |
| Persistence | Maintainer FAQ documents actor saving; reference JSON serialization only here | Supported runtime save mechanism, world ownership, migrations, unknown-version recovery and crash consistency |
| Cook/package | Windows cooking, cooked asset staging and integrator metadata documented in item guide | Actual project, cook, generated metadata, dependency declarations, package hash and install verification |
| Linux/Proton deployment | Native `ModIntegrator-linux-x64` documented in the FAQ; [Classic v1.8.2.0 release](https://github.com/atenfyr/AstroModLoader-Classic/releases/tag/v1.8.2.0) | Steam installation/prefix resolution, loader success, rendering and save verification on user's actual build |

Do not make a `metadata.json` referencing nonexistent assets. Do not copy tutorial
paths into production or treat `content/resonance.json` as loader metadata. Stable
mod/author identifiers must be selected before publishing native assets.

## Reference semantic contract
The Python event names are ours, not SDK callbacks. An eventual adapter supplies:
- `site_discovered`: the specific Sylva site was genuinely discovered
- `sample_experiment_completed`: a successful repeatable experiment, including
  successful sample delivery or an explicitly designed full-storage behavior
- `tuning_lens_crafted`: a successfully created lens from valid inputs
- `site_restored`: restoration succeeded at the correct site with the lens
- `core_awakened_observed`: authoritative current state says Sylva is awakened
- `site_retuned`: retuning succeeded at that restored site after awakening

Input/resource side effects and mission state must be coordinated by the runtime;
the pure model neither validates inventory nor performs transactions. Repeated
notifications are harmless in the reference, but that does not guarantee in-game
item grants are idempotent. Other planets' core changes must never trigger this gate.

## Evidence quality
These links are maintainer documentation, reviewed as a feasibility starting point.
Relevant SDK source locations are linked for implementation inspection. No source
commit is pinned, no game assets were inspected, and no runtime binary was
executed. The implementing agent must pin the selected kit/tool releases, inspect
actual current declarations, and update this matrix with runtime evidence.

## Additional implementation references
- [Mission objective types](https://github.com/AstroTechies/ModdingKit/blob/master/Source/Astro/Public/EAstroMissionObjectiveType.h)
- [Mission data](https://github.com/AstroTechies/ModdingKit/blob/master/Source/Astro/Public/AstroMissionData.h)
- [Mission manager](https://github.com/AstroTechies/ModdingKit/blob/master/Source/Astro/Public/AstroMissionsManager.h)
- [Procedural generation](https://astroneermodding.readthedocs.io/en/latest/guides/proceduralGeneration.html)
- [Diegetic UI](https://astroneermodding.readthedocs.io/en/latest/guides/diegeticUI.html)
- [Metadata standard](https://astroneermodding.readthedocs.io/en/latest/standards/metadatav2.html)
- [Loader Linux setup](https://github.com/atenfyr/AstroModLoader-Classic#linux-setup)

The native integrator and the Classic graphical loader are different executables;
the latter's Linux instructions use Wine. Neither establishes that this expansion
works. Do not adopt security-reduction suggestions in third-party setup instructions.
