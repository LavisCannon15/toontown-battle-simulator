# Crunch and Downsize

Interpreted “Number Cruncher's crash attack” as Crunch, one of its four named attacks. Compared retained MovieSuitAttacks.doCrunch (2881–2941) and doDownsize (1492–1536).

Crunch: added 5–9 black digit sprites clustered in the right hand, appearing/growing .9–1.5 and removed at 3.2; two number spills and randomized number sprays from 3.03–3.63. Uses extracted audit-one through audit-six art and a separate presentation RNG, leaving combat randomness unchanged. Added missing classic numberSpray config from https://raw.githubusercontent.com/open-toontown/resources/master/phase_5/etc/numberSpray.ptf (only .bam extension normalized). Toon performs the reference cringe slices then slip-forward; damage at 4.7 and dodge at 3.6.

Downsize: source spray at 1.0, hit-only target cloud at 2.1; damage/reaction at 2.3, miss dodge .6. Toon scale sequence begins 2.8: .44/.36/.42/.38/.4, holds 2.1 seconds, then restores with 1.5/.5/1.2/.8/1 overshoot sequence. Saves original scale and restores on cancellation; fatal hits skip shrinking. Native juggle, lose forward/reverse, struggle and sidestep-right splice replaces generic cringe. The lose slice is only part of the ordinary animation; it does not change battle status. Immediate actual sadness remains in the health path.

Dedicated implementation: crunch_downsize_movies.py. Assets remain bundled TTR models/animation/sprites; classic source timings are adapted to simulator character dimensions, not independently verified modern TTR code parity.

Validation: tests/check_crunch_downsize.py passes hit/miss/fatal/cancel variants, hand numbers, emitter counts, combat RNG isolation, exact-once live damage, shrink amount and scale restoration, cleanup. Both effects rendered and visually inspected. All 93 battle-rule unit tests passed.
