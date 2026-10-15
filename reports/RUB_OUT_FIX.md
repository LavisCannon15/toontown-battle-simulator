# Rub Out audit and fix

Reference: retained MovieSuitAttacks.doRubOut (1002–1073), BattleParticles.__makeRubOut (144), and bundled extracted TTR props/sprites/channels. The phase assets supply art, not modern TTR sequencing; this follows the classic source adapted to simulator dimensions.

The generic movie had no RubOut particle-factory mapping, no staged disappearance, and incorrect prop lifetimes. The dedicated rub_out_movie.py now implements:
- Left-hand pad and right-hand pencil with source positions/rotations. Both appear at .5, grow .5, remain 2.57, then shrink .5.
- Hit reaction at 2.2; jump dodge at 2.0; Rub Out sound at 1.7.
- Head, torso, legs fade over .2 seconds beginning 2.2, 2.8, 3.4. Visibility restores at 4.6, preserving original color-scale and transparency attributes.
- Hit-only colored eraser particles at 2.5, 3.6, 4.7, emitting .5 seconds each. Uses source demotionUnFreeze config, extracted snow-particle sprite, and reference sprite sizes (.03/.02 to zero). Retains config scale multiplied by simulator scene scale. Part locations derive from assembled Toon geometry; colors follow simulator Toon colors.
- Cancellation restores visibility via movie cleanup. Fatal hits prioritize immediate sadness instead of erasure.

Verified real-asset hit/miss, progressive part fading, effects at distinct heights, hand attachments, exact-once live damage, fatal hit, and cancellation restoration (including transparency) in tests/check_rub_out.py. Rendered and inspected head-erasure stage. All 93 battle-rule unit tests passed.
