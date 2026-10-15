# Mechanics and animation implementation — September 12, 2026

See [the subsequent rules/rewards update](RULES_AND_REWARDS_UPDATE.md) for newer changes and verification.

## Implemented and checked

- Event-by-event battle resolution. Toon health changes at the animated impact, before the next Cog chooses its targets. A Unite during an attack's wind-up changes the eventual damage result. Fatal impacts start sadness immediately. Separate Unite effects survive transitions between attacks.
- v2.0 option in Setup. Destroying the outer suit reveals a fresh Skelecog health layer, without carrying over excess damage. Remotes persist across the transition; Fires bypass both layers. The surviving second layer can attack.
- Presentation and Hypno-goggles share the highest additional-Lure bonus tier. Mixed-target accuracy includes the lured/remote ratio for level-7 Throw and Squirt as well as Sound. High Dive's base accuracy metadata is 95.
- An ordinary gag is not consumed or animated when all its applicable targets have already been removed before its track resolves.
- Sequential Toon-Up performers receive their own healing events rather than showing all healing with the final performer.
- Fifteen reference attack definitions now provide explicit hit timing, dodge timing and hit reactions. Power Trip uses a forward fall on hit and a jump on miss; Guilt Trip likewise uses its source reaction. Added the extracted forward-fall, backward-fall and struggle Toon clips. Dodges use their animation's natural length.
- Removed the six-second truncation of Cog attack clips. Thrown props inherit the character's hand scale before release and retain that scale in flight.
- Healing remotes use the extracted Song and Dance clip and sound. Damage remotes use the speaking clip and Bad Joke sound, with captions. These are still abbreviated sequences.
- Live Cog damage reactions, single breakup per defeated Cog, and walking to updated formation positions between events.

## Verification

74 mechanics tests passed. Real-model checks covered impact-time health, emergency Unites, immediate sadness, v2.0 model replacement, reaction rig binding, and projectile scale preservation. The resource playback sweep exercised all 49 gag entries, all 32 Cog attack mappings, and six normal/skeleton breakup rigs. Full UI integration and the previous target-marker, Fire heading, Toon-Up travel and Unite checks passed. Rendered Power Trip, Song and Dance and Cog breakup frames were inspected. These checks do not establish complete live-game parity or verify sound quality by listening.

## Still open from the larger audit

This update does **not** complete every item in MECHANICS_AUDIT.md. The exact current accuracy soft-cap formula and the twelve estimated Cog probability entries remain unverified. Partial training, XP/level-7 recharge, pet fatigue, remote replacement priority, mixed SOS/gag calculations, Unite radius, reinforcement controllers, supervisors, bosses and Field Offices remain unimplemented or incomplete.

Animation work is also not complete: most attack props still use generalized attachment/choreography; special particles and camera work are adapted; SOS and Doodle performances are abbreviated; trap deployment/activation and several gag-specific sequences need deeper reconstruction. No claim is made that extracted assets provide TTR's current battle logic. They contain clips and artwork, but the choreography must be implemented separately.

## References

- [Public classic attack choreography](https://github.com/open-toontown/open-toontown/blob/develop/toontown/battle/MovieSuitAttacks.py): explicit timing/reactions stored in assets/battle_movies.json under attack_timing. This is classic reference code, not current TTR client code.
- [TTR Lure](https://toontownrewritten.wiki/Lure), [accuracy](https://toontownrewritten.wiki/Accuracy), [v2.0 Cogs](https://toontownrewritten.wiki/Version_2.0_Cogs), [Unites](https://toontownrewritten.wiki/Unite).
- [Official soft-cap change](https://www.toontownrewritten.com/news/release-notes/505): establishes the change but does not specify the complete formula.

Runtime models, animations, textures and sounds remain bundled under assets/ttr; no external Desktop resource directory is required.
