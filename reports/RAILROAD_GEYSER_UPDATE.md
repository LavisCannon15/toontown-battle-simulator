# Railroad, Geyser and attack titles

The attack title uses bundled MickeyFontClassic lettering, uppercase red text with a black edge/shadow, centered above the scene. The earlier small typewriter caption is removed.

Railroad uses the same held button and pushbutton clip as Drop. One extracted traintrack2 model stays across the battlefield until the trap is activated or removed. Its tunnel nodes start hidden, following BattleProps. On activation, Cogs move onto the track, the extracted train passes through the lineup, and damage is accompanied by the original flatten reaction (the drop animation alias in Suit.py) and train sounds.

Geyser separates the extracted model's mound and water nodes, grows and retracts the water, and lifts/returns hit Cogs with slip-backward reactions. Misses offset the eruption. Repeated Geysers share the target visual to avoid competing position intervals.

References: bundled phase_3 font, phase_3.5 button/pushbutton assets, phase_5 train/traintrack2/geyser/drop assets, phase_4 slip-backward assets; local public MovieTrap, MovieLure, MovieSquirt, BattleProps and Suit reference files. Scene scale, camera and timing are adaptations, not a claim of an exact TTR movie port.

Verification: 81 mechanics tests; all 49 gag and 32 Cog movie-loading checks; rendered title, track, train and eruption frames; dedicated placement, trigger, reset, lift/return and live-round regression check in tests/check_rail_geyser.py. Sound cues are connected but were not audited by listening.
