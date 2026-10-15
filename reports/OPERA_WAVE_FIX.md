# Opera Singer sound-wave origin

The reported misplaced 2D wave was parented to the Toon root at its feet. The reference MovieSound.__createToonInterval instead positions the effect from the singer instrument at local offset (0, 1.6, -.18), converts that point into render coordinates, and lets the effect run in world space.

Applied that origin at playback time 2.8, after the prop is attached and growing. Restored the source two-stage instrument growth (.85 then 1.1), six-second hold, and .1-second shrink so the mouth offset is sampled at the correct instrument size. Kept the reference particle configuration scale, adjusted for this simulator's Toon body scale, rather than overriding it with 1.2. Emission stops after 2.5 seconds and existing particles finish over the remaining 3.5 seconds.

Checks verify the effect's position equals the singer-relative reference point at launch, render parenting, growth/hold/shrink timestamps, and cleanup. Source: existing local ref-MovieSound.py, __doOpera and __createToonInterval. No new external assets were required.
