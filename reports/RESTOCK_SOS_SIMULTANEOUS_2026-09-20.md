# Restock SOS simultaneous presentation

The previous support_performance appended a complete smooch, lipstick prop and sound sequence per recipient. Replaced that with one NPC smooch/held lipstick/sound and parallel lips projectiles to every living Toon, including the caller. NPC faces the team's center. Projectile origin and destination are evaluated during playback, after arrival, and every projectile uses the same frame-115 release and half-second flight. The sequence length no longer multiplies by the number of Toons.

Assets: bundled TTR lipstick/lips, smooch channels, AA_heal_smooch audio. The retained work/sos-audit/MovieNPCSOS.py gives the prop attachment and release timing, but its old per-target sequence is precisely the behavior replaced here at the user's direction; extracted phases do not prove modern Python scheduling. The official 2016 SOS article describes restock distribution, not simultaneous animation, so it is not evidence for this animation change.

Validation: all eight Restock cards with one, two, three and four living Toons (32 combinations), shared release/arrival timing, caller inclusion, one sound and prop cleanup. All 113 mechanics tests pass. Restock inventory rules were not changed. Backups/logs are in work/restock-sos-fix/. Restart the running simulator to load the edited module.
