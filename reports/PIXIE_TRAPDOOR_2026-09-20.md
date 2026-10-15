# Pixie Dust direction and Trapdoor sound — September 20, 2026

Pixie Dust's retained MovieHeal.__healSprinkle source explicitly faces the caster 90 degrees from the recipient: sprinkle-dust throws along local +X. The simulator previously faced the target directly. Added the source quarter-turn at playback time, after reaching the healing position. Also moved pixiePoof to the recipient, matching pixieDrop and the source. The other three particle systems remain attached to the caster. All 12 distinct caster/recipient combinations verify throw direction, target particle parents, and restoration of position/heading.

Trapdoor placement previously scheduled a button/opening sequence separately for every simultaneous user. It now plays each shared placement sound once. Button starts at 2.3 seconds, stops at 2.97; trap opening starts at 3.27 and stops at 3.77. Tests step real Panda intervals for one and four Toons and verify the 0.3-second gap and absence of duplicate cues. These two distinct sounds are intentional in the retained MovieTrap source. The reported phase (placement versus a Cog falling through) has not yet been confirmed by the user; this fix addresses simultaneous placement duplication, not a proven single-Toon overlap. Fall-through sounds were not changed in this pass.

Current TTR phases supply the sound and animation assets; retained classic Python supplies these choreography references. No claim is made that phase files contain current TTR Python.

Files: audited_gags.py, trap_movies.py. Tests: check_pixie_target.py, check_trapdoor_audio.py. Logs/backups: work/pixie-trapdoor-fix/. Running simulator processes must be restarted to load edited modules; the active game was not interrupted.
