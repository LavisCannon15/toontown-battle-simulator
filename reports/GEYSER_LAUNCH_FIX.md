# Geyser launch correction

User identified the launched Cog's movement as the issue. Compared battle_movies.geyser_movie with local ref-MovieSquirt.py, __getSuitTrack's geyser branch.

The previous movie compressed all of slip-backward into 1.7 seconds. The reference uses half-speed frames 0–15 for A-body Cogs (0–14 for B/C), holds frame 16 (15 for B/C) for .5 seconds, then resumes the remaining animation at native speed. This staged sequence is now used. The root rises over 1.1 seconds and returns over .6 seconds; the reference's 14-unit rise is adjusted by the rendered Cog scale. It restores the idle/remote pose after recovery.

Also corrected the water spout to 1.8 times the common prop scale, retained the mound under the target on misses (the Cog dodges), and set dodge timing to 1.8 seconds. Each Cog now receives its own random offset in [0, 1) seconds, matching the classic per-target delay. Eruption, launch, damage, and dodge all share that offset. A separate presentation random generator leaves combat randomness untouched.

Dedicated checks passed for separated mound/water geometry, spout scale, hit launch height, stationary miss branch, return to original position, and prop cleanup.
