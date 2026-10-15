# Gag panel changes applied

The red outer frame, yellow native Shticky Notes cover, gag total, Pass, Run and briefcase now form a persistent shell. Opening the briefcase replaces only the gag grid. Pass is left of Run, with icon-only controls, and the briefcase switches between native open/closed artwork.

SOS uses a scrollable collection with a filter, native card fronts and inventory-button CALL controls, counts, stars and validation-aware Unavailable states. Scroll positions are remembered by filter within the session. Remote controls use two rows of three, native Damage/Healing headings, native button states, tier stars and stock counts. The Doodle page has a live preview of the simulator's Doodle and seven native colored trick strips.

Corrected Lure strip color, missing-track blank rows, stale hover details, SOS Toon-Up caller target marks and Cog Accuracy Down target-team marks. Pass/Run work from reward pages. Doodle preview actors are cleaned up when switching, closing or starting a new battle. The notes control opens editable local session notes; that editor is a simulator feature, not a claim to reproduce TTR's complete Shticky Notes system.

## Verification

- 91 unit tests passed.
- New panel integration check passed: 32 SOS choices, six Remote choices, seven tricks, availability, shell visibility, Pass/Run, cleanup, target marks, notes and hover reset.
- Resize integration passed at original, maximized, 5:4, 16:9, ultrawide, small-window and restored sizes. The test exposed and led to a fix for stale hover callbacks during HUD reconstruction.
- Rendered and inspected all four principal panel pages. Screenshots are in reports/panel-audit.

## Remaining fidelity limits

The simulator still does not model gag XP/progression, so training counters were not fabricated. NPC portrait accessories and exact per-NPC proportions are not fully reproduced. Fire retains its resource-backed classic target-selection page; screenshots supplied did not establish the modern Fire targeting state. The filter and scrollbar use Panda controls styled for this panel, rather than a complete port of TTR client UI code. Local notes are session-only. The unused logo on the original playing-card model refers to a texture absent from the extracted archive; only the intact front geometry is displayed.

These changes address the gag-panel audit. The separate mixed-healing, v2.0 same-track damage, SOS Trap activation and Synergy mechanics/movie findings in GENERAL_BATTLE_AUDIT.md remain outstanding.
