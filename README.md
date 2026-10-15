# Toon Battle Lab — Panda3D

A local battle simulator built with Python and Panda3D. This repository contains the simulator source; extracted game media and generated icons are not included. Once supplied locally under `assets`, no running TTR client or external asset folder is required. This is an independent practice project, not the TTR client or an exact reconstruction of its server.

Current review: [Project audit, September 19](reports/PROJECT_AUDIT_2026-09-19.md). Rules and known limits: [MECHANICS.md](MECHANICS.md). Earlier reports describe historical versions and may have been superseded.

## Set up a checkout

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Copy `assets/ttr/`, `assets/particle_effects/`, and the generated `assets/*.png` icons from your existing local simulator into the same locations in this checkout. Keep these resources local: the ignore rules exclude extracted media and generated images from Git. Game resources retain their original ownership; this repository does not grant rights to redistribute them.

The existing Desktop installation remains self-contained and is not changed by this source snapshot. The extraction helper currently contains the original machine's TTR installation path; adjust it for your installation before using it. Rebuilding gag icons is available through `tools/render_ttr_icons.py` after assets are present.

## Play

Double-click **Play Toon Battle** on the Desktop, or run `./launch.sh`. The launcher uses the project's local Python environment. `./launch.sh --untimed` starts without a countdown; `--seed 42` supplies a repeatable battle seed.

- Select a Toon through its green status card, its character, or keys **1–4**. Choose a gag, then a target if needed. **Back** or **Escape** cancels target selection while preserving an already confirmed action.
- The gag panel uses the extracted TTR inventory artwork, notes, Pass/Run controls, and briefcase. Open the **briefcase** for SOS cards, Fires, Remotes, or Doodle tricks. Closing it returns to gag selection. Target markers use **X** in the simulator's left-to-right formation order.
- **Next Toon: ON/OFF** switches to the next living, unselected Manual Toon after confirming a choice. Cancelling target selection does not advance. This toggle is independent of automatic gag choices and Auto resolve.
- **Resolve round** or **Enter** starts the selected plan; unselected Manual Toons pass. **Auto resolve: ON/OFF** controls whether a complete team plan starts automatically.
- Each Toon, including your own, has a **Manual / Auto** switch. Auto chooses legal regular gags independently, without inspecting other pending choices. It does not spend rewards or level 7 gags.
- **Timed / Untimed** controls the 30-second selection clock. Setup and playback pause it. Reward menus do not.
- **SpeedChat / Unites** or **U** opens a separate menu. A Unite does not replace a gag choice or consume a round. During playback, any living Toon can be its caster.
- **Run** removes that Toon using its teleport movie without spending a round. The Cogs win once no living, participating Toons remain.
- **New battle** interrupts playback and restores the last successfully applied setup, including the chosen lineup and starting supplies. It does not restore the original default lineup unless that is the saved setup.
- **Setup** supports 1–4 Toons and 1–4 Cogs, all 32 standard Cog profiles, Regular/Skelecog/v2.0 forms, Toon appearance and Laff, gag pouches, reward supplies, and Doodle training. **Start this battle** applies edits; closing cancels them.
- **Battle log** opens a scrollable popup. **Sound on / Muted** controls the game-resource audio.

## Camera

Over the battlefield, right-drag to rotate, middle-drag to pan, and use the wheel to zoom. **Home** resets the view. Scrolling an open SOS list or the log scrolls that panel instead.

## Resources and animation

Models, animation channels, textures, fonts, icons, and sounds load from the bundled extracted TTR files. The manifest records their source archives and hashes. The original installation is not modified. Public classic Toontown code is used as a reference; downloaded reference modules are not imported by the simulator.

The extracted phase archives contain media, not current TTR Python battle logic. Playback combines those assets with locally implemented choreography. Not every prop path, camera movement, reaction, or sound overlap is an exact match. The current audit lists the confirmed gaps instead of claiming complete fidelity.

The battle engine is separate from presentation. Live playback advances between events so emergency Unites and immediate sadness affect subsequent attacks. Throw/Squirt damage popups distinguish base, Lure knockback, and combo damage. Some other tracks still aggregate their damage display.

## Development and checks

The application requires Python 3.12 and the pinned dependency in `requirements.txt`. On another computer, recreate `.venv` and install that file; the supplied virtual environment is specific to this machine. A working OpenGL driver is required.

```bash
.venv/bin/python -m unittest discover -s tests -q
.venv/bin/python tests/check_event_health.py
.venv/bin/python tests/check_all_gag_sequences.py
.venv/bin/python tests/check_cog_attack_audit.py
.venv/bin/python tests/check_lineups.py
```

The Panda checks load actual assets and exercise playback. Passing them establishes resource and regression coverage, not equivalence with the live TTR game. Their output must include the final success message; inspect logs for tracebacks.

Main entry points:

- `panda_battle.py`: application, setup, input, timer, and round orchestration.
- `battle_engine.py`, `support.py`, `combat_rules.py`: mechanics and reward calculations.
- `battle_hud.py`, `target_panel.py`, `rewards_ui.py`, `setup_screen.py`: interface.
- `battle_movies.py`, individual movie modules: playback and impact-time health.
- `scene_art.py`, `toon_expression.py`, `character_nametags.py`: character appearance and presentation.
- `game_resources.py`, `assets/ttr_resource_manifest.json`: bundled resource lookup and provenance.

Read `assets/CREDITS.md` before sharing the game artwork. This project is unaffiliated with Disney and Toontown Rewritten. The old Tkinter application is archived under `work/legacy-tkinter` and is not the active interface.
