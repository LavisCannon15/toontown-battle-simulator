# Lowden speech audit — 2026-09-13

Confirmed in the user's reference video: https://www.youtube.com/watch?v=oQSXv7RyrH8

There are two separate dialogue moments, not two simultaneous bubbles:

- Around 9–10 seconds: greeting after arrival, thanking the caller and saying he will take it from here.
- Around 21–22 seconds: after the Cogs have been fired, a second bubble appears before/during propeller departure. The visible text reads “Happy to be of assistance, as always.” The inset gameplay was inspected in full screen; punctuation is a visual transcription, not extracted localization data.

The previous inspection stopped around 20 seconds and missed this later line. That earlier uncertainty is now resolved: the second bubble is present in this demonstration.

Current simulator: `lowden_movie.movie` calls `speech` only once, for the greeting. Its departure calls `flight` without `speech`. `sos_movies.support_movie` routes this card directly to Lowden's special movie, bypassing generic SOS arrival/departure dialogue. No second/overlapping dialogue path was found. The defect is a missing farewell, not duplicate greeting construction.

Required correction: add the farewell after firing completes, as departure begins; hide the name while it is visible and clean up with the guest. Preserve the four-second flight movement and complete departure audio. Do not overlap it with the arrival greeting or borrow the generic “See you later!” line.

Implemented after user approval: the farewell now accompanies departure for four seconds, after firing finishes. Verified both lines, no overlapping bubbles, name replacement, normal cleanup and New Battle interruption (`work/lowden-farewell.log`). Flight movement and full audio remain unchanged.
