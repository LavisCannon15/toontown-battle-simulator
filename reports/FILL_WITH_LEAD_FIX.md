# Fill With Lead

Compared classic MovieSuitAttacks.doFillWithLead (lines 850–941 in retained reference) with the generic movie and bundled extracted assets. Phase files provide art/channels; they do not establish current TTR sequencing code.

Fixed in fill_with_lead_movie.py:
- Pencil in right hand: source transform, appear .7, grow .2, hold 3.2, shrink .5.
- Sharpener in left hand: source transform, appear 1.3, grow .5, hold 2.3, shrink .5.
- Source black roll-o-dex lead spray begins 2.5, emits 1.9; particles drain before cleanup.
- Hit-only smother effects at head, torso and legs begin 3.5/4.2/4.9. Previous generic path stacked all three effects at one default location. Heights use this simulator's assembled Toon geometry, adapting the classic DNA-height approach.
- Staged blackening at 3.7/4.4/5.1; restores at 7.6. Original per-mesh color scales are saved and restored, including cancellation through New Battle.
- Repeated conked segments follow the reference splice instead of one compressed reaction. Damage at 4.5; body-duration-relative dodge and miss label. Fatal damage interrupts these ordinary flinches, preserving immediate sadness.
- The classic function has no sound track, so no invented sound was added.

Validation: real-asset hit, miss, interruption and lethal-hit checks in tests/check_fill_with_lead.py; particle heights, hand attachments, exact-once live damage, color restoration and cleanup passed. Render inspected for the temporary darkening. All 93 battle-rule unit tests passed. This is classic-source behavior adapted to the simulator's scale, not independently verified frame-perfect modern TTR choreography.
