# SOS cards: mechanics and presentation audit

Audit date: September 12, 2026. Scope: all 32 cards currently offered by this simulator (29 regular, three special), from selection and consumption through effects, NPC arrival/performance/departure, and cleanup. This is an audit, not a claim of complete TTR reproduction. Gameplay and the user's HUD layout were not edited for this audit.

## Evidence and limits

Bundled phase archives provide rigs, meshes, textures, animation clips and sounds. They do not provide the current TTR server calculations or complete client movie sequencing. Public classic source supplies useful sequencing, but its NPC table differs from modern TTR. Official TTR changes take precedence over classic code; conflicting wiki claims are flagged. A resource existing is not proof of how or when TTR uses it.

Sources inspected:
- [2021](https://cdn.toontownrewritten.com/community/notices/Rebalancing_Update_December_2021.pdf)
- [live](https://www.toontownrewritten.com/news/release-notes/284)
- [2016](https://www.toontownrewritten.com/news/item/340/the-sos-card-tweak-peek)
- [2019](https://www.toontownrewritten.com/news/item/600/no-more-fog-on-the-toontown-blog)
- [2024](https://cdn.toontownrewritten.com/community/notices/Toontown_Rewritten_Rebalancing_v4.0.0_Patch_Notes.pdf)
- [roster](https://toontownrewritten.wiki/SOS_Toon)
- [classic](https://github.com/open-toontown/open-toontown/blob/develop/toontown/battle/MovieNPCSOS.py)
- [npc](https://github.com/open-toontown/open-toontown/blob/develop/toontown/toon/NPCToons.py)
- [calc](https://github.com/open-toontown/open-toontown/blob/develop/toontown/battle/BattleCalculatorAI.py)

Locally inspected: support.py, battle_engine.py, combat_rules.py, sos_movies.py, lowden_movie.py, rewards_ui.py, battle_movies.py, trap_movies.py, scene_art.py, and assets/sos_portraits.json. Downloaded classic files are saved in work/sos-audit/. Existing tests were inspected; this audit adds separate diagnostic probes in that folder.

## How an SOS action works

1. Select a card from the caller's inventory as that Toon's battle action. It consumes the turn; it is not an out-of-turn Unite. TTR explicitly chose not to add an SOS cooldown. Canceling a selection should not spend a card. [2021 balance notes](https://cdn.toontownrewritten.com/community/notices/Rebalancing_Update_December_2021.pdf)
2. The simulator checks inventory, commits the action, then deducts one card during its support event. Gag-track SOS effects wait for the relevant track; restock, accuracy effects and Lowden execute in the early support stage. This exact cross-reward ordering is an implementation choice pending current TTR sequencing evidence.
3. Classic NPC movie code creates a separate NPC, brings it into battle, greets the caller and waves, turns it toward the action, performs the relevant movie, says goodbye, bows or curtsies, and teleports away. For track-based calls, its position is offset from the caller. It is not an additional selectable player Toon. Our code implements a simplified version of this sequence. [MovieNPCSOS](https://github.com/open-toontown/open-toontown/blob/develop/toontown/battle/MovieNPCSOS.py)
4. Healing includes the caller; attack cards target the living Cog group with track-specific exclusions. Restocking operates per living Toon. A card is a distinct action, not a gag deducted from the pouch. The simulator has these broad distinctions.
5. Inventory cancellation, invalid targets, battle interruption, multiple callers and NPC cleanup must be checked separately from whether a model loads. End-of-clip checks cannot prove frame timing or sound synchronization.

## Confirmed and high-priority findings

### Toon-Up SOS healing disappears in animated battles

Confirmed for Madam Chuckle, Daffy Don and Flippy. With four Toons at one HP and Cog attacks disabled, engine-only Flippy produces [46,46,46,46], but the animated round leaves [1,1,1,1]. The live event resolver rolls back the calculated HP to apply it at impact; base_gag_movie returns an empty Toon-Up sequence when there are no ordinary Toon-Up actions, so no callback delivers the SOS healing. Multiple or mixed healing actions require their own attribution tests too. This is a gameplay bug, not merely a missing visual.

### Trap SOS overwrites the wrong way

Official TTR release notes require an unlured Cog with an empty trap slot. The simulator instead toggles an existing trap off. Reproduced: put TNT on Cog 1, resolve Clerk Clara, and the trap becomes None. Three sequential SOS traps currently leave the third trap behind. The entire conflict/priority handling of ordinary Trap plus SOS in one round needs review; ordinary duplicate-trap cancellation must not simply be reused for SOS. [TTR v3.0.0](https://www.toontownrewritten.com/news/release-notes/284)

### Lil Oldman has a source conflict and a likely wrong duration

The simulator stores 6. Official 2021 notes specify 5; the individual Lil Oldman wiki page also says 5, whereas the wiki roster says 6. Use the official five-round rule as the implementation target unless later official evidence supersedes it. Nancy Gas and Stinky Ned remain separate duration-verification items. [Official notes](https://cdn.toontownrewritten.com/community/notices/Rebalancing_Update_December_2021.pdf), [Lil Oldman](https://toontownrewritten.wiki/Lil_Oldman)

### Restock is a simplified allocator

The code sorts all regular gags by descending level and fills them in dictionary order, subject to track, carry and pouch limits. It excludes level 7 and missing tracks. There is no last-purchase snapshot, and no randomized tie distribution. TTR announced purchase-aware distribution in 2016; its 2021 revision establishes 12/45 limits and high-level preference but does not fully document tie-breaking or the interaction with the earlier purchase rule. Our deterministic allocator must be labeled incomplete, not exact. It also does not limit restocks using each Toon's unlocked gag level. [2016 rules](https://www.toontownrewritten.com/news/item/340/the-sos-card-tweak-peek), [Restock](https://toontownrewritten.wiki/Restock)

### Status effects are global instead of attached to recipients

Toons Hit adds 75 percentage points to supported gag calculations; Cogs Miss subtracts 75, with a five-percent floor. They are not unconditional hit/miss switches. TTR restricts these effects to combatants present when applied. Our two battle-wide counters cannot encode this recipient snapshot and use max(old, new) for reapplication. Joiners, replacement Cogs, overlapping effects and precise duration accounting require explicit rules. Toon-Up's early accuracy return ignores hit_rounds altogether. The code uses 3/4/5 round counters, while the 2021 PDF lists 2/3/4 and the current wiki lists 3/4/5; counting the application round versus subsequent rounds must be verified before changing values. [TTR v3.0.0](https://www.toontownrewritten.com/news/release-notes/284)

The already documented TTR accuracy soft-cap limitation also applies to Toons Hit. Per the user's prior choice, do not invent the unpublished formula or silently substitute an estimate. This audit makes no formula changes. [Official soft-cap announcement](https://www.toontownrewritten.com/news/release-notes/all)

### Gag interactions need stronger representation

The engine executes SOS damage before ordinary gags of the same track and does not combine SOS values into the normal combo buckets. It also clears lure immediately after each SOS damage application. Consequently multiple Throw/Squirt SOS calls and mixed SOS/ordinary actions can see different lure state within the same track. Verify same-track combo eligibility, order, rounding, kill/overkill and lure knockback against current TTR before claiming parity. Classic calculations are useful evidence but cannot settle all changed rules.

A same-track SOS currently guarantees ordinary gag accuracy, except Toon-Up. This shortcut applies to the entire track, not a stored set of successful SOS targets. Its scope, especially mixed targets and lured Drop, deserves explicit tests. Actual Drop damage on a lured Cog is skipped later in the engine, even when the shortcut reports 100%.

Damaging SOS effects do enter the stun history; non-damaging rewards do not. This broad distinction agrees with TTR's 2024 revision. The grouping/count of one group SOS hit is not fully faithful: the engine appends a separate history entry per target, inflating a later attack's stun bonus. A focused four-Cog reproduction increased uncapped Whole Cream Pie accuracy by 100 points after one Barbara Seville call, rather than a single 25-point contribution. [2024 notes](https://cdn.toontownrewritten.com/community/notices/Toontown_Rewritten_Rebalancing_v4.0.0_Patch_Notes.pdf)

### NPC appearance and choreography are incomplete

Our ordinary guests use the player's generic medium shorts body and clothing, recolored with portrait metadata. They do not reproduce complete NPC DNA, body proportions, gender/clothing, or all facial animation. Every departure bows; classic code branches between bow and curtsy. Greeting and goodbye speech are missing. Durations are forced to generic values rather than preserved from each source movie.

performance() chooses one prop/animation per track, not per card. It holds a prop for 3.5 seconds; it does not dispatch each SOS through the full gag movie with an NPC actor. All Trap guests and persistent SOS traps default to TNT. Sound lacks its complete sound movie; Throw lacks its thrown projectile; Squirt lacks its full water effect. Drop uses a piano for all three cards and can visually drop on lured targets. These are presentation gaps even where HP is correct.

The current wiki's gag identities differ from the classic NPC table, which reuses high-tier gags for several card tiers. The table below records wiki identities as candidates for current TTR; they require current gameplay footage or authoritative current client evidence before being treated as verified choreography. [Roster](https://toontownrewritten.wiki/SOS_Toon), [Classic NPC table](https://github.com/open-toontown/open-toontown/blob/develop/toontown/toon/NPCToons.py)

### Support-only effects lack their main visual sequences

Classic accuracy SOS movies aim at each recipient and use pixieSpray, pixieDrop, pixieExplode, pixiePoof and pixieWall, with staggered timings and pixie-dust sound. Restock uses lipstick with explicit hand transforms, flying lips, a recipient reaction, and smooch audio, repeating per recipient. Our code only holds dust/lipstick and plays the performer animation; those effect sequences are missing. [MovieNPCSOS](https://github.com/open-toontown/open-toontown/blob/develop/toontown/battle/MovieNPCSOS.py)

### UI metadata is incomplete

Only the first 21 cards get stars. The eight restocks and three special cards do not. Descriptions show a bare track/value rather than explaining total healing split, duration versus modifier, or Lowden's dismissal. Individual health-panel hover reports the card name and targets, not full effect statistics. Card portraits exist, but correct portrait appearance does not imply correct full-body NPC appearance. Inventory capacity is a separate concern from battle execution.

## Every card

Values below are the current simulator data, not a blanket verification of live TTR. All ordinary cards have a shared arrival/departure audit above. Candidate gag names come from the wiki roster; exceptions/conflicts are explicit. Stars are the intended catalogue tier, not the current UI's completeness.

| Card | Stars | Current engine effect | Current presentation / audit finding |
|---|---:|---|---|
| Madam Chuckle | 3 | 60 total Laff, split among living Toons | Generic cubes; candidate: Megaphone. Check live healing application. |
| Daffy Don | 4 | 120 total Laff, split among living Toons | Generic cubes; candidate: Bamboo Cane. Check live healing application. |
| Flippy | 5 | 180 total Laff, split among living Toons | Cubes, but incomplete juggle sequence; check live healing application. |
| Clerk Will | 3 | 60 damage per eligible Cog, on activation | TNT fallback; candidate: Quicksand. Existing trap wrongly canceled. |
| Clerk Penny | 4 | 120 damage per eligible Cog, on activation | TNT fallback; candidate: Trapdoor. Existing trap wrongly canceled. |
| Clerk Clara | 5 | 180 damage per eligible Cog, on activation | TNT fallback; existing trap wrongly canceled; placement animation incomplete. |
| Stinky Ned | 3 | 4 lure counter | Big Magnet for every Lure card; candidate: Small Magnet; duration not independently settled. |
| Nancy Gas | 4 | 5 lure counter | Big Magnet; duration not independently settled; full source sequence missing. |
| Lil Oldman | 5 | 6 lure counter | Big Magnet; candidate: Hypno-goggles. Official duration 5, stored 6. |
| Barbara Seville | 3 | 35 damage per eligible Cog (Sound) | Held fog horn; candidate: Aoogah; full Sound effect/audio missing. |
| Sid Sonata | 4 | 55 damage per eligible Cog (Sound) | Held fog horn; candidate: Elephant Trunk; full Sound effect/audio missing. |
| Moe Zart | 5 | 75 damage per eligible Cog (Sound) | Held fog horn; full Sound effect/audio missing. |
| Clumsy Ned | 3 | 60 damage per eligible Cog (Drop) | Piano for every Drop card; candidate: Big Weight; lured-target visuals wrong. |
| Franz Neckvein | 4 | 100 damage per eligible Cog (Drop) | Piano; candidate: Safe; lured-target visuals wrong. |
| Barnacle Bessie | 5 | 170 damage per eligible Cog (Drop) | Piano; timing/impact alignment and lured-target visuals need correction. |
| Soggy Bottom | 3 | +75 accuracy; 3 counter | Dust held; recipient particles/audio missing; counter/snapshot audit required. |
| Soggy Nell | 4 | +75 accuracy; 4 counter | Dust held; recipient particles/audio missing; counter/snapshot audit required. |
| Sticky Lou | 5 | +75 accuracy; 5 counter | Dust held; recipient particles/audio missing; counter/snapshot audit required. |
| Flim Flam | 3 | −75 Cog accuracy; 3 counter | Dust held; recipient particles/audio missing; counter/snapshot audit required. |
| Mr. Freeze | 4 | −75 Cog accuracy; 4 counter | Dust held; recipient particles/audio missing; counter/snapshot audit required. |
| Julius Wheezer | 5 | −75 Cog accuracy; 5 counter | Dust held; recipient particles/audio missing; counter/snapshot audit required. |
| Professor Guffaw | 3 | Restock Toon-Up: up to 12 gags per Toon | Lipstick held; flying lips/audio absent; restock allocation incomplete; stars missing. |
| Clerk Ray | 3 | Restock Trap: up to 12 gags per Toon | Lipstick held; flying lips/audio absent; restock allocation incomplete; stars missing. |
| Doctor Drift | 3 | Restock Lure: up to 12 gags per Toon | Lipstick held; flying lips/audio absent; restock allocation incomplete; stars missing. |
| Melody Wavers | 3 | Restock Sound: up to 12 gags per Toon | Lipstick held; flying lips/audio absent; restock allocation incomplete; stars missing. |
| Baker Bridget | 3 | Restock Throw: up to 12 gags per Toon | Lipstick held; flying lips/audio absent; restock allocation incomplete; stars missing. |
| Sofie Squirt | 3 | Restock Squirt: up to 12 gags per Toon | Lipstick held; flying lips/audio absent; restock allocation incomplete; stars missing. |
| Shelly Seaweed | 3 | Restock Drop: up to 12 gags per Toon | Lipstick held; flying lips/audio absent; restock allocation incomplete; stars missing. |
| Professor Pete | 5 | Restock All: up to 45 gags per Toon | Lipstick held; flying lips/audio absent; restock allocation incomplete; stars missing. |
| Rocky | 5 | 132 damage per eligible Cog (Throw) | Birthday cake held in hand; Wedding Cake projectile/movie missing. |
| Loopy Loopenloop | 5 | 115 damage per eligible Cog (Squirt) | Bottle held in hand; Geyser sequence missing. |
| Lord Lowden Clear | 5 | Dismiss every living Cog, including both v2 layers | Custom Cashbot disguise and group cannons; exact disguise, entrance and timing unverified. |

Rocky and Loopy are special attack cards, and Lowden is group dismissal rather than damage of zero. Their dedicated pages corroborate those identities: [Rocky](https://toontownrewritten.wiki/Rocky), [Loopy](https://toontownrewritten.wiki/Loopy_Loopenloop), [Lowden](https://toontownrewritten.wiki/Lord_Lowden_Clear). Special-event acquisition, VP rewards, collection limits across a persistent account, and boss-only restrictions are outside this ordinary-battle simulator's implemented scope.

## Behavioral coverage and reproducibility

- work/sos-audit/probe.py ran 512 engine cases: every card with each combination of one to four Toons and one to four Cogs. Toons started at one HP with empty gags; Cog attacks were suppressed to isolate the card. These are recorded observations, not 512 proofs of TTR equivalence.
- reports/sos-audit/mechanics.json stores healing, damage, lure/trap state, restock totals, consumption, and status counters. It also contains focused existing-trap and three-SOS-trap reproductions.
- work/sos-audit/playback.py exercises a complete animated round for every card, isolating healing from enemy damage and recording leftover guests. It fast-forwards intervals and disables audio; it does not prove audible synchronization, visual quality between frames, or real-time race freedom.
- Playback completed for 32/32 cards.
  - SOS: Madam Chuckle: actual animated-round Toon HP = [1, 1, 1, 1].
  - SOS: Daffy Don: actual animated-round Toon HP = [1, 1, 1, 1].
  - SOS: Flippy: actual animated-round Toon HP = [1, 1, 1, 1].

The engine-only four-Toon Flippy case ends at [46,46,46,46]; the animated case confirms the missing-healing bug described above. All 32 clips completed and removed their ordinary guests, but completion is not correctness.

## Remaining questions before claiming full fidelity

- Exact current status duration, application-round counting, refresh/stack rules and expiration after the final enemy attack.
- Current three/four-star Lure durations and per-card gag identities where classic code and wiki differ.
- Mixed SOS/ordinary-gag damage bonuses, simultaneous lure knockback and overkill/v2 transitions.
- Multiple simultaneous SOS traps versus ordinary traps, railroad override, and target vacancy ordering.
- Last-purchase restock interaction with newer limits, unlocked levels, missing tracks, and tie distribution.
- Full current NPC DNA/clothing and Lowden disguise, individual movie frame offsets, camera cuts, dialogue and all sounds.
- Reward selection during invalid/full-health/all-trapped situations; consumption if targets disappear before execution.
- Accuracy-effect recipients joining/leaving and newly arriving or transformed Cogs.
- Boss-specific immunities, Field Office locked tracks and reward-only encounters are not proven by ordinary-battle probes.

## Recommended implementation sequence

1. Fix the confirmed live Toon-Up delivery bug, and add expected-result tests.
2. Correct SOS trap vacancy behavior and preserve normal trap-conflict rules separately.
3. Move every card's tier, effect, gag identity, NPC identity and timing into explicit metadata, keeping disputed values labeled.
4. Make status effects recipient-scoped and settle duration/reapplication with evidence.
5. Rework restock allocation and mixed-action resolution with specific regression cases.
6. Dispatch the NPC through full gag choreography; implement the separate restock and accuracy particle sequences.
7. Review real-time footage and sound for each card, then check multi-caller, defeat, escape and New battle cleanup.

Until those are complete, it would be misleading to describe SOS cards as entirely accurate, even though every card is listed and many effects calculate correctly in isolation.
