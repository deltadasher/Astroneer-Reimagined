# Local Codex implementation handoff

## Task and boundaries
Build a genuine Astroneer content expansion from this provisional foundation,
starting with one playable Sylva loop. The user has Steam PC on Linux/Proton and
no current mods. No DLC is assumed. Check with the user before treating the names,
economy, or broader progression overhaul as approved. This repository has **no
Unreal implementation**; packaging these Python/JSON files does not create a mod.

Read applicable repository/local `AGENTS.md` and relevant `.agents/skills` first.
Do not copy proprietary game assets into the repository, commit saves, add secrets,
change security settings, or accept new licenses without appropriate authorization.
Do not auto-install mods or modify the user's live save directory without their
permission. Keep generated game packages out of source control unless specifically
requested and permitted by the upstream licenses.

## 1. Compatibility preflight (stop on mismatch)
Record exact installed Astroneer build, Steam/Proton version, Linux distribution,
architecture, kit commit/release, UE version, and mod-loader/integrator release.
Compare against upstream support rather than guessing from a successful launch.
The kit version supplied in research targets game 1.36.42.0 / UE 4.27.2; the user's
installed version is unknown. Revalidate this at implementation time.

Use current official/community maintainer instructions and verify any downloads.
A native Linux integrator exists, but Proton integration must be verified for this
installation. Do not copy instructions to disable antivirus/firewall or reduce
security. Confirm legal access to required engine/tools; hand off acceptance where
required. Identify a Windows authoring/cooking route before promising mesh/material
content. Running the game through Proton does not prove Linux cooking works.

## 2. Prove one narrow runtime path
Run reference tests first. Inspect current ModdingKit examples/types, then record
real signatures/asset classes in `docs/integration.md`. Do not translate semantic
Python events into invented API calls. Make the smallest supported in-game probe:
initialization and one existing-state read, then persistence across a restart.
Keep diagnostic output free of personal paths and sensitive data in shared reports.

Prove, in sequence: one new resource and inventory round-trip; gas storage and recipe
consumption; one non-destructive site interaction; core-state query on load; one
mission update and durable saved state. Only then author visuals and the full arc.
Choose an existing-world placement strategy explicitly. If the runtime cannot support
an element, report the precise gap and propose a scoped alternative rather than a
fake implementation.

## 3. Implement real assets and adapters
- Resource definitions, icons, storage/transfer behavior, production and recipes
- Lens item plus site interaction with validated planet/site identity
- Authoritative core-state initialization plus change observation/reconciliation
- Native mission definitions/progress notifications, stable IDs, save schema/migration
- Idempotent spawn/restore/retune, with no duplicate resources/rewards on reload
- Multiplayer replication only if deliberately supported and tested

The prototype is an executable specification, not code to embed in Unreal. Port its
ordering and reconciliation rules into the supported runtime representation.
Reference JSON persistence is not compatible with Astroneer saves.

## 4. Cook, package, integrate, and validate
Use a Windows cook if the current maintainer Linux caveat still applies. Record
commands, versions, artifact hashes, dependencies, and any required manual steps.
Before the first modded launch, have the user back up all affected saves outside the
active directory and verify the copied files exist. Use disposable copies/test worlds.
Do not let Steam Cloud overwrite the only backup; do not change sync settings without
permission. Follow the loader's current documented installation/uninstallation flow.

Required runtime checks:
- Fresh world: site discoverable, experiment, gas inventory/transfer, crafting,
  restoration, normal core awakening, retuning, observed changed site behavior
- Initially dormant core: restore first, save/quit, awaken, reload, retune once
- Already-awakened world: discover and restore after installation, no core wait softlock
- Save/reload before and after every mission and while interrupted mid-interaction
- Duplicate interaction/callback, dropped/recrafted lens, full output storage,
  insufficient inputs/power, leave/return to Sylva, and multiple load cycles
- Only Sylva's relevant core changes this site's gate; unrelated core events do not
- Backup rollback; removal from a disposable modded save, with honest limitations
- Proton launch/loader detection, resources/material rendering, persistence and logs
- If multiplayer is claimed: host/client inventory, authority, mission sync and reconnect

## Completion definition
A playable slice requires real cooked assets plus a verified integration package and
successful in-game tests on the declared build/Proton combination. Record evidence,
known failures, and compatibility limits. A logic-test pass or successful cook alone
is not completion. Do not describe broader planet content as present until built.
