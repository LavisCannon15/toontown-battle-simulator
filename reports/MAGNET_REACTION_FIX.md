# Small and Big Magnet reaction correction

Reference: local ref-MovieLure.py, __createMagnetMultiTrack (lines 130–188). Both magnets use Cog landing-channel segments: 2.37→1.82 seconds, three shakes beginning at 1.82, 1.16→0.7 recovery, then forward landing recovery and neutral. The pull starts at 3.95 seconds and lasts 0.8 seconds. Magnet audio starts at 0.7 seconds. This differs from the separate Hypno-goggles routine's hypnotized channel.

The simulator now loads each Cog body's bundled landing channel, uses those source segments, returns magnet-lured Cogs to neutral and suppresses the redundant hypnotized movement transition. Explicit source frames prevent play-rate-dependent frame remapping. Existing game logic and lure durations are unchanged. Missed magnets do not play the successful landing/pull reaction. Distance remains adapted to this simulator's formation.

Reference source is classic public client sequencing, compared with the installed TTR assets; extracted phase files do not contain current TTR Python movie code.
