# Astroneer-Reimagined

Initial expansion theme: **Resonance (provisional)**.

**Design and executable logic reference only. This is not an installable Astroneer mod.**
There are no Unreal assets, runtime hooks, loader files, or cooked packages here.
The theme, names, economy, and mission arc are proposals awaiting playtesting and user review.

## Goal
A base-game-first expansion for Steam PC on Linux/Proton, adding resources,
experiments, missions, and meaningful changes before and after a planet's core
awakens. No DLC assumed. Start with a single Sylva site to prove the full loop,
then expand only after save/load and compatibility checks pass.

## Contents
- `content/resonance.json`: engine-independent proposed content definitions
- `prototype/progression.py`: pure Python reference for mission ordering and core-state reconciliation
- `tests/test_progression.py`: repeatable logic checks; these do not test Astroneer
- `docs/design.md`: first playable slice and expansion direction
- `docs/integration.md`: runtime integration requirements and evidence gaps
- `docs/local-agent-handoff.md`: bounded implementation and verification plan
- `docs/status.md`: precise build and test status

## Run the reference tests
Python 3.10+; standard library only. From this directory:

```sh
python3 -m unittest discover -s tests -v
```

No game installation, Steam files, network, or saves are read or changed by this command.
The JSON format is our design format, **not** a ModdingKit import schema.

## Critical build boundary
The community ModdingKit currently documented to us uses UE 4.27.2 and targets
Astroneer 1.36.42.0. This does not establish compatibility with the user's installed
build. Verify exact versions before implementing. The kit documents Linux cooking
issues with meshes/materials; use a validated Windows cook for the initial playable
package. Linux/Proton deployment is a separate test from authoring/cooking.

Back up saves outside the active save directory before loading any experimental
package. Never test the first build against the only copy of a valued world.
See the [integration evidence and gaps](docs/integration.md).
