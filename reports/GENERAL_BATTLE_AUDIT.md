# General battle audit — September 12, 2026

Audit only: no gameplay code, panel layout or running-app state changed. Reproduction scripts are in work/general-audit; results are in reports/general-audit. This is a targeted ordinary-battle audit, not a claim of exhaustive visual or current-server equivalence.

## Confirmed findings, in recommended repair order

### 1. High: SOS healing disappears with two ordinary Toon-Up actions

Reproduction: start four Toons at 1 Laff, force successful gag rolls, disable enemy attacks, choose Madam Chuckle plus two Feathers targeting Toon 0, with the fourth Toon passing. The synchronous engine ends at [36,16,16,16]; live playback ends at [21,1,1,1]. All 60 points of SOS healing disappear.

Cause: battle_engine.py:356 attributes only ordinary healing to health_by_action. battle_movies.py:312 switches to those per-action lists when two ordinary healers perform, omitting the SOS health entries. sos_movies.py:78 supplies a separate health timeline only when there are no ordinary actions.

Repair: give SOS and ordinary healing separate, explicit impact ownership, preserving every health event exactly once. Add mixed healing tests, including multiple SOS and near-full recipients. The previous isolated-card success did not cover this combination.

### 2. High: mixed SOS/ordinary same-track attacks damage both v2.0 layers

Reproduction: one v2.0 Mr. Hollywood with 1 HP remaining in the suit layer, Barbara Seville and a Foghorn in the same round. The SOS destroys the suit, then the Foghorn reduces the new Skelecog from 90 to 40 HP in the same Sound track.

Cause: battle_engine.py:328 resolves SOS effects before ordinary track buckets, and damage() immediately restores the second layer at line 473. Later attacks in the same track can damage that new layer.

TTR's published rule says excess same-track damage is nullified and the Skelecog respawns at full health. This case exposes the already documented incomplete mixed SOS/ordinary resolution, now with a concrete layer-transition consequence.

Repair: resolve shared track/layer eligibility as one operation, alongside mixed SOS combo accounting. Avoid simply blocking later tracks, which must remain able to attack the new layer.

### 3. Medium: SOS Lure bypasses the placed-Trap activation movie

Reproduction: place TNT on Cogs, then call Nancy Gas with the other Toons passing. The captured live interval contains the NPC's Hypno-goggles performance and health callbacks at 1.6 seconds, but no Trap walk-in/flail/dynamite activation sequence. Defeated Cogs still play their ordinary defeat sequence afterward.

Cause: base_gag_movie builds the Trap activation wrapper, but sos_movies.py:78–79 replaces that entire base movie with a health-only interval for SOS-only tracks. Thus the fix for SOS-only healing also discards non-health choreography.

Repair: replace only the health component, retaining Trap/Railroad activation choreography and coordinating its impact with the NPC. Check each trap with both ordinary and SOS Lure.

### 4. Medium: Synergy's jump dodge samples the wrong frames

battle_movies.py:333 uses native start/end times together with a changed play rate. Inspection of the actual Panda intervals shows the first segment reaches frame 14.4, the slowed segment jumps backward to frames 3.43–5.21, then the final segment jumps to frame 21.84. The intended slowed middle lasts about 0.485 seconds, not 1.3 seconds.

Repair: use explicit source frame boundaries and account for Panda's inclusive frame timing, as already done for Lowden's reverse landing animation. Verify intermediate frames, not merely successful completion.

### 5. Medium: Lil Oldman suppresses six enemy turns

support.py configures Lure SOS values as [4,5,6]. A direct engine reproduction gives Lil Oldman six actual skipped Cog phases, not merely a display counter with a harmless offset. TTR's published rebalance specifies five for the five-star Lure SOS.

Repair: align the configured duration and descriptions with the supported rule, with tests that count real skipped enemy turns. Independently check the lower tiers before changing them.

### 6. Low: locked gag levels are not enforced by action/inventory validation

Set a Toon's Throw track level to 1 while retaining its existing inventory. Both check_inventory() and validate(Birthday Cake) accept the level-6 gag. Restock now respects unlock levels, but these paths do not.

This is currently an engine/configuration consistency gap; the current Setup screen does not expose per-track training levels. It should be fixed before exposing that configuration more broadly. Automatic partners also rely on validate(), so they inherit this gap if such a loadout is supplied.

## Verification and test-quality findings

- All 91 unit tests passed.
- Seven existing integration scripts passed: new-battle interruption, automatic resolution, Cog victory timing, parallel remotes, Unites, live rounds and reward endings.
- The existing formations script failed at its initial assertion demanding the old FIRE/SOS/PASS/RUN shortcut collection. A separate audit copy bypassing only that obsolete assertion passed all remaining checks, including all 15 surviving-slot formations and Fire target filtering. This is an outdated test expectation, not evidence of broken formation movement.
- New probes reproduced mixed-heal HP divergence, same-track layer damage, six Lil Oldman skips, locked-gag acceptance and Synergy frame discontinuities. The SOS-Trap finding is established by the constructed live interval and code path.
- Offscreen checks used muted audio and programmatic interval advancement. They do not establish sound synchronization, every intermediate visual frame, every NPC costume, or all 68 Cog attack presentations.

## Still-open fidelity limits

The exact current accuracy soft cap remains intentionally unimplemented under the user's verified-rules preference. Current Cog probabilities, remote replacement/priority, full pet fatigue, modern per-card NPC choreography and precise Unite radius remain separate research gaps. The extracted phase archives contain assets, not the current battle-server source. Existing MECHANICS.md also mixes historical UI descriptions with current ones; it should be consolidated so old descriptions are not mistaken for current behavior.

## Sources and evidence

- Official TTR rebalance: https://www.toontownrewritten.com/news/release-notes/284 — five-star SOS Lure duration, same-track v2.0 damage nullification and other baseline rules. Checked during this audit; this is historical official evidence, not access to current server code.
- Bundled animation channels and installed Panda3D ActorInterval behavior were inspected locally.
- reports/general-audit/reproductions.json and engine_edges.json contain concrete results; checks.json and individual logs contain existing-check outcomes.
