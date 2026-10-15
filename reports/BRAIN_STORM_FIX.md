# Brain Storm

Audited retained MovieSuitAttacks.doBrainStorm (1263–1314) and BattleParticles.BrainStorm factory. Missing classic config obtained from https://raw.githubusercontent.com/open-toontown/resources/master/phase_5/etc/brainStorm.ptf with .bam extension normalized. Uses extracted TTR brainstorm-box/env/track sprites, cloud model/channel and sound.

brain_storm_movie.py replaces the generic stationary cloud/water spray. Cog gesture delayed .9; posed cloud grows .7, waits 1.1, travels to target for 1, waits 1.2. Three blue-tinted particle sets begin at 4/4.5/5 with durations 2.2/1.7/1.2. Native cloud segments: second 3 for .5, 2.5 for .5, 1 for 1.5. Cloud waits .4, shrinks .5 and clears. Hit damage 4.5; cringe from .4 for .8 then duck from 1.6; sidestep dodge 3.3 and missed text 4.4. Audio starts 2.6.

Uses existing simulator face-height/scene-scale conventions and classic choreography; extracted phase assets do not provide current TTR movie sequencing code.

Validation: tests/check_brain_storm.py passes both Micromanager and Mover & Shaker hit/miss sequences, cloud endpoint, initial posed frame, three sprite identities and staggered starts, active cloud channel, live damage once and cleanup. All 93 battle-rule tests passed.
