# Freeze Assets

Reference: retained MovieSuitAttacks.doFreezeAssets (2107–2152) and BattleParticles FreezeAssets factory. Missing classic particle configuration inspected and obtained from https://raw.githubusercontent.com/open-toontown/resources/master/phase_5/etc/freezeAssets.ptf; only model-path extension normalized to .bam. It uses the project's extracted TTR snow-particle sprite. Bundled stormcloud model/channel and Cog/Toon animations remain the art source.

Dedicated freeze_assets_movie.py replaces the generic stationary cloud and water spray:
- Cog gesture delayed .9 seconds.
- Cloud stays posed at frame 0, grows .7 seconds over the Cog, waits 1.1, travels one second above its Toon target, waits .2, then emits snow for 2.1 seconds. Snow drains and cloud shrinks after .4 seconds.
- Uses reference cloud heading 0, distinct from Liquidate's 180. Suit height measured in Suit-local coordinates before parent scaling.
- Live damage at 3.5; reference cringe segment (.4–1.2), then duck from 1.6; sidestep dodge at 2.3. Immediate sadness still overrides ordinary reactions.
- No water stream or invented sound (classic function contains no sound track).

Classic source timing is adapted to this simulator's .62 scene scale and current two-unit Toon face height; extracted phase files do not provide modern TTR sequencing code.

Validation: tests/check_freeze_assets.py checks Penny Pincher, Tightwad and Cold Caller, hit and miss, cloud movement, unchanged prop pose, snow parent, exact-once live damage, and cleanup. Rendered with particle simulation and inspected snow above the target. All 93 battle-rule unit tests passed.
