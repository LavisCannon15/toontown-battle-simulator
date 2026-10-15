# Grand Piano audit and corrections

Reference: local ref-MovieDrop.py and ref-MovieUtil.py, compared with the bundled piano model/channel and Cog flatten channel. Delay constants verified at https://github.com/open-toontown/open-toontown/blob/develop/toontown/battle/BattleBase.py (TOON_DROP_DELAY=0.8, TOON_DROP_SUIT_DELAY=1.0).

Confirmed issues: every ordinary Drop builder started at time zero; generic health callbacks used a short drop-react instead of native flatten; all misses used sidestep and full prop hit playback; shadow timing began too early; animated props shrank only after their native animation instead of at its end.

Changes:
- Sort single-target Drop groups by number of attacks, stagger groups by one second and attacks within each group by 0.8 seconds. Group level-7 Drops follow ordinary Drops.
- Major Drops use native flatten; small Drops retain drop-react. Prevent generic damage callbacks from duplicating reactions.
- Piano misses play through landing frame 11, hold, and shrink. Successful animated props shrink during their final 0.3 seconds.
- Major ordinary misses use the reference's brief victory-channel tease (0.5–1.9 seconds), not a full victory loop. Lured misses omit it. Repeated misses on one single-target group avoid repeated teases.
- Shadow begins at 2.44 seconds and grows until the prop appears at 4.3 seconds.

Limitations: classic public sequencing plus current bundled art is not proof of identical current TTR client choreography. Prop positions/scales remain adapted. Track damage is aggregated by the existing engine; its total is displayed on the final applicable impact per target, rather than individual damage and bonus ticks per piano. NPC/ordinary mixed Drop scheduling is still separate. The pushbutton prop's scale-in/out remains simplified.

Validation: dedicated four-piano schedule/reaction checks cover shared and distinct Cog targets, ordinary misses and lured misses. A live-round probe compares engine and displayed damage for four pianos. Unit-test results are in work/drop-unit-tests.log. No battle damage formulas were changed.
