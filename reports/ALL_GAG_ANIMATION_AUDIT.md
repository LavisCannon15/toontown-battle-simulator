# All-gag animation audit — September 12, 2026

## Evidence and scope

All 49 gag entries were reviewed against the local public classic MovieHeal, MovieTrap, MovieLure, MovieSound, MovieThrow, MovieSquirt and MovieDrop references, plus MovieUtil and BattleProps. Models, animation channels and sound files resolve through the simulator’s bundled extracted TTR library. No external asset folder is required.

The phase archives contain assets, not current TTR Python movie sequencing or server battle formulas. This implementation is reference-informed choreography fitted to this simulator, not a recovered current TTR movie implementation. The six added particle definitions are reviewed classic configs from [open-toontown/resources](https://github.com/open-toontown/resources/tree/master/phase_5/etc); their models and textures use the bundled library.

## Changes by track

- **Toon-Up:** Centered performer; reaching Feather, lipstick/lips, hat/cane, five Pixie Dust effects, hip-attached cubes, ladder/glass/climb/swim/return.
- **Trap:** Ground props persist between rounds; slip, rake strike, sinking traps, TNT explosion and Railroad activation have separate sequences.
- **Lure:** Fishing pole with animated bill; original left-hand magnet/goggles transforms; existing Presentation screen/button sequence.
- **Sound:** Megaphone plus expanding instrument, per-level attachment and appearance sounds; Opera Singer extended pose and sound-wave particles.
- **Throw:** Hand-launched models and animated splats; Wedding Cake tiers divide among targets, with dedicated sound cues.
- **Squirt:** Continuous source-model streams, flower/button, hose/hydrant, animated cloud/rain; specialized Geyser retained.
- **Drop:** Button, growing shadow, whistle and native landing channels; small props strike at shoulder height; one centered group boat.

## Per-gag resource coverage

Every entry runs both hit and miss presentation paths in `tests/check_all_gag_sequences.py` (where meaningful: Trap placement and Toon-Up do not imply ordinary attack misses). The screenshots sample one point in each hit sequence; they are not proof of every animation frame.

| Track | Gag | Toon channel | Main prop |
|---|---|---|---|
| Toon-Up | Feather | tickle | feather |
| Toon-Up | Megaphone | sound | megaphone |
| Toon-Up | Lipstick | smooch | lipstick |
| Toon-Up | Bamboo Cane | happy-dance | cane |
| Toon-Up | Pixie Dust | sprinkle-dust | dust |
| Toon-Up | Juggling Cubes | juggle | cubes |
| Toon-Up | High Dive | climb | ladder |
| Trap | Banana Peel | toss | banana |
| Trap | Rake | toss | rake |
| Trap | Marbles | toss | marbles |
| Trap | Quicksand | toss | quicksand |
| Trap | Trapdoor | toss | trapdoor |
| Trap | TNT | toss | tnt |
| Trap | Railroad | toss | traintrack |
| Lure | $1 Bill | battlecast | 1dollar |
| Lure | Small Magnet | hold-magnet | small-magnet |
| Lure | $5 Bill | battlecast | 5dollar |
| Lure | Big Magnet | hold-magnet | big-magnet |
| Lure | $10 Bill | battlecast | 10dollar |
| Lure | Hypno-goggles | hypnotize | hypno-goggles |
| Lure | Presentation | pushbutton | slideshow |
| Sound | Bike Horn | sound | bikehorn |
| Sound | Whistle | sound | whistle |
| Sound | Bugle | sound | bugle |
| Sound | Aoogah | sound | aoogah |
| Sound | Elephant Trunk | sound | elephant |
| Sound | Foghorn | sound | fog_horn |
| Sound | Opera Singer | sound | singing |
| Throw | Cupcake | throw | tart |
| Throw | Fruit Pie Slice | throw | fruitpie-slice |
| Throw | Cream Pie Slice | throw | creampie-slice |
| Throw | Whole Fruit Pie | throw | fruitpie |
| Throw | Whole Cream Pie | throw | creampie |
| Throw | Birthday Cake | throw | birthday-cake |
| Throw | Wedding Cake | throw | wedding-cake |
| Squirt | Squirting Flower | spit | squirting-flower |
| Squirt | Glass of Water | spit | glass |
| Squirt | Squirt Gun | water-gun | water-gun |
| Squirt | Seltzer Bottle | hold-bottle | bottle |
| Squirt | Fire Hose | firehose | firehose |
| Squirt | Storm Cloud | pushbutton | stormcloud |
| Squirt | Geyser | pushbutton | geyser |
| Drop | Flower Pot | pushbutton | flowerpot |
| Drop | Sandbag | pushbutton | sandbag |
| Drop | Anvil | pushbutton | anvil |
| Drop | Big Weight | pushbutton | weight |
| Drop | Safe | pushbutton | safe |
| Drop | Grand Piano | pushbutton | piano |
| Drop | Toontanic | pushbutton | ship |

## Verification

- 49 gag hit/miss playback pairs, stepped through attachment boundaries, with position restoration checks.
- Seven actual two-round Trap/Lure battle sequences, checking persistence and cleanup.
- Existing resource/movie check covers all 49 gags, all 32 Cog mappings and six breakup rigs.
- 81 mechanics tests passed; this pass adds only pre-event trap metadata to the engine, not formula changes.

## Remaining adaptations

Camera cuts, actor scale/distance, some prop trajectories, target reactions and several secondary cue timings remain simulator adaptations. High Dive uses the resource climb/swim/jump clips and shrinking return, but not the full original camera/look choreography. Cloud rain uses the source spray model in multiple streams. Mixed same-track actions still share an event-level health timing; exact staggered original movie scheduling is not established. Audio cues were checked for resource availability and scheduled playback, not audited by listening to every possible simultaneous combination. Existing documented battle-rule limitations remain unchanged.

The default renderer also reports missing named ground/shadow bins; Panda creates them automatically. No playback exception was observed in the verification runs.
