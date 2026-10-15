# Drop gag shadow visibility

The shared Drop builder already scheduled a drop-shadow prop, but its embedded custom ground render bin ran before the simulator's opaque pavement, so the pavement covered it. Override the inherited bin at higher priority to transparent, after the pavement, preserving depth testing and disabling depth writes. Shadows sit at .095 above the ground; characters continue to occlude them normally.

The extracted phase_3/models/props/drop_shadow.bam remains the shadow asset. Match the retained Suit's .45 base model scale, converted to the lab's .6 scene scale, underneath MovieDrop's per-level growth. Preserve appearance at 2.44s and growth until 4.3s, then retain it for the source's .3-second post-impact period. Misses use the actual missed prop destination. Shared builder also covers SOS Drop and its per-Cog delay. Every shadow is registered for interruption/round cleanup.

References: retained ref-MovieDrop.py posShadow/shadowTrack and work/ref-FullSuit.py's shadow setup. These are classic source references, not current TTR Python. Rendered Piano preview: work/drop-shadow-fix/piano.png.

Validation: tests/check_drop_shadows.py covers all seven hit/miss variants, visibility before/during/after impact, growth, position, render state and cleanup; additionally four-target Barnacle Bessie verifies staggered shadow onset. Logs and backup: work/drop-shadow-fix/. Restart the running simulator to load audited_gags.py.
