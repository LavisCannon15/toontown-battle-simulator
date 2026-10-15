# Opera Singer glass cue and v2.0 revival audit

Opera Singer's extracted `phase_5/audio/sfx/AA_sound_Opera_Singer_Cog_Glass.ogg` was bundled but absent from the audio lookup and never scheduled. Added the lookup and impact cue in `sound_sequence.py`.

The retained `MovieSound.__getSuitTrack` plays the glass sound once per hit Cog at tSuitReact + 2 seconds + a random fraction of a second. Our scheduler applies that offset after the Sound group delay and synchronizes each Cog's aggregate health display with its glass cue. Multiple singers do not duplicate the cue on the same Cog. Misses do not play it. Presentation randomness does not consume the combat RNG.

Verified registered Ogg resource, one/four singers, mixed/all misses, cue count, health/audio timing, cleanup, and unchanged combat RNG in `tests/check_opera_glass.py`. Existing real-asset mixed Sound/stagger/live-round regression also passes. Audio playback was tested using the null audio backend; the test verifies scheduling/resource loading rather than subjective loudness.

Version 2.0: user elected to keep TTR rules after audit. Official v4.0.0 notes explicitly changed Reinforced Plating so newly revealed Skelecogs can attack that round: https://www.toontownrewritten.com/news/release-notes/357 . No rule change made. A deterministic engine check confirmed a surviving uncontrolled Skelecog gets its Cog-phase attack after losing the suit layer.
