# Toon expressions alongside Cog attack reactions

## Verified reference behavior
The retained MovieSuitAttacks.getToonTrack selects either getToonTakeDamageTrack or getToonDodgeTrack. Damage reactions play ActorInterval on the Toon, including complete or spliced reaction animations, then return to neutral. For example, Power Tie selects conked; Pound Key selects cringe. This file does not call the ToonHead mouth/eye expression selectors. It therefore does not establish an attack-to-angry/surprised/sad expression table.

ToonHead provides separate neutral, angry, sad, smile, laugh and surprise muzzle meshes and expression controls. Availability of these meshes is not evidence that a specific attack uses them.

## Simulator gaps
- scene_art.configure_head explicitly hides non-neutral eyes and muzzles. There is no expression lifecycle switching those meshes during battle.
- Dog heads are Actors and load the available head animation channels. Other species are loaded as static head models; the torso and legs still animate, but that does not supply an equivalent animated head channel.
- toon_clip plays the available actor parts and resets to idle. Handwritten attack sequences can bypass that helper, so adding expression changes only there would leave inconsistent coverage.
- Becoming sad plays the lose body animation, but static heads remain neutral. This needs a separately verified expression transition and reset on new battle.

## Decision
Do not assign speculative expressions to every hit or dodge. The previous claim that each body reaction necessarily needs a manually selected matching facial expression was too broad. Next verification requires examining the extracted head animation channels and reference expression/state controls, then comparing actual gameplay for non-dog head behavior. No guessed reaction-expression mappings were introduced by this audit.

Reference: work/ref-ToonHead.py (Open Toontown ToonHead), and the retained ref-MovieSuitAttacks.py under the original workspace work directory.
