# Unite audit — September 12, 2026

## Rules verified

Compared the implementation with [TTR's v3.0.0 release notes](https://www.toontownrewritten.com/news/release-notes/284) and the [current Unite reference](https://toontownrewritten.wiki/Unite). The existing five Toon-Up values (20, 35, 50, 65, 80), seven single-track Gag-Ups (maximum seven regular gags), Gag-Up All (maximum 30), 100-per-type inventory cap and shared per-caster cooldown agree with the published rules. No numerical combat rule was changed in this audit.

Unites execute immediately, independently of the planned gag, including between animated attacks. They preserve the current round and planned choices. Healing is per living recipient, capped at maximum Laff, and does not revive sad or escaped Toons. Restocking excludes the missing track and level-seven gags, and respects individual carry limits and pouch space. A second caster has their own supply and cooldown.

## Presentation changes

Replaced the custom radial stars/cards with the reviewed classic `ResistanceChat.doEffect` particle configuration: `resistanceEffectSparkle.ptf` for healing and `resistanceEffectSprite.ptf` for restocking. The original three-second duration, delayed 0.3-second tint/restore, six icon emitters and source emission/force settings are retained. A track Unite displays that track's first six gag icons; All chooses one regular gag from each of six different tracks using cosmetic randomness separate from battle rolls.

The two configs come from [open-toontown/resources, phase_4/etc](https://github.com/open-toontown/resources/tree/master/phase_4/etc). Gag artwork comes directly from the bundled extracted `inventory_icons.bam`. Particle config and artwork are packaged in the simulator. The emitter parent is scaled to the simulator's Toon size. Extracted phase files do not contain current TTR sequencing code; this is not a claim that classic configs equal every detail of current TTR.

Added the Unite phrase above the caster and a live cooldown count on their battle card. Tinting affects the character branch without coloring name labels or selection rings. Overlapping activations restore colors correctly. Unite effects have a separate lifetime, so cleaning up an ordinary attack does not delete them. New-battle and application cleanup remove them. The inspected reference effect schedules no sound or full-body gesture, so this pass does not invent one or interrupt an attacking Toon.

## Verification

- All 13 combat Unite types: particle loading, icon selection, recipient filtering, unchanged action/round/random state, tint restoration and overlapping effects.
- 84 mechanics tests, including per-recipient healing, all restock caps, shared cooldown, stock rejection and independent casters.
- Live-round integration: emergency Unite, impact-time health, immediate sadness and subsequent battle events.
- Rendered healing and restocking effects inspected; screenshots in `reports/unite-audit`.

## Remaining limits

- Current TTR's exact numerical effect radius is unverified. Normal battles affect living teammates; explicit spatial engine tests remain supported. Classic code says 30, but this was not silently promoted to a verified current-TTR value.
- Cooldown advances at the simulator's round boundary. Exact sub-round timing parity with TTR is unverified. Outside-battle three-minute cooldown conversion is absent because this app has no roaming/account session.
- Jellybean Unites (100/200/350/600) and seasonal/promotion Unites are not implemented: the simulator has no wallet, suit promotion or event progression. These were included in the audit, not treated as combat effects.
- Restock ties use fixed track order; exact current-TTR tie priority and full gag unlock progression are not established by the phase assets.
- The menu and speech card are simulator layouts, not a full reconstructed TTR SpeedChat interface.
