# Developer staging, not a playable release

`tools/stage_mod.py` copies explicitly listed, mod-owned cooked packages and their
`.uexp`/`.ubulk` sidecars into a **new** directory. It never cooks, packs, installs,
modifies a game/save, or overwrites an existing staging directory. A repeat run
fails safely; choose another output or review/remove the old directory yourself.
Concurrent invocations to the same destination allow only one writer.

There is deliberately no ready-to-install `metadata.json` in this source bundle.
The operator must supply a reviewed staging manifest. The manifest below is **our
helper's input format**, not a ModdingKit schema. `metadata` is the real v2 loader
object. Example values are illustrative, not proof these assets exist:

```json
{
  "format_version": 1,
  "author_reviewed": false,
  "metadata": {
    "schema_version": 2,
    "name": "Astroneer Reimagined: Resonance (development)",
    "mod_id": "AstroneerReimagined",
    "author": "deltadasher",
    "version": "0.1.0-dev",
    "game_build": "1.36.42.0",
    "sync": "serverclient",
    "integrator": {},
    "dependencies": {}
  },
  "packages": [
    "/Game/Mods/deltadasher/AstroneerReimagined/Resonance/Items/EchoGlass_IT"
  ]
}
```

Before changing `author_reviewed` to true:
- Supply the actual installed/cooked game build, not a compatibility guess
- List **all** mod-owned transitive dependencies, including materials and meshes;
  the helper cannot reconstruct an Unreal dependency graph
- Inspect graph implementation and generation reports. Do not register mission
  trailheads without objective event producers, a static site shell as a gameplay
  controller, or the unbound gas ItemType as working atmospheric content
- Check the assets were saved and cooked by UE 4.27.2 for Windows, with mesh
  `Has Navigation Data` disabled
- Do not copy vanilla proxy assets into the package

From the repository root, after the real cook:

```sh
python tools/stage_mod.py reviewed-manifest.json /path/to/Astro/Saved/Cooked/WindowsNoEditor /path/to/new-stage > staging-report.json
```

The output parent must exist. UTF-8 metadata is written at the staging root;
assets use `Astro/Content/...` paths. The stdout audit contains SHA-256 hashes and a
suggested pak filename. Keep this report outside the staging tree. A normal
exception removes the newly created staging tree; a killed process can leave a
partial tree, which a rerun refuses to overwrite. No `.pak` is emitted.

Supported metadata is intentionally a narrow v2 subset: persistent actors,
mission trailheads, linked actor components, item-list entries and string version
dependencies. All referenced mod packages must be in the explicit package list.
This is a structural check, **not** a full metadata-schema validator. It does not
verify UE package headers, engine serialization, dependency compatibility, asset
class types, graph behavior, or multiplayer/save safety. Nonempty test fixtures
exercise filesystem safety only; passing them is not cook/runtime validation.
The source-folder name is an operator guardrail, not cryptographic proof of a cook.

Sources reviewed 2026-10-06:
- [Maintainer metadata v2 standard](https://astroneermodding.readthedocs.io/en/latest/standards/metadatav2.html)
- [Maintainer cooking and packaging guide](https://astroneermodding.readthedocs.io/en/latest/guides/kitModding.html)
