# Bounce Check, Red Tape, Write Off and Liquidate

Source: retained classic MovieSuitAttacks.py functions doBounceCheck (2600), doRedTape (2406), doWriteOff (1115), doLiquidate (2944), getThrowTrack/getThrowEndPoint; ref-OTPGlobals.py Toon body scales. Models, animation channels, sprites and sounds come from the project's bundled extracted TTR assets. These phase assets do not contain current TTR sequencing code; this is a classic-source choreography correction, not a claim of frame-perfect current TTR parity.

The generic attack prop player omitted essential sequences. Dedicated classic_cog_movies.py now supplies:

- Bounce Check: right-hand transform, growth, body-specific release/impact timing, gravity-driven bounces, extra bounce on miss, and two bounce sound cues. Classic distances and gravity are converted to the simulator's .62 scene scale.
- Red Tape: grows in the right hand, flies to the target, and wraps a hit Toon using the extracted tube attached to the hips. Misses have no wrap. Species body scale and dog/horse variants are respected. One tube serves the simulator's rendered Toon instead of the classic three LOD copies.
- Write Off (interpreted from “writing check”): native pencil/pad transforms and lifetimes, extracted checkmark sprite launched from the pencil, hit/miss destination, separate writing/ding cues.
- Liquidate: delayed Cog gesture, cloud grows over Cog then travels over the target, three staggered source rain effects, native cloud animation segments, blue ground puddle only on hit, melt/wait/jump recovery. Immediate sad handling still takes precedence over ordinary reactions.

Presentation is adapted to this simulator's body proportions and scene scale. Target face/torso heights currently use its existing approximate scene heights (2/1.2), so they are not a full Toon-DNA dimension port.

Validation: 26 hit/miss real-model sequences across all 13 applicable Cog/attack pairs; sprite/wrap visibility, cloud location, flight parent, cleanup; 93 battle-rule unit tests. Rendered all four sequences for inspection. Dedicated live-health check verifies damage is applied once and reaction tracks finish.
