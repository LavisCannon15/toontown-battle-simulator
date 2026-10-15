# Gag group timing audit

Compared all seven entry points with retained MovieHeal, MovieTrap, MovieLure, MovieSound, MovieThrow, MovieSquirt, MovieDrop, and work/ref-BattleBase.py. These are classic client references; bundled TTR phase files provide the models, sounds, and animation channels, not modern client scheduling logic.

| Track | Reference batching | Simulator outcome |
| --- | --- | --- |
| Toon-Up | Complete each heal sequentially, including center movement and return | Existing sequential wrapper retained; four mixed performers checked |
| Trap | Parallel placements, including conflicting placements | Parallel timing retained; trap mechanics were not rewritten in this audit |
| Lure | Parallel Lure performances | Parallel timing retained; Presentation special route inspected |
| Sound | Same-level instruments together; separate level groups delayed | Existing level scheduler retained; reference has nested delay application |
| Throw | Target groups sorted by count, 1 second between groups, .5 second within group; group pies afterward | Previous Throw fix retained; mixed Wedding Cake coverage added |
| Squirt | Target groups sorted by count, 1 second between groups, .5 second within group | Fixed Geyser bypass: all mixed actions now enter the scheduler |
| Drop | Target groups, .8 second within group, 1 second between groups; group drops afterward | Existing scheduler retained |

Geyser fixes: retain per-Cog randomized contacts in the scheduler, place aggregate health at the final applicable contact, avoid a second generic damage reaction after the custom launch, and suppress duplicate water/launch effects for repeated Geysers while allowing each Toon to press their button.

Validation: 100 unit tests; 49 individual gag hit/miss playback cases plus seven live Trap/Lure rounds; four-performer mixed playback on every track, with character position restoration. These checks verify execution and timing properties, not an exact visual match to current TTR footage.

Remaining limitations: the engine aggregates damage per track, so individual pie/squirt impacts do not yet each have their own engine-authored damage and combo events. Animation wrappers also face performers before the complete track rather than at each delayed performer start. Simultaneous Lures affecting one Cog can still compete for its reaction animation. Classic Sound nested delays and all modern TTR-specific differences require current gameplay verification. This audit does not certify every gag's prop attachment, audio cue, or combat formula.
