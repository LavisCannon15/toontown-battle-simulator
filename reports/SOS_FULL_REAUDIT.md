# SOS cards: complete roster re-audit

This is a fresh audit of all 32 cards offered by the simulator. No game behavior or HUD positioning was changed. The previous report remains at SOS_FULL_AUDIT.md; this report supersedes its Lowden presentation status and adds current execution results and edge cases.

## Result

All 32 isolated animated cases complete, spend exactly one card (2 to 1), and remove their NPC guests. Several cards nevertheless have incorrect gameplay effects or incomplete presentation. Completion is not a fidelity test.

### Highest-priority confirmed failures

1. **All three Toon-Up SOS cards fail to deliver live healing.** With four Toons at 1 HP and enemy damage disabled, Madam Chuckle, Daffy Don and Flippy each leave [1,1,1,1] in animated playback. Engine-only Flippy gives [46,46,46,46]. The live movie rolls HP back pending an impact callback; the empty ordinary Toon-Up action list does not supply that callback. This remains unfixed.
2. **SOS Trap cancels occupied traps.** Existing TNT becomes None after Clara. Three SOS trap calls leave Clara's trap, reflecting toggle/cancel behavior instead of skipping occupied targets. Official TTR says SOS Trap only places in vacant, unlured slots. Ordinary Trap cancellation must remain separate.
3. **Restocks give locked gags.** A Toon with level-one tracks and an empty pouch receives 2 Whole Fruit Pies, 7 Whole Cream Pies and 3 Birthday Cakes from a 12-gag Throw restock. Allocator checks missing track, pouch, carry limit and level-seven exclusion but ignores unlocked levels. It lacks a last-purchase snapshot and uses deterministic ordering.
4. **One group Sound SOS grants four stun contributions.** Barbara Seville creates four history entries; uncapped Whole Cream Pie accuracy rises by 100 points. The intended single-action contribution is 25. This is visible in calculation even where a cap hides the final difference.
5. **Toons Hit ignores Toon-Up.** Setting its active counter changes Feather's uncapped accuracy by zero because the Toon-Up calculation returns before applying the status bonus.
6. **Accuracy statuses are battle-global.** Recipient identities, newly arriving/replaced Cogs, overlapping durations and refresh behavior are not represented. TTR specifies effects on combatants present when called.

### Values, targeting, and order

The table below reports configured simulator values, not a certification of current TTR parity. Toon-Up uses a total divided among living Toons, including caller, with HP clamping. Attack cards target living Cogs; lured targets block Drop mechanically. Lowden dismisses the group with layer bypass. All SOS selections consume an action rather than behaving like out-of-turn Unites.

Official 2021 notes specify Lil Oldman at five rounds; support.py configures six. A fresh eight-round probe with actual Cog phases shows his counter ending the application round at five, then four. This confirms the decrement boundary but does not resolve whether TTR's five counts the application phase; duration must be tested by actual skipped enemy turns. Stinky Ned/Nancy Gas configure 4/5. Accuracy tiers configure 3/4/5 and decrement at round end. Do not treat raw counters as proof of matching duration semantics.

Multiple same-track SOS and ordinary gags are not integrated into one normal combo representation. SOS damage executes first and immediately clears lure, so later attacks can see a different state. Damage rounding, same-track bonuses, eligibility after kills, v2 transitions and status stacking still require authoritative expected-result cases. A same-track SOS accuracy shortcut also applies broadly across the track rather than carrying explicit successful target identities.

## Card-by-card coverage

| Card | Configured effect | Live run | Findings |
| --- | --- | --- | --- |
| Madam Chuckle | Toon-Up: 60 | Completed; healing missing | Live healing fails; generic juggling performance for all three. |
| Daffy Don | Toon-Up: 120 | Completed; healing missing | Live healing fails; generic juggling performance for all three. |
| Flippy | Toon-Up: 180 | Completed; healing missing | Live healing fails; generic juggling performance for all three. |
| Clerk Will | Trap: 60 | completed | Existing traps incorrectly canceled; generic TNT model/placement for every tier. |
| Clerk Penny | Trap: 120 | completed | Existing traps incorrectly canceled; generic TNT model/placement for every tier. |
| Clerk Clara | Trap: 180 | completed | Existing traps incorrectly canceled; generic TNT model/placement for every tier. |
| Stinky Ned | Lure: 4 | completed | Duration review required; all guests hold big magnet; individual gag choreography absent. |
| Nancy Gas | Lure: 5 | completed | Duration review required; all guests hold big magnet; individual gag choreography absent. |
| Lil Oldman | Lure: 6 | completed | Duration review required; all guests hold big magnet; individual gag choreography absent. Official five-round rule versus configured six needs phase-count validation. |
| Barbara Seville | Sound: 35 | completed | One hit history entry per Cog inflates stun; generic held fog horn, incomplete effects/audio. |
| Sid Sonata | Sound: 55 | completed | One hit history entry per Cog inflates stun; generic held fog horn, incomplete effects/audio. |
| Moe Zart | Sound: 75 | completed | One hit history entry per Cog inflates stun; generic held fog horn, incomplete effects/audio. |
| Clumsy Ned | Drop: 60 | completed | Engine skips lured Cogs, but generic piano movie does not filter them; per-card props missing. |
| Franz Neckvein | Drop: 100 | completed | Engine skips lured Cogs, but generic piano movie does not filter them; per-card props missing. |
| Barnacle Bessie | Drop: 170 | completed | Engine skips lured Cogs, but generic piano movie does not filter them; per-card props missing. |
| Soggy Bottom | Toons Hit: 3 | completed | Global counter, no recipient snapshot; no Toon-Up accuracy effect; pixie effects missing. |
| Soggy Nell | Toons Hit: 4 | completed | Global counter, no recipient snapshot; no Toon-Up accuracy effect; pixie effects missing. |
| Sticky Lou | Toons Hit: 5 | completed | Global counter, no recipient snapshot; no Toon-Up accuracy effect; pixie effects missing. |
| Flim Flam | Cogs Miss: 3 | completed | Global counter, no recipient snapshot; pixie effects missing. |
| Mr. Freeze | Cogs Miss: 4 | completed | Global counter, no recipient snapshot; pixie effects missing. |
| Julius Wheezer | Cogs Miss: 5 | completed | Global counter, no recipient snapshot; pixie effects missing. |
| Professor Guffaw | Restock Toon-Up: 12 | completed | Restock allocator ignores unlocks/purchase history; held lipstick, no flying lips/recipient effect; stars missing. |
| Clerk Ray | Restock Trap: 12 | completed | Restock allocator ignores unlocks/purchase history; held lipstick, no flying lips/recipient effect; stars missing. |
| Doctor Drift | Restock Lure: 12 | completed | Restock allocator ignores unlocks/purchase history; held lipstick, no flying lips/recipient effect; stars missing. |
| Melody Wavers | Restock Sound: 12 | completed | Restock allocator ignores unlocks/purchase history; held lipstick, no flying lips/recipient effect; stars missing. |
| Baker Bridget | Restock Throw: 12 | completed | Restock allocator ignores unlocks/purchase history; held lipstick, no flying lips/recipient effect; stars missing. |
| Sofie Squirt | Restock Squirt: 12 | completed | Restock allocator ignores unlocks/purchase history; held lipstick, no flying lips/recipient effect; stars missing. |
| Shelly Seaweed | Restock Drop: 12 | completed | Restock allocator ignores unlocks/purchase history; held lipstick, no flying lips/recipient effect; stars missing. |
| Professor Pete | Restock All: 45 | completed | Restock allocator ignores unlocks/purchase history; held lipstick, no flying lips/recipient effect; stars missing. |
| Rocky | Throw: 132 | completed | Rocky uses held birthday cake rather than complete Wedding Cake movie; mixed-track/lure handling unverified. Stars missing. |
| Loopy Loopenloop | Squirt: 115 | completed | Loopy uses held bottle rather than Geyser movie; mixed-track/lure handling unverified. Stars missing. |
| Lord Lowden Clear | Fire: 0 | completed | Dedicated Lowden sequence now implemented; exact current TTR card transforms/dialogue/camera not verified. Stars missing. |

## Models, animations, sounds and UI

**Ordinary NPCs:** code still constructs generic medium Toon bodies and player clothing. Portrait metadata supplies species/color/head variant but not complete NPC DNA or clothing. ColorScale is broadly applied to muzzle/ears and can mix with player tint. The dedicated Lowden fix does not repair other NPC appearances. Arrival uses phone, reverse teleport, wave; departure always uses bow and teleport. Per-character curtsy, dialogue and greeting choices are absent.

**Gag movies:** performance() chooses a single clip/prop per track and holds it for 3.5 seconds. Ordinary gag animation improvements do not automatically reach SOS performers. Toon-Up uses cubes for every card; Trap uses TNT; Lure uses big magnet; Sound uses fog horn; Drop uses pianos. Rocky and Loopy still lack their dedicated projectile/Geyser sequences. SOS Drop's visual targeting tests HP, not lure, so it can show a hit where mechanics skip damage.

**Non-damaging cards:** restock lacks the source flying-lips path, recipient reactions and smooch cue sequence. Accuracy effects lack the source pixieSpray/pixieDrop/pixieExplode/pixiePoof/pixieWall sequence. Merely loading dust or lipstick does not reproduce these movies. Current support performance code has no per-card attack sound dispatch; teleport audio alone does not cover the effect.

**Lowden now differs from the old report:** dedicated red dog/Cashbot disguise, original muzzle/ears, no caller animation, four-second head-propeller entrance/exit with corrected reverse frame boundaries, Red Tape throw-object with bundled pink slip, parallel cannons after throw, corrected cannon orientation with preserved Cog facing, kapow/clouds/cannon return. Exact card arc/scale/release, full NPC DNA, dialogue and cinematic shots remain unverified. Four-second flight is the user's preference, not an inferred TTR timing.

**UI:** all 32 are listed, eight per page with track filters and inventory counts. Empty rewards are disabled. Only the first 21 get star icons; the eight restocks and three special cards omit them. Lowden's description exposes “Fire · 0” instead of explaining group dismissal. Heal splitting, status duration, restock limits and relevant target exclusions need clearer descriptions. Portrait heads do not establish matching battle bodies. Layout positions were preserved.

## Evidence and reproducibility

- 512 engine cases: each card × 1–4 Toons × 1–4 Cogs. Enemy actions are suppressed to isolate effects, so these do NOT verify duration decrement. reports/sos-reaudit/mechanics.json.
- 32 isolated live playback cases: every card, four injured Toons, enemy actions suppressed. reports/sos-reaudit/playback.json.
- All 32 plan replacements leave inventory untouched; zero-inventory call rejected. Additional restock, stun, Toon-Up accuracy and lured-Drop probes: edges.json.
- Eight-round real-Cog-phase status probes (attack rolls forced to miss): status-rounds.json.
- Multi-caller/mixed-gag and New battle interruption probes: interactions.json, summarized below when complete.
- Scripts are in work/sos-reaudit. Existing source references in work/sos-audit remain static, not executed.

These are runtime and source audits. Fast-forwarded intervals cannot establish continuous visual/audio fidelity. Sound playback was disabled in diagnostic runs. Complete current TTR server/client sequencing is not present in the extracted phase assets. Boss/Field Office restrictions, acquisition, persistent collection limits, every NPC outfit, and every animation frame remain outside verified coverage.

## Sources

- TTR v3.0.0: https://www.toontownrewritten.com/news/release-notes/284 — target vacancy, status recipients, effect values, restock limits.
- 2021 balance PDF: https://cdn.toontownrewritten.com/community/notices/Rebalancing_Update_December_2021.pdf — Lil Oldman and reward revisions.
- 2016 restock/presentation changes: https://www.toontownrewritten.com/news/item/340/the-sos-card-tweak-peek.
- TTR roster (secondary, not sufficient for disputed details): https://toontownrewritten.wiki/SOS_Toon.
- Classic NPC sequencing: https://github.com/open-toontown/open-toontown/blob/develop/toontown/battle/MovieNPCSOS.py.
- User-provided Lowden demonstration: https://www.youtube.com/shorts/oQSXv7RyrH8.

## Repair order

1. Deliver Toon-Up SOS health through live event callbacks; compare live vs engine outcomes.
2. Separate SOS Trap vacancy rules from ordinary duplicate-trap cancellation.
3. Fix restock unlock filtering and stun action grouping; apply accuracy statuses to intended calculations/recipients.
4. Validate durations and mixed-card resolution with explicit enemy-phase scenarios.
5. Introduce per-card NPC/gag metadata and route NPC performances through complete gag/support movie sequences.
6. Complete stars/descriptions and verify each card's appearance, sound and timing against current footage.

## Fresh mixed/interrupt results

- SOS: Flippy, SOS: Madam Chuckle: {"hp": [1, 1, 1, 1], "guests": 0, "completed": true}
- SOS: Flippy, Feather: {"hp": [56, 46, 46, 46], "guests": 0, "completed": true}
- SOS: Clerk Clara, Hypno Goggles: {"hp": [1, 1, 1, 1], "guests": 0, "completed": true}
- SOS: Rocky, SOS: Loopy Loopenloop: {"hp": [1, 1, 1, 1], "guests": 0, "completed": true}
- SOS: Lord Lowden Clear, SOS: Flippy: {"hp": [1, 1, 1, 1], "guests": 0, "completed": true}

New battle interruption checked for all 32 cards at 1.5 seconds into the initial support event. Failures: 0. This validates early-arrival interruption, not every mid-performance frame.
