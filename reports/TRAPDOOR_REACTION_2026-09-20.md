# Trapdoor visibility and reaction

The extracted trapdoor.bam is a flat two-unit-wide card at local Z=0. Persistent traps were at Z=.025, below the plaza pavement top at Z=.04 (grid lines reach .06). Put flat Quicksand/Trapdoor props at Z=.08 with normal depth testing, and use the retained placement source's 1.7 scale multiplied by each Suit's scene scale. Visual render confirms visible boards on A/B/C bodies.

Trapdoor activation now has a dedicated MovieLure-based reaction: spliced first .7 seconds of flail with .25 seconds of inserted waits, black hole transition, reversed flail, idle, remaining flail, pause and slip-forward landing. Fall starts at 2.2s and takes .4s; hide for 1.6s; reappear 15 Suit-scaled units above the hole and descend over .3s. Trap shrinks at 2.4s over .8s. Preserve the source's 3.5s damage event and opening/bodyfall audio sequence. The Lure destination matches the actual Trapdoor position, followed by the existing backwards formation recovery.

References: bundled phase_5/models/props/trapdoor.bam; retained original workspace work/ref-MovieTrap.py (__createPlacedTrapMultiTrack) and work/ref-MovieLure.py (trapdoor branch). These retained scripts are classic source, not modern TTR Python extracted from phases.

Validation: check_trapdoor_reaction.py checks world bounds above pavement, all A/B/C bodies, blackening, underground interval, falling/landing, one damage event, return and interruption with New battle. Render: work/trapdoor-reaction/placed.png. Regression: check_trap_panel_revision.py covers 24 Trap/Lure combinations. Logs/backups are under work/trapdoor-reaction. Running application must restart to load these modules.
