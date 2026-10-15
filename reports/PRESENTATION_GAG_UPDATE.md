# Presentation gag

Replaced the hand-held slideshow shortcut with a button press and a separate screen in front of the caller. Uses extracted av_screen and button models, pushbutton and hypnotized clips. Screen appears at 2.5 seconds, expands for 1.2 seconds, remains visible, then collapses over 0.4 seconds. Scene size and offset remain adapted to the simulator.

The public MovieLure.__createSlideshowMultiTrack reference supplies two distinct sounds: TL_presentation at 2.3 seconds and AA_drop_trigger_box at 2.5 seconds. Both are scheduled; the incorrect generic Hypno-goggles cue is excluded. Multiple sounds in one gag are intentional when they represent separate reference cues.

Rendered placement and screen cleanup were inspected/tested, along with cue selection and live Railroad/Presentation activation. Audio scheduling was checked programmatically, not by listening. This change does not claim that every gag's full sound choreography has been audited.
