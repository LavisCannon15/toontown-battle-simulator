# Schmooze and Micromanager size

Schmooze: compared retained MovieSuitAttacks.doSchmooze (2289–2346). Added missing classic particle configs from:
https://raw.githubusercontent.com/open-toontown/resources/master/phase_5/etc/schmoozeUpperSpray.ptf
https://raw.githubusercontent.com/open-toontown/resources/master/phase_5/etc/schmoozeLowerSpray.ptf
Only model-path extension normalized; textures are the bundled extracted TTR schmooze-genius/instant/master/viz sprites.

Dedicated schmooze_movie.py emits all four blue textures in upper/lower pairs. Upper starts 1.3+i*.65 for .8; lower starts .7 later for 1.0. Native speak gesture faces target. Hit repeats conked segments; miss splices duck segments, using source A/B/C body onset timing. Damage number is onset+1.1, miss number onset+1.9. Fatal live damage stops the custom reaction. Classic function contains no sound track.

Micromanager: retained Suit.py gives scale=2.5/cSize, cSize=4.14, height=3.25. scene_art.py previously normalized every Cog to 3.5+.06*level, making Micromanager oversized. It now uses (2.5/4.14)*.62, fixed across levels and applied to its skeletal variant too. Actual rendered normal-model height measures 2.013 scene units. Name label follows the reduced height. Other Cog sizes remain as previously configured; this is a scoped Micromanager fix, not a full Cog-size audit.

Validation: tests/check_schmooze_size.py passes both Schmooze Cogs (Glad Hander/The Mingler), hit/miss, eight staggered effects, live damage, cleanup; Micromanager normal/skeleton scale at two levels and measured geometry. Schmooze rendered and inspected. All 93 battle-rule tests passed. Uses classic-source choreography with extracted TTR assets; modern TTR movie-code parity is not independently verified.
