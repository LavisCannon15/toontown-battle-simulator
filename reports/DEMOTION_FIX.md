# Demotion

Audited retained MovieSuitAttacks.doDemotion (1373–1408), its spliced-animation helpers, and BattleParticles' Demotion factories. Uses existing bundled extracted TTR animations/snow sprite and retained classic particle configurations. Phase assets do not supply modern TTR sequencing code.

Dedicated demotion_movie.py now implements:
- Micromanager's native magic1 gesture, aimed at the selected Toon.
- Snow spray .7–1.8; face-centered freezing effect 1.4–4.3; unfreezing burst 6.65–7.15. Freeze/breakup effects occur only on hits; particle scale respects config scale and simulator proportions.
- Cringe begins at 1.01. Segments 0–.5, .5–.9, .9–1.2, 1.2–1.5 play over .5/.5/.5/.6 seconds, hold 2.6, then resume from 1.5. Uses frame bounds/rates rather than compressing the entire animation. Source's sampled lerp sequence is represented by continuous native animation segments with matching intended durations.
- Damage at 2.3, independently from reaction onset. Fatal live damage pauses the custom reaction and plays sadness immediately. Miss uses duck from .8 with the reference near-zero start and missed text at 1.6001.
- Demotion audio begins at 1.2. Finite particle and reaction cleanup supports cancellation.

Tests/check_demotion.py passes frozen-pose hold, face-effect heights, hit/miss, exact health timing, fatal-hit and cancellation checks. Rendered and visually inspected spray plus Toon reaction. All 93 battle-rule unit tests passed. This is classic-source choreography adapted to simulator dimensions, not independently verified frame-perfect modern TTR behavior.
