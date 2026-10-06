# Design proposal: Resonance

Status: unapproved working direction; all names and numbers are provisional.
Target: base-game Steam PC, played on Linux/Proton; single-player first.

## Experience
Core activation should change a place the player already knows. A dormant Sylva
array responds to experiments before the core awakens. Restoring it gives purpose
to a new gas and material. After awakening, returning with the same reusable lens
reveals a new mode and an exploration clue. Nothing in the slice replaces the
vanilla core activation recipe or blocks vanilla progression.

## First playable slice
1. **Discover:** find one readable, persistent array site on Sylva. Give the player
   a reliable way to locate it; procedural placement/insertion into existing worlds
   is an engineering decision, not assumed solved.
2. **Experiment:** interact with the array to obtain Resonant Vapour. Sampling must
   work both before and after awakening so late installations cannot deadlock.
3. **Craft:** turn quartz and vapour into Echo Glass, then build a reusable Tuning
   Lens. Candidate costs live in `content/resonance.json`; actual crafting station,
   unlock cost, gas consumption units, power, and duration remain to be verified.
4. **Restore:** use the lens at the discovered site. Restoration does not consume
   the lens. An interrupted interaction must not grant completion or destroy items.
5. **Awaken:** awaken Sylva through the normal game. An already-awakened core counts
   after restoration; querying current state is mandatory, not only listening for
   a future activation event.
6. **Retune:** revisit and use the lens again. The restored site's output improves,
   its visual/audio behavior changes, and it reveals a local exploration clue.

Mission completion is one-time, but experiments remain repeatable. Start with
capability unlocks rather than item rewards to reduce duplicate-reward risks.
Exact output/yield and clue reward are deliberately unbalanced until in-game tests.

## Avoid softlocks
- Lost lens: craft another with renewable inputs; avoid unique irreplaceable items
- Old save with awakened Sylva: replay discovery/experiment/craft/restore, then
  immediately satisfy the core requirement and allow retuning
- Core awakens mid-arc: retain the observation and reconcile after restoration
- Site not generated in an existing world: require a tested insertion or
  player-deployable fallback before claiming existing-save compatibility
- Mod removed: do not promise safe vanilla loading with custom objects; test only
  on copies and preserve the pre-mod backup for rollback
- Failed persistence/migration: do not silently reset progression or overwrite
  unknown data; report the issue and preserve the save copy

## What makes the eventual expansion larger
Once one complete loop works, add distinct experiments and resources to other
planets. Each planet should have a different pre-core production constraint and
post-core utility, with interplanetary recipes that reward logistics. Add optional
late-game mission branches that use multiple awakened worlds. These are roadmap
ideas, not implemented content or approved scope for an initial package.

## Design decisions still open
- User approval of theme/names and how much vanilla progression should change
- Single-player-only release versus co-op authority and replication support
- Reliable site placement on both fresh and existing saves
- Crafting stations/unlocks and numerical economy; gas capacity semantics
- Retuned-site reward that is useful without trivializing vanilla progression
