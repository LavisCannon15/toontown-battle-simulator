# Tutorial environment

Replaced the generated plaza with the bundled TTR tutorial street, using phase_3.5/dna/tutorial_street.xml and storage_tutorial.xml. The loader resolves the extracted street modules, texture assignments, colored facades, windows, cornices, landmarks, trees, fences, lamps, tunnel and signs. No external asset folder is required.

The XML battle cell (75, 20, -0.5) is transformed to the simulator's origin with a 0.6 scene scale and 90-degree heading. Existing battle coordinates, gag placement and animations remain in their own coordinate system. The default/reset camera now looks down the clear center of the street toward Toon Headquarters. Orbit and zoom remain available.

This is a lightweight renderer for this extracted layout, not the full TTR DNA/game client. Facade window spacing and sign text layout are approximated. Ambient animated props are displayed in their model pose; tutorial NPCs, quests, doors, navigation and tutorial gameplay are not introduced. Scenery collisions are removed so they do not intercept battle targeting. Arbitrary free-camera positions can still pass through or behind scenery.

Validation: offscreen scene render inspected; map survives New battle and camera reset; mechanics unit suite run. Screenshots and logs are in work/tutorial-map.
