# Build and verification status

Recorded: 2026-10-06 UTC. This file describes this source foundation, not a release.

| Stage | Status | Evidence / limit |
| --- | --- | --- |
| Provisional first-slice design | Written | `docs/design.md`; user approval pending |
| Engine-independent content definitions | Written | `content/resonance.json`; not a kit import format |
| Mission ordering/state reference | Implemented | `prototype/progression.py`; pure Python only |
| Reference test suite | Passed | 15 tests, `python3 -m unittest discover -s tests -v` |
| Independent reference review | Passed | Ordering, repeat-event idempotence, core catch-up, serialization reviewed; no game execution |
| Installed game/Proton version | Unknown | User's local preflight required |
| Kit API bindings and asset classes | Unimplemented | Inspect current kit; record actual supported types |
| Resource, gas and recipe assets | Unimplemented | No inventory, crafting or gas behavior exists in game |
| Site placement/interaction/visuals | Unimplemented | Fresh/existing save support unresolved |
| Native mission/core integration | Unimplemented | Reference semantic events have no runtime producers |
| Real save persistence/migration | Unimplemented | Reference JSON is not an Astroneer save format |
| Unreal build/cook | Not run | No engine, project or licensed game assets used |
| Mod package/integrator deployment | Not run | No installable output exists |
| In-game / Linux-Proton tests | Not run | Requires legitimate game/toolchain and disposable save copies |
| Repository destination | [Astroneer-Reimagined](https://github.com/deltadasher/Astroneer-Reimagined) | Source checkpoint; see repository commit history for published revisions |

The suite covers new saves; progress before awakening; a core awakened before or
at each intermediate mission; repeat and out-of-order events; save/reload at each
step; unsupported/corrupt reference state; mission/recipe references; and lens-free,
repeatable sample availability in the design data. These assertions do not prove
resource reachability, inventory behavior, or persistence in the actual game.

The next useful milestone is a verified runtime probe and one real resource loop,
not a zip of this reference presented as a playable mod.
