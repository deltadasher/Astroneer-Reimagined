# Build and verification status

Recorded 2026-10-06 UTC. Source checkpoint, not a playable release.

| Stage | Status | Evidence / limit |
| --- | --- | --- |
| Phase-one design and progression reference | Retained | `content/resonance.json`, `prototype/progression.py`; not runtime code |
| Original source assets | Authored | Five FBXs, editable Blender source, eight named materials, builder and studio previews in `assets/resonance/` |
| Independent mesh inspection | Passed | Five Blender round-trips; identity scale, shared pivots, UVs/materials, closed positive-volume components, no nonmanifold or degenerate faces |
| UE editor authoring source | Written, not executed | Imports meshes/materials, creates item Blueprint definitions/recipe links, site visual shell and six mission rows |
| Offline tests and Python compilation | Passed | 32 tests; input/static/reference checks and synthetic staging fixtures only |
| Generated Unreal assets | Not generated | No `.uasset`; editor reflection, Blueprint compile and reopen checks pending |
| Inventory/catalog/slot behavior | Unimplemented/unverified | Definition authoring is not functional registration; icons, body slots and real fit pending |
| Gas and production loop | Unimplemented | Unbound descriptor only; container units, production and recipe station pending |
| Site gameplay and world persistence | Unimplemented | Visual base shell only; state components, placement, interaction, save/load, authority and migration pending |
| Mission/core integration | Unimplemented | Data rows/custom tags only; event producers, activation and authoritative state reconciliation pending |
| Windows cook and loader package | Not run | No installable `.pak` or automatic runtime metadata emitted |
| Astroneer / Linux-Proton / multiplayer | Not run | Actual versions, rendering, save safety and compatibility unknown |

Follow `unreal-authoring.md` for source generation, `source-validation.md` for
independent evidence, `staging.md` for the bounded staging helper, and
`local-agent-handoff.md` for the remaining runtime acceptance checks. A source
suite pass is not an editor, cook, game or save-compatibility pass.
