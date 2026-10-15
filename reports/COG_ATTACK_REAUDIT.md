# Cog attack re-audit

September 12, 2026. Rechecked the current implementation after the Toon-facing and MISSED-text changes. This audit changes no gameplay or HUD code.

## Results

- All 135 Cog/attack pairings across 32 Cog types, comprising 68 distinct attack names, completed hit and miss playback: 270 cases.
- These checks loaded the real models, stepped effects, and checked final positions, heading restoration and idle state. They do **not** establish correct intermediate choreography, exact hand contact, audio synchronization or current TTR parity.
- Eight additional off-center hit/miss cases checked Finger Wag, Tee Off, Power Trip and Synergy. All four showed the target Toon still facing forward rather than toward the attacking Cog.
- Static reference inventory found no missing mapped sound files and no extracted prop name absent from the runtime prop lists. Neither check proves those resources are actually used correctly.
- The generic particle map lacks RubOut, Synergy and Waterfall. Synergy and Waterfall are handled separately by the specialized movies; they are not missing merely because the generic map omits them. RubOut is a real omission.

Full original per-attack table: [68-attack audit](COG_ATTACK_AUDIT.md). Current machine-readable results: [all pairings](cog-attack-audit/coverage.json), [resource inventory](cog-attack-audit/reaudit-inventory.json), [targeted probes](cog-attack-audit/reaudit-targeted.json).

## Confirmed issues

### 1. Targets do not turn toward the attacker

The classic `getToonTrack` explicitly turns the target Toon toward the suit before its damage/dodge track. The simulator's health/reaction path does not do that. The recent gag-facing fix only affects the Toon who is *performing a gag*.

An off-center Cog/Toon test returned a facing-direction dot product of approximately 0.5145, rather than approximately 1.0, for every tested attack and miss/hit branch. Side steps and jumps can consequently point the wrong way relative to the incoming attack.

Relevant implementation: battle_movies.py `health_movie` and `live_health`. Reference: [MovieSuitAttacks.getToonTrack](https://github.com/open-toontown/open-toontown/blob/develop/toontown/battle/MovieSuitAttacks.py), local ref-MovieSuitAttacks.py lines 537–551.

### 2. MISSED exists, but its timing is still generic

The popup now uses the game's font, red text and rise/hold/fade behavior. However, the simulator starts it at damage impact. The reference schedules it at `dodgeDelay + showMissedExtraTime`.

Examples from the reference:

| Attack | Reference popup start | Current scheduling |
|---|---|---|
| Synergy | 0.91 + 1.0 = 1.91 seconds | 1.7 seconds |
| Power Trip | 1.29 + default 0.5 = 1.79 seconds | 1.8 seconds |
| Tee Off | animation duration − 4.35 + 1.7 | animation duration − 2.25 |

Frame-sampled observation confirms the scheduling difference; timestamps in the JSON are quantized to 1/24 second and should not be read as exact source constants. The extracted metadata does not retain `showMissedExtraTime`, so the missing data needs to be added rather than guessing offsets for every attack.

Reference: [MovieSuitAttacks](https://github.com/open-toontown/open-toontown/blob/develop/toontown/battle/MovieSuitAttacks.py), `getToonTrack`, `doSynergy`, `doPowerTrip`, `doTeeOff`.

### 3. Rub Out is missing the erasing effect

The reference constructs three RubOut effects using the target's head, arm and leg colors, positions them at the corresponding body heights, and hides/restores body pieces in stages. Our runtime holds the pencil and pad but skips the unmapped RubOut particles and never performs that body-part sequence. A valid pencil model and completed reaction are not a complete Rub Out animation.

Reference: `doRubOut`, starting at local reference line 1002. Relevant implementation: cog_choreography.py particle loop, assets/cog_particle_map.json.

### 4. Multi-stage reactions are flattened

The generic runtime primarily selects one reaction name and one dodge name. The classic source also contains spliced animation lists, pauses, offsets and body transformations. These are not preserved by the current extraction schema. Synergy has a dedicated spliced jump, but most complex reactions remain simplified. Some short live damage reactions are also forced through the generic 0.9-second path unless specialized logic overrides it.

### 5. Particle metadata is only a partial description

The runtime supports suit-parent and target-parent particles. Entries marked world-relative are ignored by the owners selection. The generic attachment code also does not replay arbitrary reference `setPos`, `setHpr`, scale, body-height calculations or dynamically constructed paths. Effects can exist and still originate from the wrong place. Only named special cases currently repair some placements.

### 6. Prop lifetime and trajectory remain generalized

The generic movie retains hand props for its computed duration rather than replaying each prop's exact source lifetime. Thrown props use a linear 0.4-second flight, generally toward the first target, with a fixed miss offset. This does not implement source bounce curves, several throws, transformations, or recipient-specific sequences. Headings may be restored before a longer parallel prop/sound sequence has finished.

The Tee Off club's left-hand attachment, recorded orientation and 1.1 scale are present. Its ball path, swing/contact timing and miss trajectory still use an adapted implementation. Do not mark Tee Off completely accurate merely because the club loads or one screenshot looks plausible.

## Important unfinished attacks carried forward

| Attack(s) | Remaining source behavior |
|---|---|
| Head Shrink | Head scaling/detachment/drop sequence |
| Downsize; Paradigm Shift | Recipient scaling and movement |
| Spin | Target spin/body deformation |
| Red Tape | Wrapping/binding tubes |
| Write Off; Rubber Stamp | Flying checkmark / CANCELLED effect |
| Bounce Check | Multi-bounce trajectory and associated sound sequence |
| Canned; Sacked | Overhead toss and impact staging |
| Bite; Chomp | Multi-stage teeth motion |
| Brain Storm | Complete storm objects and recipient sequence |
| Freeze Assets | Complete freezing sequence |
| Liquidate | Complete sinking sequence |
| Guilt Trip | Sweeping bars |
| Quake; Shake; Tremor | Full camera and ground-shake choreography |
| Hang Up; Pound Key | Complete phone/receiver hand transitions and lifetimes |

Nine attack names still lack a dedicated implementation in the inspected classic source: Beguile, Close the Loop, Embezzle, Flood the Market, Hostile Takeover, Money Talks, Nickel and Dime, Quash, and Throw Book. The bundled TTR assets do not by themselves provide their current sequencing code. Their current presentations remain unverified adaptations.

## Verification limits

The 270-case pass used four Toons and one Cog at a time, at the Cog's upper ordinary level. It did not exhaust every lineup size, simultaneous hit/miss combination, sadness transition, remote/lure overlay, interruption point, skelecog rig or v2 transition. Existing separate checks cover some of those cases, but they were not all rerun in this pass.

Frames were captured for all 68 attack names; targeted visual inspection included Tee Off and Rub Out. The run used null audio and cannot certify how the sounds actually sound or overlap. The reference is public classic code, not a verified dump of current TTR client code. No claim of full visual parity is warranted.

## Fix order

1. Make Toon reactions face the attacker and restore formation heading safely.
2. Store and apply per-attack miss-popup timing.
3. Implement Rub Out and preserve spliced reaction sequences.
4. Replace generalized prop lifetime/path handling with explicit attack sequences.
5. Review body transformations, particle origins, audio and special attacks with real-time visual comparisons.

Scripts for reproducing this pass are tests/check_cog_attack_audit.py and work/cog-reaudit/{inventory,targeted}.py. The original report remains useful as the full attack roster; this document records the stronger findings from the second pass.
