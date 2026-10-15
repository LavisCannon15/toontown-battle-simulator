# SOS fixes applied

- Removed the caller's telephone animation and receiver for all ordinary SOS cards; Lowden already leaves the caller idle.
- Fixed SOS-only Toon-Up live healing and aligned SOS-only gag health changes with the NPC performance impact.
- SOS Trap skips occupied and lured Cogs; ordinary overlapping Toon traps still retain their separate cancellation rule.
- Restocks respect unlocked track levels, carry limits, missing tracks and pouch space, and exclude level 7 gags.
- Each damaging SOS supplies one successful stun contribution per affected target, rather than one contribution for every Cog in the group.
- Accuracy statuses are stored on their recipients; replacement characters do not inherit them. Toon-Up accuracy now includes the recipient's Toons Hit bonus.
- Every card has star metadata; descriptions clarify healing, restocking and status behavior.
- NPC gag performances now use the shared resource-backed gag builders. Restock includes lipstick and travelling lips; status performances include the reference's five particle effects per recipient and native sprinkle animation.
- Existing custom gag-panel layout values were preserved.

## Verification

91 unit tests passed. All 32 isolated offscreen SOS playback cases completed, consumed one card, and removed their NPC. Live healing from one Laff produced 16, 31 and 46 Laff per Toon for the three healing cards in a four-Toon team. Lowden's dedicated appearance, cannon and cleanup check passed.

These checks advance intervals programmatically; they do not certify continuous visual timing or audio quality.

## Remaining limits

Bundled TTR phase assets provide models, animations and sounds, not current server rules or complete movie sequencing. Ordinary NPC body proportions and outfits still use the simulator's shared body construction. Several standard NPC gag identities use the classic reference's high-tier choice; exact modern per-card differences require stronger evidence. Mixed ordinary/SOS combo and lure interactions, exact status reapplication behavior, restock purchase-history restrictions and the unpublished accuracy soft cap remain incomplete or unverified. No experimental soft-cap formula was enabled.
