# Guilt Trip and Sacked

Compared retained MovieSuitAttacks.doGuiltTrip (3361–3396) and doSacked (1641–1697). Uses bundled TTR sandbag, Toon/Cog animation channels and sound. Missing classic guiltTrip particle config obtained from https://raw.githubusercontent.com/open-toontown/resources/master/phase_5/etc/guiltTrip.ptf; waterfall config was already present.

Guilt Trip now uses the two reference-colored particle effects at headings -90/+90, scale 5, starting .7; after .4 seconds they travel to Suit-local Y=15 in one second and fade .4. Red/gray waterfall effect scale 11 starts .6. Team hit reaction slip-forward at 1.5, jump dodge .86, sound 1.1; mixed-hit events retain individual health results.

Sacked now has the source right-hand transform, appears .85, grows .2, releases 2.98, follows a .9-second arc and grows/rotates in flight. Hit bag attaches to the Toon hips; miss lands without attachment. Hit reaction starts 3.88 with struggle then slip-backward; damage displays at 5.68. Single visible Toon uses one bag instead of duplicated LOD props.

Visual inspection caught the generic loader posing the bag at Drop animation frame 0, which displaced its geometry. Added an optional pose_frame argument to movie_prop; Sacked alone requests the unposed bind model. Extracted bag geometry is larger than the old source's assumption, so final scale and position fit oriented bag bounds to the Toon while retaining source rotation/nonuniform proportions. This fit is an adaptation, not an exact port of the old target-offset constants.

Tests/check_guilt_sacked.py passes mixed/all-miss Guilt Trip, moving effects, Sacked hand/flight/hip attachment, hit-only attachment, actual geometry center/height/ground bounds, delayed damage, cleanup. Both were rendered and inspected. All 93 battle-rule tests passed. Classic-source choreography is adapted to simulator proportions; phase resources do not contain modern TTR sequencing code.
