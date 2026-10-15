# Animation audit: Lipstick, Squirt Gun, Cane, Tee Off, Hypno, High Dive, Flood

Applied September 12, 2026. Bundled TTR phase assets remain inside this project.

- Lipstick: flying lips grow to reference scale 3, originate at the performing hand, and fly at the smooch release time. The hand is sampled during playback rather than posing the live Toon while constructing its movie.
- Squirt Gun: reference right-hand position (.28, .1, .08) and rotation (85.6, -4.44, 94.43); spray originates at the model's joint_nozzle locator.
- Bamboo Cane: left-hand cane (-.28, 0, .14), roll -150; right-hand hat (.23, .09, .69), heading 180.
- Tee Off: close-up renders confirmed the extracted club already loads and is visible. Preserve its source left-hand transform and scale 1.1. Keep it through the full modern swing instead of removing it after a fixed 5.2 seconds; aim the Cog at the target and restore its heading. Explicit duck miss reaction.
- Hypno-goggles: native-speed 2.2-second prop interval, rather than compressing its entire animation into that interval. Native 3.1-second Cog reaction, forward movement at 3.3 seconds over .7 seconds, followed by neutral. Magnet and dollar reactions remain separate.
- High Dive: dynamic Toon-relative prop/ladder destinations; reference ladder/glass scales and growth; native climb through frame 116 without an additional upward root interpolation; fade, small swimmer, animated extracted splashdown, recovery jump, and transform cleanup.
- Flood the Market: removed classic Glower fallback. Added a magic gesture, expanding blue particle pool, bundled hit/miss sounds, backward hit reaction, and jump dodge. This is a reconstruction: exact modern gesture selection, particle settings, and event timestamps remain unverified. Do not represent it as a port of TTR's private movie code.

## Evidence and limits

Classic MovieHeal, MovieSquirt, MovieLure and MovieSuitAttacks references in the existing local work archive supplied transforms and timing for the six classic moves. High Dive's splash uses the extracted SZ_splashdown model/channel; secondary ripple and SplashLines layers are not yet reproduced.

The phase files contain models, animation channels, textures, and audio, not current TTR battle sequencing Python. Flood the Market is a default fallback in the classic source. Its modern appearance is described at https://toontownrewritten.wiki/Flood_the_Market. TTR confirms new animations for this attack at https://www.toontownrewritten.com/news/release-notes/367.

## Verification

91 existing unit tests passed. `tests/check_seven_movies.py` checks attachment sides, transforms, nozzle, lips scale, Hypno movement, native climb root handling, splash visibility, and recovery scale. Complete live rounds for all five gag moves completed with displayed HP equal to engine HP. Tee Off and Flood the Market movies completed for hit and miss. Rendered frames inspected for the club, Squirt Gun, Cane, and High Dive. Modern TTR visual parity is not fully established by these checks.
