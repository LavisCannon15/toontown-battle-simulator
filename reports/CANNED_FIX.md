# Canned

Compared retained MovieSuitAttacks.doCanned (1411–1490), using the bundled extracted can model and native Cog/Toon animations. Dedicated canned_movie.py replaces the generic straight projectile.

Source body-dependent release: Corporate Raider C body 2.43, Downsizer B body 3.13; 1.5-second arc. Reference right-hand transform and initial scale 6. Hit can grows/rotates during flight, attaches to Toon hips and clears after 2.4; one visible Toon LOD needs one can. Extracted can geometry would be oversized/partly underground at the old raw scale, so fit its oriented bounds to 80% of Toon height, preserving source rotation and scale proportions. Rendered can surrounds torso with head/feet visible.

Miss can follows all five source ground/bounce points and spin stages, waits 1.1, then shrinks .3. Hit reaction starts on arrival: struggle .7 then slip-backward from .45. Damage occurs release+2.4, with immediate sadness overriding ordinary reaction on fatal hits. Body-specific sidestep dodge timing retained. Toss sound starts 2.6; impact sound follows on hits only.

Tests/check_canned.py passes both Cog body types on hit/miss, held/flight/hip attachment, actual can bounds/center/ground clearance, delayed live damage and cleanup. Rendered and inspected the fitted hit can. All 93 battle-rule tests passed. Classic-source sequencing is adapted to simulator dimensions, not independently verified current TTR movie code.
