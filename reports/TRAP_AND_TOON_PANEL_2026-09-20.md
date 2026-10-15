# Toon choice panels and Trap/Lure audit — September 20, 2026

## Changes

- Replaced the classic `ToonBtl_Status_BG` with the bundled TTR `ttr_m_gui_bat_toonGUI.bam`. Face, Laff count, gag icon and target marks use the model's four locator positions. Confirmed choices use TTR's gag-circle color/alpha textures. The question mark is already in the base texture; an additional text question mark would duplicate it.
- Added **Next Toon: ON/OFF**, enabled initially, below Timed/Untimed. Successful confirmation advances cyclically to the next living Manual Toon without a confirmed choice. Choosing a gag that still needs a target, cancelling, invalid actions, and completing the last choice do not advance. Auto gag selection and Auto resolve remain separate options. New battle preserves the toggle within the running session.
- Replaced generic pie placement sounds for Banana Peel, Rake and Marbles with their respective bundled `TL_banana`, `TL_rake_throw_only` and `TL_marbles` sounds. Restored the button/pause/appearance sequence for Quicksand and Trapdoor and their second body-fall activation sound. Preserved the dedicated TNT and Railroad sound sequences.
- Thrown traps now land on the ground rather than using the generic projectile's chest-height destination. Banana slides and Marbles roll to their resting positions; placed holes grow into view. Each placement reveals only its own target's trap.
- Resting positions use MovieUtil's per-gag distances and Rake's Cog-specific offset, converted by the Suit scale. TNT's thrown endpoint and persistent placement share the same position function.
- Use the extracted resting `rake-step` model/channel. Its bind pose is flat in TTR: copying the classic 270-degree pitch put this mesh underground. Banana and Marbles now use their final resting frames rather than a common frame 74.
- Ordinary Trap activation supplies a forward destination to the Lure movie. The extra forward `walk` is gone; the Cog approaches during the native Lure reaction. Trap contact follows the Cog reaction's finish rather than the longest Toon/prop cleanup interval. Surviving Cogs return using a backwards recovery walk.

## Evidence and limits

Runtime assets are entirely inside `assets/ttr`. Choreography was compared with retained `ref-MovieTrap.py`, `ref-MovieLure.py`, and `ref-MovieUtil.py` in the original workspace's `work` directory. Those are classic source references, **not current TTR Python code**. Extracted phases provide artwork, model/channel data and sounds, not the complete current TTR battle implementation. Distances are adapted to the simulator's compact battlefield.

This pass fixes the reported panel/placement/audio/double-approach defects; it does not certify every Trap animation as an exact modern TTR match. Collision dust, full Banana/Marbles reaction shrink/slide, and complete Quicksand/Trapdoor reaction splicing remain fidelity work. Reward choices still use text for SOS/Doodle/Remote in the choice circle. User-adjusted gag-panel button positions/scales were preserved.

## Validation

- 113 mechanics tests passed.
- New real-resource integration check: TTR panel selection; advancing, skipping automatic/escaped/already-selected Toons; toggle off; cancellation; six ordinary Trap placement sounds/positions; 24 combinations with dollar, magnet, goggles and Presentation Lure, verifying forward movement, one damage application, return position and cleanup.
- Existing target-preview and auto-resolve checks passed; the target-preview scenario now explicitly reselects the original Toon after automatic advance.
- New battle interruption check passed.
- All 49 gag hit/miss playback checks and seven persistent Trap/Lure live rounds passed.
- Rendered and inspected updated choice panels and simultaneous Banana/Rake/Marbles/TNT placement. Final targeted test rerun covers the resting-frame/orientation correction.

Backups and test logs: `work/trap-panel-2026-09-20/`. Existing nonfatal missing `toontown-logo.jpg` load warning remains unrelated to these controls and traps.
