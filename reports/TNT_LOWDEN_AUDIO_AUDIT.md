# TNT, Lowden and animation/audio audit — 2026-09-13

## Evidence and limits

Runtime models and sounds remain inside `assets/ttr`. SHA-256 checks matched the extraction manifest for all nine assets inspected: TNT model/channel/audio, kapow model/channel, Cog death/breakup audio, Bugle audio and the chatbox model. All 46 literal `sound_clip` calls resolve to registered, bundled assets; dynamically chosen audio is outside that static count.

Sequencing references are the retained classic MovieTrap, MovieLure, MovieSound and MovieUtil code. These establish classic timing, not the unpublished current TTR client timeline. Current TTR assets supply the media, not Python battle logic. Diagnostic sound objects record scheduled play/stop/seek calls; null-audio scene tests cannot certify perceived synchronization through the user's speakers.

## Applied corrections

### TNT

Placement incorrectly used `AA_pie_throw_only.ogg` and a generic projectile into the Cog's upper body. It now follows the medium-Toon reference: native toss, release at 2.5 seconds (2.3 + 0.2), 0.9-second parabolic flight to the trap slot, and `TL_dynamite.ogg` starting at 3.3 seconds for 0.7 seconds. World distances and final model scale fit this simulator; this is not a claim of exact TTR positioning.

Idle TNT was posed at the last frame of its channel. It now remains at frame zero until activated.

Activation previously played the complete 4.445-second dynamite file starting 0.5 seconds late, with a generic four-second flail and generic explosion. The reference instead plays:

| Activation time | Cue |
| --- | --- |
| 0.0–2.0 | `TL_dynamite.ogg` |
| 2.0–2.6 | `ENC_cogfall_apart.ogg` |
| 2.3 | Damage and native animated kapow |

TNT now plays its prop channel and the reference's forward/reverse flail, brief idle, slip-forward recoil and temporary darkening. Color restores on completion and New Battle. The reference's persistent fuse-spark particle effect is still absent; it was not replaced with unrelated particles.

### Lord Lowden Clear

Lowden's special path bypassed ordinary SOS speech entirely. It now creates a resource chatbox after landing, hides his name during the greeting, then restores the name. The anchor is measured from his head instead of using a fixed height above it. The caller's name is inserted in the greeting.

The arrival greeting is transcribed from the user's [Lowden demonstration](https://www.youtube.com/watch?v=oQSXv7RyrH8), around 10 seconds. The on-screen name is personalized; punctuation and the 3.4-second display duration are adaptations, not extracted TTR code. No unverified departure quote was added. Four-second arrival/departure movement, cannon orientation, and Cog facing are retained. His departure propeller sound remains capped to the user-requested four-second flight, so this does not certify the full flight-audio envelope.

### Sound gags

MovieSound.__doBugle plays `AA_sound_bugle.ogg` at 1.7 seconds alongside instrument growth. The simulator used 2.45 seconds and also played `m_match_trumpet.ogg`, which the reference loads but does not actually play. Corrected the cue and growth/shrink sequence, and removed that extra sound. Whistle, Aoogah and Elephant Trunk appearance cues changed from 1.15 to 1.05 seconds. Their main sound remains at 2.45 seconds. Existing Sound group ordering and the additional lured-Cog step-back delay remain intact; exact modern TTR differences are still unverified.

### Cog defeat

MovieUtil.createSuitDeathTrack plays two different excerpts of the spinning sound, followed by full breakup audio. Added audio seek-offset/volume support and corrected the sequence:

| Start | File | Source offset | Duration | Volume |
| --- | --- | --- | --- | --- |
| 0.8 | `Cog_Death.ogg` | 1.5 | 1.2 | 0.2 |
| 2.0 | `Cog_Death.ogg` | 0.6 | 3.0 | 0.8 |
| 5.0 | `ENC_cogfall_apart.ogg` | 0 | Full clip (~1.855) | 0.32 |

Previously the simulator played one uninterrupted spinning clip, then started breakup at 5.2 and cut it after 1.2 seconds.

## Validation

- 103 unit tests, including audio seek-before-play, excerpt duration and muted-cue regressions.
- 49 gag hit/miss playback cases plus seven live Trap/Lure sequences.
- Recorded TNT placement and activation play/stop times to 0.01 seconds; verified portal/prop cleanup and color restoration.
- Lowden greeting visibility, measured anchor, name replacement/restoration and New Battle interruption.
- Recorded Whistle/Aoogah/Elephant/Bugle cues and all Cog death seek offsets, volumes and stop times.
- Native TNT reactions verified on A/B/C body families, both suited and Skelecog models.
- Full live TNT → Hypno-goggles activation and four-Cog Lowden dismissal complete with cleanup and display/engine HP parity. Diagnostics are recorded under `work/tnt-lowden-audit/`.

## Further audit findings

1. **Other thrown Trap gags remain simplified.** Banana Peel, Rake and Marbles still use the generic projectile and pie-throw placement sound; their source has individual paths, sounds and timings. Fixing just sound onset without corresponding motion would leave them inconsistent.
2. **Ordinary Trap activation has an extra generic approach.** The wrapper completes Lure's performance before a 0.7-second walk into the trap. Integrating the trigger with each Lure's own approach remains separate work. TNT's activation timeline is now consistent once that approach ends.
3. **Hit damage is still aggregated.** Throw/Squirt base, knockback and combo numbers have separate colors, but individual Toons' base damage remains grouped at the last contact.
4. **Non-dog head expressions remain static.** The current attack-expression audit records this; no guessed attack-to-expression table was added.
5. **Some TTR-specific Cog attacks remain reconstructed.** Embezzle has the correctly named extracted sound, but its exact modern onset is not established by the classic source. Asset filenames alone cannot verify choreography.

Source files: original workspace `work/ref-MovieTrap.py`, `ref-MovieLure.py`, `ref-MovieSound.py`, `ref-MovieUtil.py`; corresponding [Open Toontown battle source](https://github.com/open-toontown/open-toontown/tree/develop/toontown/battle).
