# Toon and Cog name-tag audit

Compared the retained Avatar, Toon, Suit and TTLocalizerEnglish source with our HUD and bundled extracted models/fonts.

## Reference findings

- Toon font: `ImpressBT.ttf`; Cog font: `vtRemingtonPortable.ttf`. Both were already correctly loaded from the bundled TTR resources.
- Cog display text: name, department, `Level N` on three lines (`SuitBaseNameWithLevel`). This was already correct. Skelecogs use the Skelecog name.
- Avatar's base anchor is height + 0.5; Suit uses height + 1.0. Converted to this simulator's 0.62 scene scale.
- Toon supplies the leg `joint_nameTag` to the native name-tag system. The extracted TTR equivalent is `jnt_M_nameTag_01`. Suit.getNametagJoints returns no joints, so Cog tags use a fixed height relative to the moving character root.

## Fixed

- Hard-coded 3.45 Toon / 4.6 Cog heights replaced with cached neutral-model heights. Cache is established before held props and effects, preventing a large attack prop from moving the name tag.
- Toon tag anchor follows the extracted animated leg name-tag joint, relative to its neutral position.
- Cog card widths/heights automatically fit the actual font text; no fixed narrow frame.
- Live names, Cog levels and displayed skeleton form refresh without a HUD rebuild. The visible actor's skeleton flag prevents a label changing ahead of the model transition.
- Projection uses the actual camera display region and scene-graph transforms; no manual division by a guessed uniform UI scale. Out-of-view anchors are hidden.
- Hidden Unite speech nodes no longer suppress names. Visible speech and health popups retain their existing name suppression behavior.
- Name-tag layer sits behind battle controls. Hidden/removed character roots hide their tags.

Implementation: `character_nametags.py`, `scene_art.py`, and `BattleHUD.make_nametags/position_nametags` in `battle_hud.py`.

## Remaining differences

This simulator uses projected DirectGUI labels, not the original compiled NametagGroup/Nametag3d implementation. Exact native distance scaling, off-screen arrows, click/hover name-tag behavior, friend/chat color categories, purchased name-tag styles and integrated speech balloons are not recreated here. Existing text colors are retained, not claimed to be a verified modern TTR palette. The yellow Lured/Trapped/Remote line is a simulator diagnostic, not native Cog display text. Version 2.0 level suffix now follows the retained reference: DistributedSuitBase.setSkeleRevives appends TTLocalizer.SkeleRevivePostFix (` v2.0`) while a revival remains. The suffix is removed when the visible model changes to the Skelecog layer. Name and department remain on their own lines. Verified ordinary, v2.0, pending revival and visible Skelecog labels.

The extracted files supply resources, not modern TTR UI logic. This audit fixes verified differences; it does not claim complete pixel-for-pixel TTR parity.

## Checks

`tests/check_nametags.py` loads real resources and checks auto-sized text frames, dynamic label updates, model-height/joint anchors, hidden speech/characters and projection at three UI scales. A rendered inspection is saved as `work/nametag-audit.png`. Existing 93 unit tests pass.
