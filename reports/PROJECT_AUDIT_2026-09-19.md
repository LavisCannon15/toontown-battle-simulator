# Project audit — September 19, 2026

The audit found and corrected several real bugs, including one that could erase SOS healing from the live battle state. The project now passes the mechanics suite, all-gag and all-Cog-attack playback checks, mixed reward/gag consistency checks, and the listed interface/lifecycle checks. It still has documented fidelity gaps; passing playback is not proof of exact TTR behavior.

## Scope and method

Reviewed the active Python/Panda3D application: battle calculation/event delivery, regular gag dispatch, SOS and other rewards, impact-time health, character reactions, setup/reset, targeting, timer/Auto controls, menus, camera/window sizing, resource resolution, and documentation. Archived Tkinter code and third-party dependencies were not audited as active application code.

Used three kinds of evidence:

1. The **bundled extracted TTR files** for actual models, channels, fonts, icons, particles, and audio. Checked all files against their recorded extraction hashes and all mapped movie-resource paths against the active resolver.
2. **Local classic source references** for the movie structure that the files alone do not specify, particularly `MovieSquirt`, `MovieSuitAttacks`, `MovieTrap`, `MovieLure`, and Toon/ToonHead. Reference code was read, not imported or run.
3. **Official TTR publications** to distinguish modern behavior from classic assumptions. Current TTR Python sequencing and server tables are not present in the extracted phase media.

The review included broad coverage tests and targeted reproductions. It did not involve frame-by-frame comparison or listening to every complete movie. Assertions about fidelity below are limited accordingly.

## Confirmed issues corrected

| Issue | What was wrong | Correction and evidence |
|---|---|---|
| **Mixed SOS/gag health attribution** | Regular same-track playback inherited the full health event, including SOS contributions. Rocky plus Cupcake displayed 190 HP instead of 58 on the chosen 196-HP Cog; Loopy plus Squirting Flower displayed 192 instead of 77. More seriously, Flippy plus two Feathers could leave actual live Toon HP at `[10,10,20,20]` instead of `[55,55,65,65]`. | The engine records health/status snapshots for each SOS caller and a separate regular-gag health list. Each performer owns its playback effects once. Eleven mixed cases now match an independent headless resolution for health and statuses. Changes: `battle_engine.py`, `battle_movies.py`, `sos_movies.py`. |
| **Repeated SOS Lure entry** | NPC Lure could replay a reaction on Cogs already lured before that SOS, or regular Lure could inherit the wrong pre-SOS status snapshot. | Both paths use their own pre-action Lure state and the existing fresh-target filter. Unit regression covers one already-lured Cog plus SOS and regular group Lure. Changes: `battle_engine.py`, `sos_visuals.py`, `battle_movies.py`. |
| **SOS Lure skipped trap activation** | The NPC performed Lure and generic damage presentation even when the health change came from springing a trap. | SOS Lure now dispatches through the same trap/TNT/Railroad activation movies as player Lure, with health owned by that sequence. Live TNT and Railroad cases pass with no duplicated damage or leftover guest. Changes: `sos_visuals.py`, `sos_movies.py`. |
| **Loopy's Geyser damage was early** | All SOS damage was scheduled at 2.9 seconds while the Geyser launches had individual delays. | Each Cog's health change follows its own Geyser contact. Deterministic offsets `0/.2/.5/.9` verify that only the first Cog has lost HP at 3.0 seconds and the fourth has not yet lost HP at 3.5 seconds. Changes: `sos_visuals.py`, `sos_movies.py`. |
| **Storm Cloud reaction missing/overridden** | Storm Cloud relied on the shared Squirt reaction at the final contact; a later Squirt could replace its native `soak` motion. The Lure knockback prefix also used the generic small-Squirt reaction. | Schedule the bundled `soak` at the cloud's contact, preserve it in mixed Squirt selections, and use the source `soak` prefix before body-specific knockback. Tested A/B/C bodies, lured/unlured, and mixed Storm Cloud/Fire Hose. Changes: `squirt_sequence.py`, `battle_movies.py`. |
| **Chomp reaction incomplete** | Only the first generic reaction was used; the source cringe/spit slices and repeated reverse/forward mouth motion were missing. | Added the nine source reaction slices using the extracted `cringe`/`spit` channels. Reaction starts at 3.2 seconds and damage at 4.6 seconds per the classic reference. Fatal damage cancels the reaction and begins sadness. Tested hit, miss, fatal/nonfatal, and reset. Changes: `chomp_reaction.py`, `cog_choreography.py`. The teeth prop's full route remains a separate gap. |
| **Identical Toons targeted incorrectly** | Cog targeting converted Toon objects to indices with value equality. Two identical Toon configurations could both be recorded as index 0. | Carry participant indices through target selection, damage, and misses. A four-identical-Toon group-attack regression preserves `[0,1,2,3]`. Change: `battle_engine.py`. |
| **Target-panel click-through** | World picking used an old fixed screen strip, despite the target panel having moved and changed scale. | Block picking inside the panel's actual transformed bounds and active GUI regions. Bounds checked across position/scale changes and hidden state. Changes: `ui_hit_test.py`, `panda_battle.py`. |
| **Setup retained a temporary battle buff** | Setup copied Toon Accuracy Up into the new starting configuration. | Clear it alongside cooldown/escaped state when applying setup; test also verifies it cannot reappear through New battle. Change: `panda_battle.py`. |
| **Documentation contradicted the application** | Main docs described the removed classic reward layout, GitHub asset fallback, no v2.0 support, no player Auto, and New battle restoring the original default. | Replaced README/MECHANICS with the current behavior and explicit limits. Earlier documents are preserved in the audit backup and older reports are treated as history. |

User-custom gag-panel positions/scales were preserved. No extracted game files were edited.

## Remaining findings and concrete next steps

These are open work or evidence limits, not claims that the corresponding feature crashes.

### 1. Some damage presentation remains aggregated

`drop_sequence.py` applies a target's complete regular Drop damage at its final prop impact. `sound_sequence.py` applies the complete Sound total at the final group/Opera contact. Throw/Squirt already have per-action contact attribution in `hit_damage.py`.

**Next step:** extend per-action contact allocation to Drop and then Sound, retaining one authoritative total and the source-specific same-level Sound grouping. Add mixed-level/mixed-target and overkill cases before changing the schedule. Also verify SOS bonuses and same-track multi-SOS timing against current TTR; self-consistency tests alone cannot establish those rules.

### 2. Non-TNT traps still use abbreviated choreography

`trap_movies.py` levels 1–5 use generic toss/button and walk/reaction paths. The classic `MovieTrap` reference has distinct Banana/Rake/Marbles flight, growth, hand/prop transforms, and sound tracks. For example, the reference names `TL_banana.ogg`, `TL_marbles.ogg`, and `TL_rake_throw_only.ogg`, while the current generic thrown-trap path uses a pie-throw cue. Activation/return paths are also simplified. TNT is specialized, but its fuse spark detail is not complete.

**Next step:** port each level's complete placement and activation timeline from the references using the bundled models, rather than changing just one scale or sound. Check persistent trap ownership, cancellation, earlier-round replacement, fatal hits, and interruption. SOS now shares the same dispatcher, so these improvements will cover NPC-triggered traps too.

### 3. Current TTR probabilities and the soft cap remain unresolved

The attack table has 135 entries; 12 use the recorded fallback probabilities, and the rest are predominantly classic values. Their provenance is explicit. This audit found no current server probability table in the extracted media. The legacy 95% cap remains the user's chosen disclosed limitation.

**Next step:** change these only when a reliable current rule/table is available. Keep the limitation visible. Do not turn an asset name, animation duration, old table, or community estimate into a claimed current TTR formula.

### 4. Modern Cog choreography and Bad Joke need stronger evidence

Nine attack names lack a dedicated function in the classic reference audit: Close the Loop, Hostile Takeover, Flood the Market, Throw Book, Quash, Nickel and Dime, Money Talks, Embezzle, and Beguile. Several now have dedicated local movie implementations, but that does not prove current TTR equivalence. TTR's own v4.0.5 notes mention changes to most of these animations. Bad Joke uses the bundled antenna/bubble/sounds; its body channel and complete dialogue fidelity remain unverified.

**Next step:** obtain current gameplay reference clips or corresponding sequencing code, annotate prop release/contact/return and audio times, then compare with the local movie. The extracted channels are the media source, not a complete choreography specification.

### 5. Facial and secondary sound choreography is partial

Neutral/sad faces, blinks, Laff teeth, and several attack-specific body reactions exist. The source frequently splices reactions; Chomp demonstrates why selecting a single named animation is insufficient. Audio resources resolve, but a successful load does not prove the right overlap, spatial source, or complete sound combination.

**Next step:** review the remaining source reaction slices and secondary cues per attack, with observed playback. Preserve immediate sadness and interruption cleanup when adding subtracks. Chomp's teeth path still needs the complete source trajectory.

### 6. Low-priority resource/test maintenance

- Fifteen basenames occur in multiple extracted phases. Explicit phase paths resolve correctly; basename-only lookup is last-file-wins. No failing mapped path was found, but new mappings should use explicit paths for ambiguous names.
- Loading one bundled GUI model logs a missing legacy `phase_3/maps/toontown-logo.jpg` texture reference. The modern logo file exists under a different name. This is distinct from the manifest/path audit, which checks the actual files and explicit movie mappings; it does not validate every internal BAM texture reference. Current tested panels render. A narrowly scoped resource alias/model remap is preferable to modifying extraction originals.
- Some old standalone checks assumed eager round resolution; `check_lineups.py` was updated to finish the current live event stream. The refreshed tests listed below passed; not every historical script was modernized.
- The project is not a Git repository. This pass saved pre-edit top-level files in `work/full-audit-before`; that is a recovery copy, not version history.

## Verification record

| Area | Result |
|---|---|
| Mechanics regression suite | **113 tests passed**. |
| Extracted files | **12,567 files; 537,933,299 bytes; zero hash/size mismatches** against the extraction manifest. |
| Movie resource mappings | **1,551 unique paths resolved; zero missing mapped paths**. |
| Regular gag playback | **49 gags**, hit/miss paths, transform restoration; all seven persistent Trap→Lure cases passed. |
| Cog attack playback | **135 Cog/attack pairs, 68 distinct attacks, 270 hit/miss cases** passed model/effect/restoration checks. |
| Mixed SOS/regular playback | **11 cases** independently compared live versus headless health/status results, including multiple SOS callers and TNT/Railroad activation. |
| Lineups/forms | All **16** Toon/Cog count combinations and **32** Skelecog profile mappings passed. |
| Window/layout | Seven requested transitions: original, maximized, 5:4, 16:9, ultrawide, small window, restore. Rendered maximized planning view inspected. |
| Controls/lifecycle | New battle interrupt and saved setup; Auto resolve; player Auto; camera controls; target preview/cancel; setup buff reset and panel bounds passed. |
| Rewards/endings | All **13 combat Unite** types; seven Doodle movies and failure; reward-panel navigation; live emergency healing/sadness/v2; parallel remotes; persistent antenna/joke bubble; Cog victory timing passed. |
| Targeted new animation checks | Storm Cloud body variants and mixed hits; Chomp reaction/HP timing/fatal cancellation; Loopy per-Cog contact timing. |
| Syntax | All active top-level Python modules compile. |

Checks use real extracted models and channels. Many movie checks use deterministic time stepping or null audio. They establish playback/cleanup and state consistency; they do **not** establish complete cinematic, audio, or live-server parity.

Raw logs and the resource report are in `reports/project-audit-2026-09-19/`. Additional sampled gag/Cog frames remain in `reports/gag-audit/` and `reports/cog-attack-audit/`; the maximized interface is `reports/window-resize/maximized-planning.png`.

## Evidence links

- Local classic references: `/home/laviscannon/Documents/Codex/2026-09-08/can/work/ref-MovieSquirt.py` (`__doStormCloud`, `__getSuitTrack`), `ref-MovieSuitAttacks.py` (`doChomp`, `getSplicedAnimsTrack`), `ref-MovieTrap.py` (placement routines).
- Bundled channels include `assets/ttr/phase_5/models/char/ttr_a_ene_cga_soak.bam` and corresponding B/C channels; Toon `ttr_a_chr_dgm_torso_spit.bam`, legs `spit`, and `cringe` channels.
- [TTR v4.0.5](https://www.toontownrewritten.com/news/release-notes/367): revised modern attack animation details and later Trap stun corrections.
- [Official v4.0.0 balancing notes](https://cdn.toontownrewritten.com/community/notices/Toontown_Rewritten_Rebalancing_v4.0.0_Patch_Notes.pdf): battle-rule reference, subject to subsequent corrections.
- [TTR's ToonFest article](https://www.toontownrewritten.com/news/item/1021/toonfest-orlando--everything-revealed): Chomp's Toon reaction reuses the Glass of Water animation.
- [TTR v4.0.0](https://www.toontownrewritten.com/news/release-notes/357): Reinforced Plating; retained same-round Skelecog attacks.
- [TTR remote battle guidance](https://www.toontownrewritten.com/taskforce/battles): remote effects, not full body/dialogue sequencing.
