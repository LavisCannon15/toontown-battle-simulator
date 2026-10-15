# Razzle Dazzle

Compared the simulator with the existing local MovieSuitAttacks.py, doRazzleDazzle (line 1177). The generic recipe omitted the moving Smile particle effect, started the sign at .3 rather than .5 seconds, and omitted growth to 1.39 scale.

The dedicated movie restores right-hand placement and rotation, .5-second appearance, .5-second sign growth, sparkle launch at 1.5 seconds, two-second travel to the target, four-second native sign animation, 1.6-second sound, 2.6-second damage/cringe, and 1.9-second sidestep. Miss particles continue five units beyond the target instead of disappearing at the Toon. World-space endpoints adapt the classic coordinates to this simulator.

The bundled smile model/channel still come from the extracted TTR assets. The inspected particle definition is bundled from https://raw.githubusercontent.com/open-toontown/resources/master/phase_5/etc/smile.ptf . It has no external runtime dependency.

Targeted hit/miss playback checks passed for visibility, growth, hand attachment, particle movement/endpoints, heading restoration and cleanup. The shared Razzle Dazzle move uses this sequence for every Cog that has it.
