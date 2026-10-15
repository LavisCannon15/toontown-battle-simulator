# SOS NPC presentation

Calling an SOS card now creates a separate NPC scene character in front of its caller. The caller uses the phone; the NPC appears, waves toward the caller, turns toward the battle, performs in the card's track, then bows and teleports away. Non-gag rewards perform during their support event. NPCs do not become party members, targets, status cards or extra battle actions. Separate callers have separate guests, and new battles clear guests.

Uses the bundled character rigs, head variants/colors already recorded in sos_portraits.json, teleport/wave/bow clips, and gag props. Staging follows public MovieNPCSOS.teleportIn/teleportOut/doNPCTeleports, with spacing adapted to this scene:
https://github.com/open-toontown/open-toontown/blob/develop/toontown/battle/MovieNPCSOS.py

Limits: body proportions and clothing still use the simulator's shared Toon body. Cards lacking a portrait definition use a generic dog guest. Performances are abbreviated and do not yet reproduce every NPC-specific gag, particle effect or camera shot. This fixes the missing NPC lifecycle; it does not establish exact SOS combo mechanics.

Verification: all card guest models loaded, front-of-caller placement checked, rendered arrival inspected, five reward categories and multiple callers exercised through live rounds with cleanup checks. Existing mechanics tests were rerun separately.
