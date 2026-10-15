# Rubber Stamp

Compared retained MovieSuitAttacks.doRubberStamp and __makeCancelledNodePath plus the classic English MovieSuitCancelled string with the simulator. Bundled extracted TTR models, sound and Cog font are used; current TTR movie code is not contained in phase assets.

Dedicated rubber_stamp_movie.py replaces the generic sequence:
- Correct A/B versus C-body pad and stamp hand transforms.
- Pad grows .5 seconds, remains 3.2, shrinks .5. Stamp grows .5, holds 2.6, then launches the imprint at 3.1; shrinks after flight plus .3 pause.
- Red, three-line CANCELLED imprint uses the extracted Cog font and front/back text, matching the source's generated TextNode (not a missing PNG). Starts at stamp-local (.81,-1.11,-.16), flies .5 seconds to the face, or continues past the face on miss. Text scale and miss overshoot are converted to this simulator's .62 scene scale; face height uses its current two-unit convention.
- Damage reaction 3.4, sidestep dodge 1.9; stamping sound starts 1.3 and lasts 1.1 seconds.

Validation: tests/check_rubber_stamp.py covers Yesman, Bottom Feeder, Double Talker and Glad Hander on hit/miss: hand transforms, text content/front/back, visibility, flight endpoints, live health applied once, and cleanup. Rendered and inspected the launched text and held models. All 93 battle-rule unit tests passed. This is classic-source choreography adapted to the simulator, not independently verified frame-perfect modern TTR behavior.
