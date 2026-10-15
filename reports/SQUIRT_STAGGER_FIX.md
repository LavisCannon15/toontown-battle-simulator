# Squirt team timing

Cause: `audited_gags.track_movie` placed every Squirt builder directly in a Parallel, so all four Fire Hoses began at time zero.

Fix: `squirt_sequence.py` groups attacks by target, stably sorts groups by their number of attacks, and wraps each entire gag movie in its source delay. `MovieSquirt.doSquirts`, `__doSuitSquirts`, and `__doSquirt` apply this ordering. `BattleBase.py` defines TOON_SQUIRT_DELAY=0.5 and TOON_SQUIRT_SUIT_DELAY=1.0. Four hoses on one Cog now start at 0, 0.5, 1.0, 1.5 seconds; four separate targets start at 0, 1, 2, 3 seconds. Animations, props, spray and sound share the same offset.

The scheduler covers the ordinary Squirt track builders (including mixed levels). Geyser retains its existing specialized movie path. The engine's aggregated damage is applied once per target on its final applicable contact; this does not introduce per-gag damage breakdowns. Miss reactions occur once per target, using its earliest scheduled contact/dodge.

Validation: tests/check_squirt_stagger.py loads four real Fire Hose props and checks actual start offsets for shared, separate and mixed target arrangements, hit/miss, aggregate damage count and cleanup. Also checks mixed Squirt scheduling. Existing 93 unit tests pass.

Sources: retained ref-MovieSquirt.py and work/ref-BattleBase.py, fetched from https://github.com/open-toontown/open-toontown/blob/master/toontown/battle/BattleBase.py . These are classic source timings, not a claim that modern TTR sequencing code was extracted from phase files.
