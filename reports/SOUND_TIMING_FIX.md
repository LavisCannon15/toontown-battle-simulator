# Mixed Sound gag timing

The previous generic track builder started every Sound movie at t=0. A dedicated Sound scheduler now groups actions by gag level, orders the groups from lowest to highest, and starts matching gags together.

Reference: the local MovieSound.py's doSounds / __doSoundsLevel / __createToonInterval and instrument builders. BattleBase defines TOON_SOUND_DELAY = 1.0:
https://github.com/open-toontown/open-toontown/blob/develop/toontown/battle/BattleBase.py
https://github.com/open-toontown/open-toontown/blob/develop/toontown/battle/MovieSound.py

The classic movie applies each level's delay twice: once around the instrument movie and once within its animation/prop/sound tracks. The simulator's instrument builder has no internal group delay, so its single wrapper uses the resulting two-second interval between distinct levels. Missing gag levels do not create empty slots.

Example: Bike Horn, Aoogah, Aoogah, Foghorn start at 0, 2, 2, and 4 seconds. Four Foghorns still start together.

The simulator aggregates damage across Sound gags. That total is still applied once, at the last group's contact; it is not duplicated per instrument. Per-level damage text and the original Opera randomized break timing remain separate presentation limitations. SOS Sound guests are still handled by the existing SOS wrapper rather than this player-group scheduler.

Verification: dedicated checks cover sorting, same-level synchronization, prop visibility before/after each start, complete mixed/same-level/Opera rounds, and display/engine HP parity.
