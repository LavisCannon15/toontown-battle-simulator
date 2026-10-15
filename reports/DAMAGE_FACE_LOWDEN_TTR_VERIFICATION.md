# Damage, expressions, Lowden and TTR verification — 2026-09-13

## Applied fixes

- The engine now records each Toon's base damage per target. Throw and Squirt playback displays and applies that damage at each actual contact, including mixed gags and group targets. Orange knockback follows the final hit by 0.75s; yellow combo follows the previous bonus by 0.75s. Health deductions are capped to the authoritative engine total, avoiding duplicated damage on overkill. Earlier saved events without per-action attribution retain the old compatible aggregate path. Existing final-contact reaction choreography is retained; this is not a rewrite of every hit reaction.
- Lowden's flight movement still lasts four seconds. His extracted propeller sounds now play their complete files instead of being stopped at four seconds; the departure interval includes the remaining audio tail after he has flown offscreen.
- Lowden's SOS card uses the same short red dog head resource as his battle appearance. Skin-only coloring preserves the muzzle, nose and ears. Portrait depth testing now prevents rear mouth polygons appearing through the face, and portraits select the high-detail meshes rather than overlapping detail variants. No button positions or scales were changed.
- Toons now blink using their extracted neutral/sad eye meshes. Blink closure lasts 0.125s; idle spacing follows the retained ToonHead random timing and uses an independent random generator so battle rolls are unaffected. At zero health, the defeat path selects sad eyes and the available sad muzzle; New Battle creates neutral faces. All eight supported species were checked. No speculative hit-to-angry/surprised expression table was introduced. Non-dog head motion remains supplied by body attachment plus these mesh expressions, rather than invented animation channels.

## Checks

- 106 unit tests passed, including separate contact/bonus times, overkill accounting and compatibility fallback.
- Real multi-hit Throw event maintained display/engine HP parity.
- Mixed Seltzer Bottle/Fire Hose, Storm Cloud/Geyser, and Whole Cream Pie/Wedding Cake events maintained HP parity for every target.
- Eight species' sad and neutral eye meshes selected correctly; Lowden portrait loaded and was visually inspected after the depth correction.
- All 135 Cog/attack pairs (68 distinct attacks) completed hit and miss playback with transform/idle restoration: 270 cases. This establishes runtime coverage, not exact TTR choreography.
- Diagnostics: `work/presentation-fixes.log`, `work/damage-variants.log`, `work/cog-current-verification.log`; screenshot `reports/lowden-portrait-fixed.png` includes an enlarged diagnostic portrait for inspection, not a new live HUD element.

## What the current TTR comparison establishes

[Official v4.0.5 notes](https://www.toontownrewritten.com/news/release-notes/367) explicitly say animations for almost all new standard attacks introduced in v4.0.0 were polished. Therefore the older reference and matching extracted model names cannot certify their modern paths or audio onsets.

[Official ToonFest discussion](https://www.toontownrewritten.com/news/item/1021/toonfest-orlando--everything-revealed) specifically states that Loan Shark's Chomp reaction reuses parts of the Glass of Water animation. The retained `doChomp` indeed splices `cringe` and `spit` segments. Our generic Chomp path still has only `cringe`: **a confirmed remaining reaction mismatch**, not a verified TTR match. Its teeth trajectory also remains generic compared with the multi-stage classic path. This verification pass records it rather than presenting the entire Cog catalog as correct.

[Official v4.0.0 notes](https://www.toontownrewritten.com/news/release-notes/357) confirm the same-round newly revealed v2.0 Skelecog attack rule; the simulator retains the user's chosen TTR behavior.

[Official remote description](https://www.toontownrewritten.com/taskforce/battles) confirms joke damage and dance healing, but does not identify the exact Bad Joke body animation channel or frame range. That body choice remains unverified.

[Official Lowden spotlight](https://www.toontownrewritten.com/news/item/299/the-silly-spotlight-lord-lowden-clear) provides character context; the portrait now shares the bundled head and coloring already used for his in-battle model.

**Conclusion:** runtime playback is checked across the catalog, but not every attack is confirmed visually against current TTR. Chomp has a concrete remaining mismatch; exact timing for reconstructed newer attacks and Bad Joke requires modern footage or sequencing code. Extracted phase media do not include that sequencing code.
