# Accuracy SOS simultaneous effects

Cogs Miss and Toons Hit now use one NPC sprinkle-dust performance with one pixie-dust sound cue. The extracted particle effects reach all living recipients together. Toons Hit includes the caller. Restock keeps its separate simultaneous lipstick performance.

Cogs Miss also displays impact laughter through the existing Cog speech system, temporarily replacing the name tags. The dialogue timing and laughter strings come from the retained classic MovieNPCSOS.__healToon and TTLocalizerEnglish.MovieHealLaughterHits1. The simultaneous recipient choreography follows the requested TTR behavior; extracted phase assets alone do not establish modern TTR Python logic or exact current dialogue wording.

Validation: tests/check_accuracy_sos_simultaneous.py passed for all six accuracy SOS cards with one through four recipients, checking parallel particle delivery, one casting sound, Cog bubbles, and cleanup. All 113 unit tests passed. These checks verify interval behavior, not complete visual parity with TTR. Restart the simulator to load the change.
