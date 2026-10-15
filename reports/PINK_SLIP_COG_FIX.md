# Pink Slip Cog attack

Compared retained MovieSuitAttacks.doPinkSlip (1539–1583), using the bundled extracted pink-slip model, throw-paper/Toon animations and SA_pink_slip sound. Dedicated pink_slip_movie.py only handles the Cog attack; Toon fires and Lowden presentation are separate.

Fixed source right-hand position/rotation, .8 appearance, .5 growth to scale 8 and 1.73 hold. Release at 3.03; paper travels .5 to the Toon ground point while rotating to H=300. Hit pauses .01, rises/slides .2, lands over 1.1, spinning to (-200,100,100). Miss slides along the ground over .5 with a different final rotation. Paper shrinks .4 and clears. Classic displacement values use simulator .62 scale.

Hit reaction begins 2.81 (jump from .3 for .7, then slip-forward), damage at 3.71. Miss jumps at 2.8. Sound at 2.9 for 1.1. Custom ordinary reaction yields to immediate fatal-hit sadness; cancellation cleans the model.

Validation: tests/check_pink_slip.py passes hit/miss flight endpoints, held-model geometry size, ground arrival, tumble height, exact live damage timing, fatal/cancel and cleanup checks. All 93 battle-rule tests passed. Classic-source behavior is adapted to simulator scale, not independently verified frame-perfect current TTR movie code.
