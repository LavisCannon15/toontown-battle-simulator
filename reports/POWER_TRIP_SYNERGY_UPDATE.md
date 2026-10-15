# Power Trip and Synergy

Replaced the simplified Power Trip particles and missing Synergy effects with the public game's particle definitions. The definitions are bundled under assets/particle_effects; Synergy's dollar-sign texture still comes from the extracted TTR suit-particles model. Only the model filename extension was adapted for the current loader.

Power Trip: two purple power bars, central waterfall, reference actor-relative placement and movement/fade sequence; impact at 1.8 seconds, jump dodge at 1.29 seconds, slip-forward hit reaction.

Synergy: dollar-sign ring and waterfall, impact at 1.7 seconds, the spliced jump dodge starting at 0.91 seconds, slip-forward hit reaction. SA_synergy starts at 0.9 seconds; Toon_bodyfall_synergy starts at 2.2 seconds only when a Toon is hit.

References:
- Local ref-MovieSuitAttacks.py: doPowerTrip and doSynergy.
- https://github.com/open-toontown/resources/tree/master/phase_5/etc : powertrip.ptf, powertrip2.ptf, waterfall.ptf, synergy.ptf, synergyWaterfall.ptf. These are reviewed classic particle definitions, not files recovered from the installed TTR archives.

Dedicated hit/miss tests cover effect creation, interval playback and cleanup, and rendered frames were inspected. The fixed camera and character scale remain simulator adaptations. Sound scheduling is checked, not audited by listening.
