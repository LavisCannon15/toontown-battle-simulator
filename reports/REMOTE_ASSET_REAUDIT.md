# Remote presentation audit

Compared the simulator with the bundled TTR models, animation channels and decoded audio durations. The retained classic Toontown reference predates TTR remotes; it cannot establish their modern choreography. Resource durations verify native playback, not exact battle cue offsets.

## Corrections applied

- Toon remoteAttack and remote prop: both 5.708 seconds, previously compressed to 2.4. Both now use native duration.
- Healing Cog song-and-dance: 5.833 seconds, previously compressed to 3. Now native speed.
- AA_remote_control: 4.909 seconds, previously stopped at the 3.25-second Cog seize-control duration. Now complete.
- SA_song_and_dance: 5.508 seconds, previously stopped at 3. Now complete.

## Present and checked

- Bundled animated handheld remote and matching Toon channels.
- Cog seizecontrol (3.25s), controlidle (3.333s), speak (7.083s).
- Head-attached antenna, persistent while lured; removed on expiry or actor replacement.
- Antenna open (1.042s); antenna speak is a one-frame pose, not a full speech animation.
- Animated joke bubble: speak 2.708s, matching 2.709s speak sound; separate badJoke recording 4.241s.
- Concurrent activation on distinct Cogs; safe New Battle cancellation.

## Remaining discrepancies / unverified details

- SA_remote_control (3.744s) is bundled and registered but not cued. Its exact role/onset needs modern sequencing evidence.
- Joke bubble currently starts at 0.35s, while its speak audio starts immediately. This offset is not justified by reference code.
- Joke impact at Cog speak duration minus 0.5s and healing at 1.6s are simulator timing assumptions.
- Real joke text and recipient response dialogue are missing. TTR explicitly mentions added response lines: https://www.toontownrewritten.com/news/release-notes/314
- Remote healing/damage prop textures, hand attachment offsets, antenna scale/anchor and the static antenna variant need visual comparison with modern TTR footage. Existing assets alone do not verify placement.
- This is not certification of exact TTR choreography. No unsupported replacement animations or guessed cue offsets were introduced.

Validation: decoded real asset durations in work/remote-assets-audit.json; parallel activation and remote presentation regressions.
