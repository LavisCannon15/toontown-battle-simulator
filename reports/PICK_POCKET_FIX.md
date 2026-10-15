# Pick Pocket attachment audit

Compared `doPickPocket` and `getPropTrack` in the locally retained classic MovieSuitAttacks reference with the simulator and bundled extracted dollar asset. Extracted assets alone do not supply current TTR movie sequencing.

The generic prop player animated the dollar's own channel. Pick Pocket's reference uses a stationary bill attached to joint_Rhold; its Cog animation moves the hand. The bill now remains posed at frame 0, using the reference position (-0.01, 0.45, -0.25), HPR (136.424, -46.434, -129.712), and scale 1.41. It appears at 0.6 seconds, grows for 0.5, holds for 0.55, and shrinks for 0.5. Bill and theft sound occur only on hits, matching the reference.

Verification: tests/check_pick_pocket.py loads actual assets for Bottom Feeder, Short Change, Telemarketer and Name Dropper. Confirms stationary model geometry in the moving right-hand joint, scale, visibility times, absence on misses, and cleanup. All passed. This fixes the extra bill motion without changing dollar Lure or Embezzle.
