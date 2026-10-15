# Ordinary battle rules and rewards — September 12, 2026

## Policy

Use documented rules and label gaps. The user explicitly chose to retain the known accuracy-cap limitation instead of implementing the community-estimated soft cap. TTR states that the exact thresholds will not be published. The simulator therefore remains cap-limited; it is not an exact current TTR calculator.

## Implemented

- Centralized the accuracy cap and Cog Accuracy Down calculation. Accuracy Down retains a 5% floor. Raw gag accuracy is available for inspection; defense now follows the targeted level, with the documented rank-1 exceptions. Organic Lure base accuracy cannot exceed 95. Track-experience bonuses support explicit unlock levels in the engine; the default GUI gag loadout remains max-trained.
- Railroad alone replaces traps from an earlier round. Simultaneous Trap actions, including a same-round Trap SOS, still cancel.
- Doodles have separate 0–10000 skill points per trick, editable under Setup → Toon → Doodle training. Successful tricks award 5 points; failures award none. Healing and success probabilities interpolate with training rather than switching between only untrained/maxed endpoints. Doodle rolls preserve fractional probabilities. Positive/negative mood is still explicit; full trait-driven fatigue/recovery is not implemented.
- Unites can be used by any living Toon during playback using the caster buttons in the Unite panel. The chosen Toon spends their own supply and receives their own shared Toon-Up/Gag-Up cooldown. Other Toons' gag choices remain unchanged. The engine can test explicit spatial recipient cases, but the GUI still affects the living battle team: the current TTR numerical radius was not verified, so no legacy radius is silently adopted.
- Remote duration, healing/damage, expiry, v2 layer interaction and replacement of ordinary attacks were regression-checked. Added the extracted animated antenna on controlled Cogs, retained through the last remote performance and removed afterward. Status counters refresh during playback. Remote replacement/competing-remote priority remains unverified and unsupported.

## Cog probabilities: audit outcome

All 135 attack entries were audited for provenance and effective normalized selection probabilities. See [the data report](COG_PROBABILITY_AUDIT.json). Twelve entries contain the previously documented fallback estimates; other values came from the classic game. Current TTR release notes establish that attack frequencies have changed, so classic provenance alone does not prove current correctness. The installed client was also checked for readable rule files: it exposes a compiled engine and a TTRGame.vlt bundle, not readable probability tables. No replacement probabilities were fabricated. Each entry now explicitly records that its current TTR probabilities are unverified.

This is an audit and a correction to the Cog debuff formula, **not completion of the current probability tables**. These values remain a material limitation when judging live battle risk.

## Animation work

Doodle calls now use the bundled pet model, textures, all seven trick sequences, trick sounds, failed-trick pose/question mark, and portable-hole arrival/departure. The choreography follows public PetTricks/MoviePetSOS/Pet reference code: Beg and Play Dead include their transitions, Rollover reverses, Jump has a flight interval, and healing follows the performance. Appearance and scene placement are adapted to this simulator. Remote antenna animation uses the bundled TTR rig and clips. These changes do not complete every gag/Cog animation or full SOS choreography.

## Verification

81 mechanics tests pass. Panda checks cover all seven pet tricks and failure, skill-point setup, alternate Unite casters, antenna creation/removal, impact-time health, emergency Unites, immediate sadness, v2 transformation, and previous UI/presentation behavior. Rendered pet and remote frames were inspected. Sound assets were loaded and connected, not audited by listening. The tests establish regression behavior, not live-server equivalence.

## Sources

- [TTR release notes](https://www.toontownrewritten.com/news/release-notes/503): soft cap; exact thresholds intentionally withheld.
- [Official 2021 changes](https://www.toontownrewritten.com/news/item/744/sellbot-field-offices-have-launched): Railroad replacing prior traps.
- [Official 2021 rebalancing](https://cdn.toontownrewritten.com/community/notices/Rebalancing_Update_December_2021.pdf): Cog accuracy floor and reward changes.
- [Accuracy](https://toontownrewritten.wiki/Accuracy), [Doodles](https://toontownrewritten.wiki/Doodles), [Unites](https://toontownrewritten.wiki/Unite), [remotes](https://toontownrewritten.wiki/Remote_control): current public tables.
- [PetTricks](https://github.com/open-toontown/open-toontown/blob/develop/toontown/pets/PetTricks.py), [pet battle logic](https://github.com/open-toontown/open-toontown/blob/develop/toontown/pets/DistributedPetProxyAI.py), [pet choreography](https://github.com/open-toontown/open-toontown/blob/develop/toontown/battle/MoviePetSOS.py), [pet teleport sequences](https://github.com/open-toontown/open-toontown/blob/develop/toontown/pets/Pet.py): classic primary reference code, cross-checked against the current published Doodle tables; not represented as current TTR source.

All runtime assets remain inside assets/ttr. Reference downloads are not imported or executed by the game.
