# Gag audio timing audit

Compared the retained MovieHeal, MovieSquirt and MovieLure sequencing source with the simulator. Extracted TTR assets contain the audio and animation channels; they do not establish the current TTR Python timeline.

Corrected Toon-Up starts (seconds into the gag performance): Feather 1.0, Megaphone 2.0, Lipstick 2.0, Bamboo Cane 0.2, Pixie Dust 2.0, Juggling Cubes 0.7, High Dive 0.6. Previously all started at 0.6. Restored the reference's intentional durations for Cane (6.4), Pixie Dust (4.1), Juggling (7.7), and High Dive (9.0).

Corrected Squirt audio starts: Glass of Water 1.7, Squirt Gun 1.8, Seltzer Bottle 0.1 seconds before spray, Fire Hose 2.8. Previously these used a shared 0.4-second lead relative to spray, which disagreed with individual reference cues. Flower's existing 2.1 and Storm Cloud's two cues at 2.3 and 4.6 match the reference. Removed Geyser's unsupported three-second sound cutoff; its full extracted clip now plays from 1.8.

Checked Lure's fishing pole, magnets, goggles, and Presentation audio lead-ins; those already match the retained reference and were preserved.

This is a focused timing correction, not certification of every Cog attack or of exact modern TTR playback. Automated playback uses null audio, so it checks interval execution and cleanup, not perceived audiovisual synchronization. Further visible/audible discrepancies should be compared against actual gameplay.
