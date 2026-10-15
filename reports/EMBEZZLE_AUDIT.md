# Embezzle audit

The old movie used a generic Pick Pocket fallback: a bill existed during misses, appeared before the grab, played the fishing-bill animation, and lacked the dollar-sign effect and Embezzle-specific audio.

Reference description: https://toontownrewritten.wiki/Embezzle . On a hit, Robber Baron takes a large bill, shakes it with dollar signs, and pockets it; on a miss there is no bill. The extracted assets contain the dedicated Embezzle audio, a dollar-sign mesh in suit-particles, and the Pick Pocket channel. The classic doPickPocket reference supplies the right-hand bill transform but is not the modern Embezzle sequence.

Applied: hit-only bill and dollar signs, delayed bill appearance, source right-hand transform, no fishing-channel playback, bill removal during the pocketing motion, and dedicated sound. Miss dodge uses the documented jump. User clarified the reported defect was not the Toon's reaction.

Limitations: the extended right-arm reach has NOT been reconstructed. Inspection of the 101-frame native Pick Pocket animation shows only a short reach. Exact modern grab/shake/pocket timing and hand stretch require further reference; the new timestamps and dollar-sign motion are approximations. Do not claim full Embezzle parity.

Checks passed for hit-only bill/signs, delayed right-hand attachment, miss branch, and cleanup.
