# Gag panel and related UI audit

Compared all four supplied actual-game screenshots with newly rendered simulator Gags, SOS, Doodle and Remote pages, the bundled ttr_m_gui_bat_battleMenu model, and selection/targeting code. No layout or gameplay changes were made.

## Highest-priority findings

1. **Briefcase replaces too much of the interface.** rewards_ui.py open_rewards hides self.content and the red base. This removes the right-hand notes, Pass, Run and briefcase together with the gag grid. All supplied references retain that column and the red outer frame while replacing only the left grid. Separate persistent shell, grid and reward-page containers are needed.
2. **Unavailable rewards look callable.** Reward buttons disable only for zero stock. With all Cogs lured, Lil Oldman's button still reports state NORMAL. Engine validation rejects the call afterward, but the panel should communicate unavailability first, as the reference does for Clara and Oldman. Remote target eligibility needs the same validation-aware treatment.
3. **SOS Toon-Up target marks are incorrect.** battle_hud.py target_marks excludes the caller whenever the track is Toon-Up, including SOS. Ordinary Toon-Up excludes its caster; SOS healing includes the caller. Also, Cogs Miss is classified as a Toon-targeting status in target_marks/target_caption, so it uses the wrong team's slots. Unequal Toon/Cog counts expose the latter more clearly.

## Screenshot differences and available resources

| Area | Current simulator | Reference / required work |
|---|---|---|
| Right-side notes | White open pages, default “Choose a gag”; pouch total beneath grid | Yellow idle notes area with blue Shticky Notes control and Total gags counter. Keep this visible on reward pages. No Shticky Notes editing action is implemented. |
| Pass and Run | Run left, Pass right; extra text beneath symbols | Reference has Pass left, Run right, icon-only. These are user-edited positions; preserve until a redesign is authorized. |
| Briefcase state | Closed icon only, hidden while browsing rewards; separate Back/Esc | Reference switches to open briefcase while browsing. Bundled closed/open/partial/locked/empty variants exist. |
| SOS list | Eight fixed cards per page, Previous/Next navigation | Reference has a scrollable collection, visible scrollbar and styled filter. loc_SOSPanelSlider and loc_SOSPanelType exist in the model. |
| SOS cards | All cards use stretched remotePanel button artwork; tiny “Call” text on an entirely clickable card | Reference uses compact white cards with a distinct red CALL control, readable name/effect/count/stars and Unavailable state. Existing classic card assets should be compared before selecting final artwork. |
| Doodle page | Seven generic white cards, no Doodle preview | Reference has a large Doodle on the left and seven colored trick rows on the right. Bundled trickStrip_base/highlight, buttonIndent and all seven trick icons are present. A preview actor and appropriate clipping/cleanup are needed. |
| Remote page | Four cards on top, two below, mixing healing and damage | Reference has three Damage Remotes above three Healing Remotes, compact colored icon buttons, star tiers and stock counts. Both section-title nodes and button up/down/hover/highlight variants are bundled. |
| Reward tabs | Small icons in wide oval tab art with extra labels; no Fire quantity | Reference has a vertical tab rail, larger icons, selected-state backing and Fire count over its icon. |
| Track colors | Lure pink; Throw muted purple/brown edge | Reference Lure is green and Throw orange; the whole strip should retain its track identity. |
| Missing track | Disabled, dark gag icons and counts remain | Reference Toon-Up row is empty when unavailable as a track. Distinguish missing track from owned gags with zero stock. |
| Training display | Track names only | Reference shows per-track “0 to Go!” progress boxes. Real progress data is not yet modeled; do not fabricate it. |
| Portraits | Generic head rendering, broad mesh tint, no matching accessories | Reference portraits include distinctive colors and accessories. For example, the supplied Bessie has a pirate hat. Verify each NPC separately; screenshots show only part of the roster. |
| Typography and proportions | Reward text very small at the tested size; art nodes independently stretched and recentered | Reuse resource layout markers and preserve artwork proportions. art_node/ui_states currently normalize each node independently, losing original relative transforms. Exact screenshot pixels depend on window size and should not be copied blindly. |

## Further interaction findings

- **Stale hover details:** hovering Birthday Cake and leaving retains “Birthday Cake” in the notes. gag_leave only resets the separate tooltip unless a pending gag exists. It should return to the appropriate idle or selected state.
- **Targeting is a simulator-specific flow:** gag/remote targeting uses name buttons above the grid and world picking. Fire opens a separate classic selection panel. The screenshots do not show target-selection states, so exact TTR targeting transitions cannot be certified from them.
- **Auto resolve and open menus:** resolve_if_ready deliberately waits while any modal is open, but timed expiry can resolve through reward menus. This is an implementation policy requiring explicit testing/design; the still screenshots do not establish the game's timing behavior.
- **Reward reopen state:** briefcase always opens SOS page 0 rather than retaining the prior category/filter/scroll position. Reference behavior for reopening needs observation.
- **Team selections:** ordinary gags use their artwork, but SOS/Doodle/Remote selections use text placeholders. Their target semantics and hover details need a dedicated pass alongside the reward pages.
- **Disabled state rendering:** ui_states supplies the up artwork as its fourth state, with whole-button tint used for disabling. Dedicated disabled styling and readable counts should be checked against the reference.

## Working behavior verified

- Captured all four simulator pages successfully.
- SOS displays eight cards per page; all six Remote choices and seven Doodle tricks are present, despite incorrect presentation.
- Closing the reward overlay restores the gag content.
- Cancelling a pending Birthday Cake target preserves an already confirmed Cupcake choice.
- No inventory is consumed merely by opening these pages; consumption remains in battle resolution.
- Engine-side validation prevents the unavailable Lure SOS from actually being committed, despite the misleading enabled button.

## Recommended implementation order

1. Correct shared shell structure and reward availability/target marks.
2. Build distinct SOS scrolling, Doodle preview/trick rows and Remote two-row pages from bundled nodes.
3. Implement notes idle/hover behavior, open briefcase state, tab quantities and visual states.
4. Restore track colors/missing-track styling, improve portraits and verify proportions at multiple window sizes.
5. Check every transition: opening, switching tabs, cancelling, selecting targets, timeout, auto selection, zero stock, lured Cogs, unequal lineups and battle ending.

Evidence: reports/panel-audit contains gags.png, SOS-cards.png, Doodle.png, Remotes.png, behavior.json and resource-nodes.txt. Reproduction: work/audit_panel.py. The four user screenshots establish visible states; they do not establish unseen animations or interaction rules. This audit did not change manually positioned controls or resolve the separate battle-mechanics findings.
