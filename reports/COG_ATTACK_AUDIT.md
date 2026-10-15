# Cog attack audit — September 12, 2026

## Scope and evidence

Reviewed all **68 distinct attack names across 135 Cog/attack pairings and all 32 Cog types**. Source evidence is the local public classic `MovieSuitAttacks.py` and `BattleParticles.py`; artwork, rigs and clips come from the bundled extracted TTR library. Static extraction produces `assets/cog_attack_audit.json`, including body-specific constants and affine duration-dependent timing. It does not execute the reference module.

There are dedicated classic movie functions for 59 of the 68 names. Nine have no dedicated function in that file: Close the Loop, Hostile Takeover, Flood the Market, Throw Book, Quash, Nickel and Dime, Money Talks, Embezzle, Beguile. Classic `doDefault` redirects unimplemented attacks to other named movies, so its presence is not evidence for a dedicated current-TTR animation. These nine retain explicitly unverified simulator handling.

Phase archives do not supply current TTR sequencing code or server formulas. This audit does **not** establish full animation or rules parity.

## Implemented corrections

- Applied available per-attack hit reactions, dodge choices, impact/dodge times and sound start times. Previously the generic path ignored its reaction metadata and used uniformly staggered sounds.
- Native Cog animation duration, chosen-target facing, heading restoration and return to idle. Victory remains restricted to the completed Cog win.
- Source-derived hand offsets, rotations, scales and left/right attachment for the available prop records.
- Phone receiver hand change; Fountain Pen ink and Watercooler spray from the resource spout.
- Removed hand-held stormclouds; added overhead clouds, adapted streams and Liquidate ground puddles.
- Glower Power now emits six staggered face-region daggers.
- Added reference particle layers for covered symbol, speech, paper, fire, calculator and magical attacks. Particle textures use bundled suit-particles artwork. Target effects only attach to hit recipients; temporary effects clean up between events.

Particle configs were reviewed as declarative particle instructions and bundled from [open-toontown/resources](https://github.com/open-toontown/resources). 34 mapped definitions are available to this pass; not every source effect is mapped or placed exactly. Resource model paths use the bundled BAM versions. Particle scale is adapted to this scene; original nonuniform effect scaling is preserved.

## Per-attack findings

“Partial reference” means supported constants/attachments were incorporated, with complex paths, stage sequences or dynamically computed placement still adapted. A checked resource or passing test is not proof of visual equivalence.

| Attack | Cogs | Reference | Findings / remaining work |
|---|---|---|---|
| Audit | Bean Counter, Number Cruncher | doAudit | Calculator left-hand transform and five number/symbol particle layers added. |
| Beguile | Mr. Hollywood | No dedicated classic function | Current TTR choreography unverified; existing mapping retained. |
| Bite | Loan Shark | doBite | Teeth model/channel checked; multi-stage biting/target choreography remains adapted. |
| Bounce Check | Double Talker, Short Change, Penny Pincher, Tightwad | doBounceCheck | Multi-bounce path and sequential sound timing remain adapted. |
| Brain Storm | Micromanager, Mover & Shaker | doBrainStorm | Cloud removed from hand; current stream effect does not reproduce the full original storm/projectile sequence. |
| Buzz Word | Micromanager, Double Talker, The Mingler | doBuzzWord | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Calculate | Bean Counter, Number Cruncher | doCalculate | Calculator left-hand transform and five number/symbol particle layers added. |
| Canned | Downsizer, Corporate Raider | doCanned | Hand transform/scale improved; overhead toss/landing path remains adapted. |
| Chomp | Loan Shark | doChomp | Teeth model/channel checked; multi-stage biting/target choreography remains adapted. |
| Clip on Tie | Flunky, Short Change, Telemarketer | doClipOnTie | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Close the Loop | Micromanager | No dedicated classic function | Current TTR choreography unverified; existing mapping retained. |
| Crunch | Number Cruncher | doCrunch | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Demotion | Micromanager | doDemotion | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Double Talk | Double Talker, Cold Caller, Telemarketer | doDoubleTalk | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Downsize | Downsizer | doDownsize | Target shrinking and return sequence remains incomplete. |
| Embezzle | Robber Baron | No dedicated classic function | Current TTR choreography unverified; existing mapping retained. |
| Eviction Notice | Bloodsucker | doEvictionNotice | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Evil Eye | Corporate Raider, Legal Eagle, Two-Face | doEvilEye | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Filibuster | Glad Hander | doFilibuster | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Fill With Lead | Pencil Pusher | doFillWithLead | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Finger Wag | Pencil Pusher, Micromanager, Back Stabber, Big Wig, Penny Pincher, Tightwad, Mr. Hollywood | doFingerWag | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Fired | Tightwad | doFired | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Flood the Market | The Big Cheese | No dedicated classic function | Current TTR choreography unverified; existing mapping retained. |
| Fountain Pen | Pencil Pusher, Micromanager, Head Hunter, Glad Hander | doFountainPen | Right-hand pen and ink spray now use resource spout; splash detail remains adapted. |
| Freeze Assets | Penny Pincher, Tightwad, Cold Caller | doFreezeAssets | Cloud removed from hand; full freezing choreography remains incomplete. |
| Glower Power | Head Hunter, The Big Cheese, Tightwad | doGlowerPower | Six staggered daggers now launch from the face region instead of being held. |
| Guilt Trip | Back Stabber | doGuiltTrip | Impact/jump timing applied; sweeping bars still need a dedicated sequence. |
| Half Windsor | Head Hunter, Mover & Shaker | doHalfWindsor | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Hang Up | Ambulance Chaser, Two-Face | doHangUp | Phone/receiver transforms, receiver hand change and jump dodge timing improved; return path adapted. |
| Head Shrink | Head Hunter | doHeadShrink | Head scaling, detached/falling-head choreography remains incomplete. |
| Hostile Takeover | Corporate Raider | No dedicated classic function | Current TTR choreography unverified; existing mapping retained. |
| Hot Air | Cold Caller | doHotAir | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Jargon | Double Talker, Legal Eagle | doJargon | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Legalese | Legal Eagle | doLegalese | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Liquidate | Bloodsucker, Money Bags | doLiquidate | Cloud/stream and ground puddle added; full sinking choreography remains incomplete. |
| Market Crash | Money Bags | doMarketCrash | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Money Talks | Money Bags | No dedicated classic function | Current TTR choreography unverified; existing mapping retained. |
| Mumbo Jumbo | Double Talker | doMumboJumbo | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Nickel and Dime | Penny Pincher | No dedicated classic function | Current TTR choreography unverified; existing mapping retained. |
| Paradigm Shift | Spin Doctor, The Mingler | doParadigmShift | Target lift/scale choreography remains incomplete. |
| Pecking Order | Legal Eagle | doPeckingOrder | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Pick Pocket | Bottom Feeder, Short Change, Telemarketer, Name Dropper | doPickPocket | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Pink Slip | Downsizer | doPinkSlip | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Play Hardball | Corporate Raider, Loan Shark | doPlayHardball | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Pound Key | Flunky, Cold Caller | doPoundKey | Phone/receiver transforms, receiver hand change, symbol effect and reaction timing improved. |
| Power Tie | Corporate Raider, Money Bags | doPowerTie | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Power Trip | The Big Cheese, Big Wig, Robber Baron, Mr. Hollywood | doPowerTrip | Existing specialized bar effects/jump dodge retained and playback checked. |
| Quake | Spin Doctor, Mover & Shaker | doQuake | Reaction timing checked; full ground/camera shake remains adapted. |
| Quash | Big Wig | No dedicated classic function | Current TTR choreography unverified; existing mapping retained. |
| Razzle Dazzle | Yesman, Name Dropper, Two-Face, Mr. Hollywood | doRazzleDazzle | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Red Tape | Bloodsucker, Ambulance Chaser, Two-Face | doRedTape | Binding tubes are no longer incorrectly held in the Cog hand; target wrapping remains to implement. |
| Restraining Order | Back Stabber | doRestrainingOrder | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Rolodex | Head Hunter, Ambulance Chaser, Telemarketer, Name Dropper | doRolodex | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Rub Out | Pencil Pusher | doRubOut | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Rubber Stamp | Yesman, Bottom Feeder, Double Talker, Glad Hander | doRubberStamp | Pad grip and reaction timing improved; flying CANCELLED text remains missing. |
| Sacked | Downsizer | doSacked | Hand transform/scale improved; overhead sack path remains adapted. |
| Schmooze | Glad Hander, The Mingler | doSchmooze | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Shake | Ambulance Chaser, Mover & Shaker | doShake | Reaction timing checked; full ground/camera shake remains adapted. |
| Shred | Flunky, Bottom Feeder | doShred | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Spin | Spin Doctor | doSpin | Target spin/deformation and source placement remain incomplete. |
| Synergy | Yesman, Robber Baron, Name Dropper | doSynergy | Existing specialized particle sequence/spliced dodge retained and playback checked. |
| Tabulate | Bean Counter, Number Cruncher | doTabulate | Calculator left-hand transform and five number/symbol particle layers added. |
| Tee Off | Yesman, The Big Cheese, Robber Baron, The Mingler | doTeeOff | Existing specialized golf sequence retained and playback checked. |
| Throw Book | Big Wig | No dedicated classic function | Current TTR choreography unverified; existing mapping retained. |
| Tremor | Mover & Shaker | doTremor | Reaction timing checked; full ground/camera shake remains adapted. |
| Watercooler | Bottom Feeder, Short Change | doWatercooler | Left-hand cooler and continuous spray use resource spout. |
| Withdrawal | Bloodsucker | doWithdrawal | Partial reference: available constants, props and effects applied; full stage timing, placement and reactions still require comparison. |
| Write Off | Pencil Pusher, Spin Doctor, Bean Counter, Loan Shark | doWriteOff | Paper/pencil grip improved; flying checkmark remains missing. |

## Verification

- 135 pairings × hit/miss = **270 playback cases**; real model/channel loading, particle simulation, heading/position restoration, and no mid-battle victory.
- One sampled frame for each of the 68 distinct attacks; representative frames visually reviewed. A sampled frame does not establish correctness for an entire clip.
- Existing resource check: all 49 gags, all 32 Cog mappings and six breakup rigs passed.
- 84 mechanics tests passed. Live-round integration passed for impact-time health, emergency Unites, immediate sadness and v2.0 transition.
- No battle probabilities, damage formulas or inventory rules changed.

## Remaining limits

Secondary prop paths, facial/body deformation, some sound combinations and camera cuts are still incomplete. Static extraction intentionally skips expressions it cannot evaluate safely; their values are not asserted as verified. Full audio combinations were not audited by listening. The nine attacks without dedicated classic evidence need a reliable current-TTR choreography reference.

Files: `cog_choreography.py`, `assets/cog_attack_audit.json`, `assets/cog_particle_map.json`. Coverage and rendered frames: `reports/cog-attack-audit/`.
