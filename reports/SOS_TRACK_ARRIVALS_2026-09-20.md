# SOS arrivals follow their gag track

Cause: support_movie played arrival for every ordinary gag-track SOS during early support processing, retaining each guest until wrap_track later performed/departed it. Trap and Lure guests consequently waited on the battlefield together.

Fix: early support processing still consumes the card once but produces no guest movie. Each support_events record carries its original action. wrap_track creates and plays only that track's arrivals, followed by performance and departure. SOS-only Trap tracks are explicitly dispatched even when there are no player gag actions or health changes. No pending-guest queue is necessary, so resetting cannot leave deferred guests behind.

Evidence: retained work/sos-audit/MovieNPCSOS.py doNPCTeleports produces arrivals and departures for the attacks supplied by a track; retained MovieTrap and MovieLure invoke this per-track. This is classic source guidance, not a claim that current TTR Python is present in extracted phases. Models, animations and sounds remain the bundled extracted TTR assets.

Validation: live Trap+Lure rounds in both caller orders prove the Trap guest is removed before Lure arrival, traps activate/clear, inventory decrements once, and reset leaves no guests. All 113 mechanics tests pass. Existing check_sos_guests exercises model loads and five live SOS tracks plus two simultaneous Toon-Up cards. Logs and backups: work/sos-track-arrivals/.

Files changed: battle_engine.py (event metadata), sos_movies.py (track-scoped arrivals), battle_movies.py (SOS-only track dispatch). A running simulator must restart to load changes.
