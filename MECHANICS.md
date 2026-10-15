# Mechanics and evidence

Current implementation snapshot: September 19, 2026. See [the current project audit](reports/PROJECT_AUDIT_2026-09-19.md) for findings, fixes, verification, and priorities. Older reports remain research history; this page supersedes their descriptions of the active interface and implemented features.

## Evidence boundary

This simulator uses public TTR rules, a separate local battle engine, and bundled extracted TTR media. The 12,567 extracted phase files contain no Python source/bytecode. Animation clips supply motions; they do not specify the complete event order, probabilities, prop placement, or server calculations. Classic public source is a useful reference, not proof of current TTR behavior.

The user chose verified behavior with disclosed limits rather than the community-estimated accuracy soft cap. `combat_rules.py` therefore retains a **legacy 95% cap**. The UI and battle log disclose this. Do not use the simulator as an exact current-TTR accuracy calculator.

## Ordinary battles

- Independently configured teams of 1–4 Toons and 1–4 Cogs. Toons have Laff, not character levels. Setup allows sandbox values up to 200 Laff and defaults to max-trained tracks, optionally with a missing track.
- All 49 gags, with track order Toon-Up, Trap, Lure, Sound, Throw, Squirt, Drop. Inventories distinguish regular pouch space from level 7 stock. Organic bonuses and per-gag carry limits are applied.
- Toon-Up excludes its caster. SOS Toon-Up, Doodles, and Toon-Up Unites can include the caller. Missed Toon-Up gives a weak heal.
- Trap cannot target an already lured Cog. Conflicting ordinary traps cancel. A lone Railroad can replace traps from a prior round. Trap SOS skips occupied/lured slots; SOS plus a regular same-round trap can collide.
- Lure does not extend an already lured Cog's duration or replay its entry motion. All-Lured lineups reject another Lure or Trap before a choice is committed. Trap activation consumes the trap.
- Successful damaging gags wake Lure. Throw/Squirt add a rounded-up 50% base-damage knockback bonus; Sound wakes without that bonus; Drop misses lured targets. Same-track ordinary gag combinations add a rounded-up 20% bonus.
- Passive traps contribute Lure accuracy; activated Trap contributes 50 stun points. Other damaging gags contribute 25 stun points per contributing gag, not per victim. Details and raw accuracy are in `Battle.accuracy`.
- Run is immediate and spends no round. Escaped Toons disappear from active targeting and status panels. No living participating Toons means a Cog win. No living Cogs means a Toon win. Victory motions are restricted to the result of the battle.
- The normal selection timer is 30 seconds; untimed practice and optional automatic resolution are simulator controls. Setup pauses the clock. Manual unselected/invalid actions pass on timer expiry.

## Cogs and v2.0

All 32 ordinary Cog profiles have department, rank, model/body mapping, and an attack table in `cogs.json`. Supported levels are 1–12; normal health is `(level+1)*(level+2)`, with level 12 at 196 HP. Setup restricts each profile to its supported rank through rank+4 range.

Regular and Skelecog forms use the selected profile's attacks. v2.0 has a suit layer followed by a full-health Skelecog layer; overflow is not carried through the layer. Fires dismiss both layers. A revealed v2.0 Skelecog can attack that round, preserving the user's choice to follow TTR's Reinforced Plating rule. This does not add supervisors, Virtual Skelecog encounters, or Field Office promotion rules.

**Current TTR attack probabilities are not fully verified.** Most table values originate from classic source; 12 entries use the documented fallback estimates. Provenance is recorded in [COG_PROBABILITY_AUDIT.json](reports/COG_PROBABILITY_AUDIT.json). Attack name coverage and working models do not establish live-server selection odds or accuracy.

## Rewards

SOS cards, Fires, Remotes, and Doodle tricks use the caller's battle action. Unites do not.

SOS performs at its associated gag track. Normal cards cover Toon-Up, Trap, Lure, Sound, Drop, restock, Toons Hit, and Cogs Miss; Rocky, Loopy Loopenloop, and Lord Lowden Clear are included. Healing is split among living Toons. Restocking fills unlocked regular gags within pouch/carry limits, never level 7. Matching-track SOS supplies the implemented accuracy guarantee. Damage/healing events now distinguish each SOS caller from regular gag users so live playback does not omit or double-apply their health changes.

SOS and ordinary same-track damage are still resolved separately, without a joint SOS/gag combo bonus. Multi-SOS sequencing, mixed hit correlations, and current TTR reward ordering require further verification. Card choreography reuses the bundled Toon, gag, and teleport assets; modern per-card details remain partly adapted.

Damage remotes last 2/3/4 Cog phases and deal 45/60/75 damage to other Cogs per tick. Healing remotes last 2/3/4 phases and heal each living Toon 15/20/25. Their controlled Cog takes 45/90/150 damage on expiry. Remote performance replaces the normal attack; damage to other Cogs wakes their Lure. The antenna remains visible during control. Replacing an active remote or competing for the same Cog is rejected because current priority rules remain unverified. Remotes act in Cog-slot order.

Doodles have separate 0–10000 skill points per trick, interpolated healing/chance, seven native trick movies, and success/failure. Success awards five points. Mood is explicitly configured; full temperament, fatigue, recovery, and ownership simulation are absent.

Combat Unites offer Toon-Up 20/35/50/65/80, seven regular gags of a track, or 30 across tracks. Any living Toon can use its supply, including during attack playback. Toon-Up and Gag-Up share that caster's three-round cooldown and preserve its planned action. The GUI affects the living battle team. The engine supports an explicitly supplied radius for tests, but the current TTR radius is unverified; no default numerical radius is claimed.

## Presentation and known limits

The modern extracted gag/briefcase artwork, notes, target arrows, status panels, animal Laff faces, fonts, portraits, remote/doodle icons, and native media are used. Status targets follow the simulator's left-to-right formation. Speech temporarily replaces nameplates. Cog lights and floating damage values follow displayed health.

Toon HP is applied at playback impact so emergency Unites and immediate sadness can affect later attacks. The engine resolves one event at a time; this is not a networked TTR client. Throw/Squirt split base hits and bonus popups, while some other tracks still aggregate damage. v2.0 layer changes occur at event boundaries rather than a complete original cinematic.

Remaining work includes non-TNT Trap choreography, some Chomp teeth movement, modern Cog movie verification, Bad Joke body/dialogue fidelity, exact secondary sound overlap, and full facial choreography. The current audit distinguishes these from newly fixed defects. A passing hit/miss playback test does not prove frame-for-frame visual or audio parity.

Bosses, supervisors, Field Offices, reinforcements, reward earning, gag experience/recharging, Jellybean Unites, online play, and account progression are outside this ordinary-battle sandbox. Auto Toon choices are a local practice policy, not TTR AI or a model of real player decisions.

## Primary references

- [Official 2021 rebalance](https://cdn.toontownrewritten.com/community/notices/Rebalancing_Update_December_2021.pdf).
- [Official v4.0.0 rebalance](https://cdn.toontownrewritten.com/community/notices/Toontown_Rewritten_Rebalancing_v4.0.0_Patch_Notes.pdf).
- [v4.0.5 corrections](https://www.toontownrewritten.com/news/release-notes/367): later Trap stun and animation adjustments supersede earlier values.
- [v4.0.0 notes](https://www.toontownrewritten.com/news/release-notes/357): Reinforced Plating behavior.
- [TTR accuracy disclosure](https://www.toontownrewritten.com/news/release-notes/503): unpublished soft-cap thresholds.
- [Remote battle guidance](https://www.toontownrewritten.com/taskforce/battles).
- [Classic public client reference](https://github.com/open-toontown/open-toontown/tree/develop/toontown/battle): movie staging, inventory, and battle code, not current TTR source.

The existing research reports link individual TTR wiki pages for secondary rule tables; all 32 Cog page URLs are recorded in `cogs.json`. Reference source is read, not executed. Runtime artwork loads exclusively from `assets/ttr`; there is no GitHub asset fallback in the active resolver.
