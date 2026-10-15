# Current source comparison — September 12, 2026

## Evidence boundary

Rechecked the bundled extracted library: 12,569 files, including 4,104 BAM files and 1,265 OGG files; no `.py`, `.pyc`, or `.pyo` files. The import manifest records the installed phase archives. These resources establish available artwork, rigs, animation clips and sounds, not server battle calculations or the code that sequences movies.

The readable calculator in `work/rules-reference/BattleCalculatorAI.py` is public classic Toontown reference code, not extracted current TTR source. Differences from that calculator are comparison findings, not automatically TTR bugs. Current TTR overrides and unresolved evidence remain recorded in RULES_AND_REWARDS_UPDATE.md.

## Code comparison findings

| Area | Simulator implementation | Comparison/status |
|---|---|---|
| Accuracy | `Battle.accuracy` combines base, training, defense and bonuses; caps through `combat_rules.py`. | Classic calculator also combines these components and caps accuracy. Current TTR soft-cap equivalence remains unresolved; retain the user's chosen explicit limitation. |
| Shared hit rolls | `resolve_events` caches rolls by tuple of participating actions. | Classic `__calcToonAtkHit` shares a preceding same-track outcome using target and Lure conditions. These algorithms are not identical; overlapping group/single actions need scenario comparisons. |
| Lured targets | Automatic damaging hits in applicable cases, Drop rejection, and Sound unluring are implemented. | Broad behavior agrees with the inspected classic hit calculation; this does not establish every mixed-target or current TTR probability. |
| Trap conflicts | Ordinary same-target traps cancel; prior-round Railroad replacement has a separate rule. | Classic code retains a `TRAP_CONFLICT` sentinel and treats NPC traps separately. Simulator clears to `None`; combinations involving multiple Trap SOS calls require explicit comparison before claiming equivalence. Do not overwrite TTR Railroad changes with classic behavior. |
| SOS plus ordinary gags | SOS effects resolve separately before ordinary actions in their track. | Not a unified damage/combo calculation. Known limitation remains for shared damage bonuses, stun accounting and ordering. |
| Cog attack selection | Uses catalog weights, including documented fallback estimates. | Classic tables are available; current TTR probabilities are not established by phase assets. See COG_PROBABILITY_AUDIT.json. |
| Remotes | Applies duration, ticks, expiry and a receiving animation; rejects replacement and competing same-target remotes. | Receiver clips prove asset availability, not replacement priority or server event order. Those rules remain unresolved. |
| Doodles | Per-trick training and success/healing interpolation; explicit mood. | Public pet code includes a broader trait/mood system. Full fatigue and recovery are absent. |
| Unites | Separate from the round action; per-caster supply/cooldown; available during playback. | GUI applies effects to living battle teammates. Numerical current TTR spatial range is unverified; no exact spatial-equivalence claim. |
| Running and defeat | Escaped Toons leave without advancing the round; no living Toons triggers Cog victory; cards disappear. | Covered by the new presentation regression checks. These tests establish simulator behavior, not an extracted server implementation. |
| Presentation | Bundled TTR assets with reference-informed choreography. | Tee Off now uses reference hand attachment/rotation; attack captions, Lure misses, remote receiver and reward overlays were checked. Remaining movie timing, camera, trajectories and sound synchronization still require individual audits. |

## Next comparison priorities

1. Build concrete overlapping group/single gag and SOS scenarios, comparing hit sharing, damage bonuses and stun accounting.
2. Compare multi-Trap/SOS cases without importing obsolete classic exceptions into TTR mode.
3. Resolve remote priority, Doodle fatigue and Unite spatial behavior only where evidence supports the implementation.
4. Continue per-attack movie inspection: grip, prop scale, impact frame, reaction, disappearance and audio timing. Loading a resource successfully is insufficient to establish correct choreography.

This review changed no combat formulas. The 81-test result and presentation/integration checks are from the preceding implementation verification; they are not proof of full live-game equivalence.
