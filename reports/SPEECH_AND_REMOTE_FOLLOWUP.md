# Speech layout and remote follow-up

Reference inspected: https://github.com/toontownretro/libotp, src/nametag/chatBalloon.cxx, nametag3d.cxx, nametagGlobals.cxx, nametagGroup.I. This repository preserves/reconstructs classic libotp; it is not current official TTR source.

Speech now follows the reference's 10-unit wordwrap, 9-unit internal balloon width, 0.25 minimum horizontal scale, text origin (1,0,2), 0.2 baseline adjustment, row/line-height based middle scaling and top translation. Font comes from Suit.getSuitFont: VT Remington Portable. Distance scaling uses 0.56 * sqrt(distance/50), converted to this scene's .62 world scale. This replaces the previous guessed fixed text size and whole-model stretching. Full native NametagGroup camera-offset, paging, and social features are not ported.

Remote takeover now cues the separately bundled SA_remote_control.ogg at the existing 0.8s seizecontrol onset, independently of AA_remote_control.ogg. Both recordings play fully. This is synchronization with our existing reaction; modern TTR exact offsets remain unverified.

Bad Joke bubble now begins with its speech audio, and the punchline/hit is scheduled at the 2.708s bubble-channel end instead of 6.583s. The timing is inferred from matching 2.708s animation / 2.709s audio durations, not claimed as modern TTR source timing. Cog body remains the bundled native speak channel: replacement body animation is unresolved pending identification/footage. Do not claim the reported body-animation mismatch is fixed.

Checks passed: parallel remote activation and interruption; remote antenna/bubble lifecycle and Lure priority; speech/name replacement; source-layout formulas across camera distances; 93 engine unit tests. Simulator restarted.
