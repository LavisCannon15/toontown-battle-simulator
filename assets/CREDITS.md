# Active game resources

Runtime models, animation clips, textures, fonts, panels, icons and sounds come from the locally installed Toontown Rewritten phase archives, extracted to `assets/ttr` inside the simulator. The original installation is unchanged.

`assets/ttr_resource_manifest.json` records archive provenance and file hashes. `tools/import_installed_ttr.py` repeats the extraction. `tools/render_ttr_icons.py` creates the gag thumbnail cache from those extracted assets. `game_resources.py` resolves renamed modern models and rejects missing resources; it does not fall back to GitHub assets.

The phase files contain assets, not the game client source. Battle rules, UI assembly, choreography, generated text and particle configuration remain simulator code. Modern resource availability does not imply exact reproduction of the live game's behavior.

Historical GitHub artwork provenance is retained in `work/classic-art-provenance.md`; those archived resources are not used by the active resource loader. Game assets retain their original ownership. Panda3D is an independent runtime dependency.
