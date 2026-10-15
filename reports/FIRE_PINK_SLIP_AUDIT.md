# Fire and pink-slip presentation audit

Scope: ordinary Fire, shared cannon sequence used by Lowden, and Lowden's pink-slip throw. No gameplay/presentation code changed by this audit.

References:
- https://github.com/open-toontown/open-toontown/blob/develop/toontown/battle/MovieFire.py
- Local reference copy: work/ref-MovieFire.py
- https://www.youtube.com/shorts/oQSXv7RyrH8 (TTR Lowden demonstration supplied by user)
- Bundled assets under assets/ttr.

Classic MovieFire is evidence for classic choreography, not proof that every timing is identical in current TTR. The supplied Lowden video confirms group cannons and the animated burst, but does not demonstrate ordinary player Fire.

## Confirmed differences

| Area | Simulator | Classic reference / evidence |
| --- | --- | --- |
| Ordinary caller | Pushbutton compressed to 2.4 seconds; immediately returns idle | Native pushbutton, two-second wave, duck, then neutral |
| Caller facing | No target-facing wrapper in fire_movie | Turns toward chosen Cog and restores heading afterward |
| Button | Constant-sized hand prop | Grows over one second, holds 2.5 seconds, shrinks over one second |
| Trigger sound | Starts immediately | Starts at 2.15 seconds |
| Cannon barrel | Uniform original proportions | Barrel widens X/Z by 1.6; attachment inversely compensates |
| Cog sinking | Fixed depth 2.5; missing initial short movement | Initial quarter-second descent to -1, then depth 2.5 + level * 0.2 |
| Cog flailing | Forced two-second clip followed by idle restoration | Native flail; no generic idle restoration in the loading track |
| Blast | Static explosion.bam image | Animated kapow plus test_clouds that expands and fades; the TTR clip visibly contains the burst |
| Cannon motion | Rises and tilts, then disappears | Tilts back upright and sinks after firing |
| Launch | Two-second flight/shrink | Three-second flight/shrink |
| HP feedback | At projectile launch | At start of cannon response |
| Stun effect | Omitted | createSuitStunInterval on single-hit Fire |
| Cameras | Fixed simulator view | Dedicated Fire camera selection |

## Lowden-specific findings

Correct resources are selected: pink-slip.bam, throw-object (the Red Tape body animation), Cashbot disguise, head-mounted animated propeller, landing animation and flight sounds. Caller phone/button animation is suppressed. Group cannons are scheduled in parallel after the slip's travel.

The slip's pose, 0.9 scale, and release timing currently borrow Red Tape settings. Those are an adaptation, not verified Lowden-specific transforms. The card travels in a straight line toward the average Cog position and disappears without a separate impact effect. Video matching is still needed for the precise throw arc, card orientation, hand scale, greeting/departure pauses and timing. The shared cannon shortcomings above also affect Lowden.

## Resource availability

The required cannon, pink slip, kapow-mod/kapow-chan, test_clouds, cannon adjust/fire, Cog panic and whistle assets are already bundled. Missing effects here are implementation gaps, not missing downloads.

## Verification and limits

work/check_fire_audit.py exercises four default Cogs (levels 8–11, covering A/B/C bodies), verifies end-of-flight HP, restoration of actor parent/scale/heading, and removal of cannon nodes. Captured and inspected reports/fire-audit.png. Tests establish completion/cleanup, not exact visual fidelity. Audio runs used the null backend; audible mixing was not verified. Special bodies, Skelecogs, duplicate-target Fires and interrupted playback were not exercised in this focused audit.

Recommended order: restore shared cannon effects/proportions/loading and return motion; then ordinary caller choreography; then match Lowden-specific card staging against the provided video. Preserve the established simulator launch direction when porting reference transforms.

## Applied implementation

Shared presentation now lives in fire_movie.py. Added native flail, level-dependent sinking (including the initial quarter-second dip), widened barrel with compensated Cog attachment, animated kapow, expanding/fading test_clouds, three-second flight/shrink, and upright/sinking cannon return. HP feedback is applied at cannon response start. Ordinary Fire now faces its target, plays native pushbutton then wave/duck, scales the button in/out, delays the trigger cue to 2.15 seconds, and includes the bundled stun stars. Lowden bypasses the caller sequence and retains simultaneous cannon responses after his slip throw.

Four ordinary Fire completion/cleanup cases and the Lowden group sequence passed. The refreshed screenshot was visually inspected. Exact Lowden-specific card arc/scale/timing and dedicated cinematic camera matching remain unverified; the existing fixed camera is retained. Audio cue scheduling is implemented but playback was tested with audio disabled.
