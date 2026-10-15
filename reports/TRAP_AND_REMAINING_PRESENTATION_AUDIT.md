# Trap and remaining presentation audit — 2026-09-13

This is an audit, not an implementation pass. Current simulator code was compared with retained MovieTrap and MovieLure references, and the full unit suite was rerun: **103 tests passed**. This pass did not visually replay every animation or certify speaker synchronization.

The extracted TTR phases supply models, animation channels, textures and sounds. They do not contain current TTR Python battle choreography. Findings below identify concrete differences from the available classic source; exact modern parity remains a separate gameplay check.

## Confirmed placement gaps

Current implementation: `trap_movies.py`, functions `place` and `sync`. Reference: original workspace `work/ref-MovieTrap.py`, functions `__createThrownTrapMultiTrack` and `__createPlacedTrapMultiTrack`.

| Gag | Current behavior | Reference behavior / required correction |
| --- | --- | --- |
| Banana Peel | Generic projectile launched at 1.8s with 0.6s flight; pie sound at 2.3s; persistent prop appears at 2.5s | Medium torso release at 2.55s, 0.9s parabola followed by 0.8s slide; animated banana and `TL_banana.ogg`. Preserve its final resting state after flight. |
| Rake | Same generic projectile and pie sound | Medium torso release at 2.5s, 1.1s parabola, rotating rake and `TL_rake_throw_only.ogg` for 1.1s. Reference uses a separate `rake-react` resting prop and body-dependent position offset. |
| Marbles | Same generic projectile and pie sound | Medium torso release at 2.5s; 0.2s fling then 1s roll with native prop channel; `TL_marbles.ogg` at 2.6s. |
| Quicksand / Trapdoor | Persistent prop appears immediately at fixed scale at 2.5s; button and trap sounds both at 2.3s | Grow prop over 1.2s starting at 2.5s. Button at 2.3s for 0.67s, wait 0.3s, then trap sound at 3.27s for 0.5s. Native pushbutton duration instead of forcing 3.5s. |
| TNT | Dedicated corrected placement and activation | Fuse sparks remain missing. Do not undo the previous TNT timing correction. |

The generic thrown prop finishes at 2.4s but the persistent trap appears at 2.5s, leaving a 0.1s scheduling gap. More importantly, the projectile helper is not the individual ground-level throw/slide choreography.

The three dedicated placement sounds already have entries in `assets/battle_movies.json`; the problem is selection/choreography rather than requiring newly invented audio.

## Confirmed activation gaps

Current implementation: `trap_movies.activate`. Reference: `ref-MovieLure.py`, `__createSuitDamageTrack` and `__createSuitResetPosTrack`.

- **Lure and approach are separated.** `battle_movies.base_gag_movie` builds the complete Lure windup with health suppressed; `activate` waits for that interval to finish, then runs a generic 0.7s walk into the trap. Integration should follow each Lure's approach/contact timing.
- **Return movement snaps.** Every ordinary trap finishes with `Func(node.setPos, origin)`. The reference uses a 0.5s backwards walking return. Fix this together with the approach so actors do not receive competing movement intervals.
- **Banana and Marbles props do not perform their reaction choreography.** Missing prop slide/channel playback and shrink-away. Their reference audio starts with a 0.55s pie-throw excerpt followed by body-fall audio; current code only starts body-fall at 0.5s. The pie sound belongs here, not their placement.
- **Rake is incomplete.** Missing two secondary bounces and final shrink; reaction is stretched to 4s instead of the reference 3.125s. Step-on sound starts at 0.5s rather than 0.6s. Use the correct resting reaction prop before adjusting transforms.
- **Quicksand and Trapdoor are oversimplified.** Both use a generic four-second flail and shortened sink/reappear path. Missing spliced/reversed reaction portions, final slip-forward, trap shrink and second landing sound. The reference starts trap audio at 0.7s / 0.8s respectively; current code uses 0.5s for both. Second sounds depend on first clip duration plus the reference wait, not a guessed common timestamp.
- **Trap collisions have logic but lack the source effect.** Engine clears colliding traps; `place` has no collision dust branch corresponding to reference `explode` handling. Cancellation should be visible at the placement contact without briefly showing a surviving trap.

Railroad already has a separate implementation. This pass inspected its placement dispatch, but did not re-certify its entire train/tunnel movie.

## Battle rules checked

Existing tests cover rejecting Trap on lured Cogs, trap persistence after Lure misses, same-round Trap then Lure, simultaneous trap cancellation, Railroad replacement versus simultaneous collision, and SOS restrictions. All passed. No new engine regression was established in this audit. Passing these tests does not prove every TTR battle rule.

## Other requested gaps rechecked

1. **Individual hit damage is still aggregated.** `throw_sequence.movie` and `squirt_sequence.movie` schedule a target's health event at the last contact. Separate bonus colors exist, but early individual hits do not each display their own base damage. The correction needs per-action damage attribution and must not apply the engine total multiple times.
2. **Non-dog expression switching is absent.** `scene_art.configure_head` hides non-neutral eye/muzzle meshes; non-dog heads are static models. The sad-state face needs a verified lifecycle and reset. The available attack source does not establish a universal manually assigned expression for each hit/dodge, so that mapping remains unverified.
3. **Bad Joke body motion remains unverified.** `battle_movies.py` selects native `speak` for damage remotes and returns to the controlled pose. Extracted antenna and body channels being present does not establish the correct body channel/frame range. Do not mark this resolved merely because the interval executes.

## Recommended implementation order

1. Port individual Trap placement, persistent prop selection, and collision effects.
2. Integrate Lure contact with Trap reactions, return walking, and full audio sequences; include TNT fuse sparks.
3. Test same-round and stored traps, misses, collision, A/B/C bodies, and interruption by New Battle.
4. Split per-hit damage display while preserving one authoritative total.
5. Audit sad-state expressions; verify Bad Joke against visible modern gameplay before choosing a replacement body motion.

Preserve user-adjusted UI positions and scales. No runtime source files or battle settings were changed by this audit.
