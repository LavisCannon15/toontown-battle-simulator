# Two-Face, Money Bags, Spin Doctor and Head Hunter

## Evidence and limits

Compared all 17 configured attacks with retained `ref-MovieSuitAttacks.py`, `ref-BattleProps.py` and `ref-BattleParticles.py`, then loaded the actual bundled TTR models. Extracted phase files contain models, animation channels and sounds; they do not contain modern TTR battle movie sequencing code.

Classic source: https://github.com/open-toontown/open-toontown/blob/master/toontown/battle/MovieSuitAttacks.py
New particle configurations: https://github.com/open-toontown/resources/tree/master/phase_5/etc (`headShrinkCloud.ptf`, `pixieDrop.ptf`). Reviewed before use; neither references external textures. These configurations are now bundled in `assets/particle_effects`.

## Findings and changes

| Cog | Attack | Result |
|---|---|---|
| Two-Face | Evil Eye | Removed the generic hand-held prop. Eye now grows beside the face, turns, flies and rolls toward/past the Toon. Slowed glower hold; separated reaction onset from damage display. |
| Two-Face | Hang Up | Uses Two-Face-specific phone/receiver offsets and scales. Receiver begins in the left hand, transfers to the right, and returns to the phone before shrinking away. |
| Two-Face | Razzle Dazzle | Existing explicit smile-sign/particle sequence agrees with classic source; retained and exercised hit/miss. |
| Two-Face | Red Tape | Existing Two-Face leftward hand offset and thrown tape/body tube retained; exercised hit/miss. |
| Money Bags | Liquidate | Corrected initial cloud bounds to actor-local coordinates. Retained source cloud/rain/puddle and melt/jump sequence. |
| Money Bags | Market Crash | Replaced straight generic projectile with growing/spinning newspaper, ballistic flight, landing/slide and source reaction slices. |
| Money Bags | Power Tie | Native held origin, growth, C-body release delay, billboard flight and distinct hit/miss destination. Impact sound only on hit. |
| Money Bags | Money Talks | Previously no effect or sound. Added a green jargon wall using bundled suit-particle art, teamward travel, duck misses and extracted hit/miss sounds. **Reconstruction, not verified TTR timing/choreography.** |
| Spin Doctor | Paradigm Shift | Restored offset spray, yellow lift effects, Toon rise/shake/fall, think/slip reaction and held jump dodge. |
| Spin Doctor | Quake | Restored repeated slip-forward reactions and three jump dodges; separated displayed damage from reaction onset. |
| Spin Doctor | Spin | Restored three effect bands and progressive Toon rotation with return to original heading. Uses bundled hit/miss sounds. |
| Spin Doctor | Write Off | Existing pencil/pad/checkmark trajectory retained. Limited pen sound to source 0.9-second segment before ding. |
| Head Hunter | Fountain Pen | Static pen attached by its native hand origin; spray from pen-tip joint, pen spill, black splat and temporary ink-darkened head. Source duck segment on miss. |
| Head Hunter | Rolodex | Static prop channel, source grip, grow/hold/shrink lifetime and body-specific particle timing. |
| Head Hunter | Glower Power | Head-Hunter-specific dagger origins, six staggered daggers, 0.1-second growth and 0.3-second flight. |
| Head Hunter | Half Windsor | Native grip/rotation/scale, source release delay, offset face/behind destinations and conked/cringe reaction. |
| Head Hunter | Head Shrink | Restored circling cloud, falling particles, actual head shrink and overshoot recovery, sounds and spliced reactions. |

Distances are adapted to the simulator's 0.62 Toon scale. These are source-derived reconstructions on the extracted models, not a claim of frame-for-frame modern TTR parity. Money Talks' retained speaking channel, word layout, motion, reaction and cue timing require modern footage/code to verify. Documented green-wall behavior: https://toontownrewritten.wiki/Money_Talks . Other source adaptations include scene formation rings and the simulator's simplified Toon rig/face-height conventions.

## Lifecycle protections

Movement/head scale have cleanup restorers for interruption/new battle. Fatal damage stops the affected Toon's custom reaction, restores its transform, then permits sadness immediately. Group attacks now track custom reactions per Toon, preventing one Toon going sad from stopping other Toons' reactions.

## Verification

- `tests/check_four_cog_attacks.py`: real extracted models; all 17 attacks hit/miss; handoff, prop bounds, spin, lift, head scale, health and cleanup checks.
- `tests/check_four_cog_attacks.py --shared`: the other Cog/body types using changed shared routines.
- `tests/check_four_cog_cleanup.py`: fatal damage, mixed group outcomes and interrupted animation restoration.
- Rendered eight representative attacks; inspected `work/four-cog-visuals.jpg`.
- Existing unit suite: 93 tests pass.

No battle probabilities, damage formulas or customized UI positions were changed.
