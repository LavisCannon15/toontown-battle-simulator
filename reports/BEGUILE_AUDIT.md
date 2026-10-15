# Beguile audit and provisional presentation correction

The previous implementation mapped Beguile to Finger Wag, attached Razzle Dazzle's smile sign to the hand, played Razzle Dazzle audio, and used a sidestep miss. There is no Beguile function in the available classic movie source; the audit entry had no source function.

TTR's documented presentation: Hollywood leans over, teeth sparkle, hit Toons flinch/backstep, and missed Toons duck: https://toontownrewritten.wiki/Beguile . The extracted assets include distinct ttr_s_ene_bat_beguile.ogg and ttr_s_ene_bat_beguileMiss.ogg audio.

Applied: dedicated Beguile movie; removed handheld sign and old Razzle sound fallback; used bundled hit/miss audio, duck dodge and backward hit reaction; attached sparkle particles to the moving head. A leaning glower animation is used provisionally. Exact modern gesture selection, sparkle placement, and timestamps are not verified by modern source or footage. This is a reconstruction, not a complete TTR movie port.

Targeted hit, miss, and mixed-outcome playback checks cover actor channel availability, duck selection, head effect attachment, absence of the unrelated prop, and cleanup.
