# Battle mechanics audit — September 12, 2026

**Historical baseline:** several findings below have since been fixed. See [implementation status](IMPLEMENTATION_UPDATE.md) for the verified changes and remaining work.

The simulator is an ordinary-battle practice sandbox, not yet a faithful TTR combat calculator. This audit inspected the current Python implementation and compared it with official balance notes and the TTR community wiki. No live-server parity testing was performed. Extracted phase assets contain artwork, models, clips and sounds; they do not supply the battle calculation code.

## Confirmed discrepancies

1. **Accuracy soft cap missing.** `battle_engine.py:228–261` clamps ordinary calculated accuracy to 95. TTR changed this to a soft cap. The missing behavior affects stun-heavy strategies and accuracy rewards. The exact replacement formula still requires verification; the release note establishes the discrepancy, not the complete algorithm. [Official release note](https://www.toontownrewritten.com/news/release-notes/505).

2. **Presentation's Lure tier is wrong.** `battle_engine.py:251` computes `(level+1)//2`: Presentation becomes tier 4 and Hypno-goggles tier 3. They belong to the same bonus tier. Thus their pairing receives a 15-point rather than 20-point additional Lure bonus before the cap. [Lure tiers](https://toontownrewritten.wiki/Lure).

3. **Mixed-lineup accuracy is incomplete.** The lured-ratio bonus is implemented only for Sound, counts only Lure, and omits level-7 Throw/Squirt and remote-controlled Cogs. Reproduction: Wedding Cake against four level-12 Big Cheeses reports 80% both before and after luring one Cog. [Accuracy rules](https://toontownrewritten.wiki/Accuracy).

4. **Training is assumed maxed.** Every ordinary damage calculation adds 60 track-experience accuracy, and gag powers are fixed at maximum. No per-track unlock/experience state exists. High Dive also has 70 base accuracy in the data and shares the unconditional 95% Toon-Up result, rather than preserving its distinct 95 base value. [Accuracy and track experience](https://toontownrewritten.wiki/Accuracy), [Toon-Up table](https://toontownrewritten.wiki/Toon-Up).

5. **Unites cannot interrupt playback.** `panda_battle.py:282` blocks their menu while animating. Furthermore, the entire round is calculated before its movie starts. Supporting emergency mid-battle Unites requires event-by-event calculations, not just enabling the button. There is no spatial radius check; all living teammates receive the effect. The existing stock limits, healing amounts, restock caps and three-round cooldown cover part of the system. [Unites](https://toontownrewritten.wiki/Unite).

6. **Twelve Cog attack entries have estimated probabilities.** `cogs.json` explicitly marks 85% accuracy and selection weight 25 assumptions for: Micromanager/Close the Loop; Corporate Raider/Hostile Takeover; The Big Cheese/Glower Power and Power Trip; Big Wig/Finger Wag and Quash; Penny Pincher/Nickel and Dime; Money Bags/Money Talks; Robber Baron/Synergy and Embezzle; Mr. Hollywood/Finger Wag and Beguile. Damage tables are separate from these probabilities. These assumptions prevent exact difficulty comparisons; this audit does not claim a verified replacement probability.

## Missing battle systems

7. **Version 2.0 layers.** The Skelecog option changes appearance while retaining an ordinary Cog profile. There is no suit-to-skeleton second health layer, layer transition behavior, or remote persistence across it. A level-12 v2.0 requires two 196-HP layers. Current Reinforced Plating permits an attack after transformation; the older damage-reduction implementation was removed. [v2.0 rules](https://toontownrewritten.wiki/Version_2.0_Cogs), [official 2024 changes](https://cdn.toontownrewritten.com/community/notices/Toontown_Rewritten_Rebalancing_v4.0.0_Patch_Notes.pdf).

8. **Encounter rules beyond ordinary battles.** Cog health validation stops at level 12. No supervisor battles, boss phases, reinforcement waves, Field Office track recovery, Boiler modes or their encounter status effects exist. Those require encounter controllers, not more Cog models. [Supervisors](https://toontownrewritten.wiki/Supervisor_Cogs), [Field Offices](https://toontownrewritten.wiki/Sellbot_Field_Office).

9. **Doodle state and progression.** Two booleans select trained/untrained and positive/negative endpoints. Individual trick training, fatigue, traits and mood changes are absent. Repeated calls therefore do not evolve the pet's condition. [Doodle training and moods](https://toontownrewritten.wiki/Doodles).

10. **Experience and resource recovery.** There is no gag XP award, gradual power increase, level-7 recharge, reward earning or persistent progression. Level-7 stock exists, but the 500-point recharge loop does not. No between-encounter economy or jellybean Unites exists. [Skill points](https://toontownrewritten.wiki/Skill_points), [Wedding Cake recovery](https://toontownrewritten.wiki/Wedding_Cake).

## Simplifications needing targeted verification

11. **SOS combinations and ordering.** `resolve_support` applies SOS damage separately before ordinary same-track gags. They never enter one combined damage group. Ordinary gags also receive unconditional same-track SOS accuracy. Mixed SOS/gag damage, guarantees, multiple-card order and stun accounting need dedicated reference cases; do not rely on the existing documentation alone to declare all these behaviors correct or incorrect. Standard SOS values and inventory limits broadly match the published table. [SOS table](https://toontownrewritten.wiki/SOS_Toon).

12. **Remote edge cases.** Replacing an active remote or assigning two in one round is rejected. Effects resolve in slot order. Basic duration, per-tick effect and expiry damage match the published values, but replacement priority, competing effects and mixed Lure interactions are not validated. [Remote values](https://toontownrewritten.wiki/Remote_control).

13. **Invalidated actions and inventory.** All ordinary gag stock is deducted before gag phases. Reproduction: choose Grand Piano against a Cog that a teammate fires; the Piano is spent even though it never lands. Live cancellation/refund/retarget behavior needs explicit cases. This is confirmed simulator behavior, not a claim that every such live action is refunded.

14. **Group hit correlation and healing distribution.** Same-track hit results are grouped by action signatures and first-gag metadata; mixed single/group attacks merit dedicated tests. Group healing splits fixed shares across living recipients and caps them independently, with no redistribution. Correct treatment of excess healing and multiple simultaneous heals needs verification.

## Rules already represented

All seven gag tracks and level-7 stocks; ordinary gag-track order; standard Cog profiles and variable 1–4 participant lineups; organic bonuses; Sound carry limits; Trap/Lure selection restrictions; trap cancellation; Drop missing lured targets; Sound waking Cogs; ordinary same-track combo and Throw/Squirt knockback; self-excluding gag Toon-Up; ordinary SOS/Fire/remote/Doodle actions; separate Unite use; sad Toons excluded from later attacks.

Presence is not proof of complete correctness. In particular, mixed-action cases above remain open. The Trap stun value of 50 and additional group-trap placement bonus are consistent with the later [official v4.0.5 update](https://www.toontownrewritten.com/news/release-notes/367); changing them back to the original v4.0.0 values would be a regression.

## Presentation, separately

Extracted assets are now bundled and used, but prop attachment, camera work, effects and timing remain adapted. Remote ticks still lack full joke/dance sequences; SOS and Doodle cinematics remain abbreviated. These are visual gaps, separate from numerical battle accuracy.

## Recommended work order

First correct ordinary-battle accuracy, Lure tiers and mixed-target calculations, with sourced numerical cases. Next redesign resolution to support mid-playback Unites and validate reward/inventory edge cases. Then add v2.0 layers and reinforcement encounters. Add bosses and Field Offices only after ordinary battle calculations are reliable.

Existing tests establish regression coverage, not equivalence with TTR. The older MECHANICS.md mixes historical UI descriptions with current rules and should not be treated as a current parity certificate. This audit made no gameplay changes.
