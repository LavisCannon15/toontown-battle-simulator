# Lord Lowden Clear SOS correction

Removed the generic dog/dust fallback for this card. The battlefield guest now combines the extracted Cashbot suit, Cashbot clothing textures and a red Toon dog head. The SOS portrait also has a dedicated red dog definition. Head attachment follows the public Toon.makeCogDisguise pattern, retaining Toon-sized head proportions rather than scaling the head down with the suit.

Group Fire reuses the existing cannon insertion, aim, launch and sound sequence for each affected Cog, without repeating the caller's button animation. It consumes one SOS card. Fired Cogs no longer play the ordinary breakup sequence afterward.

Character reference: https://www.toontownrewritten.com/news/item/299/the-silly-spotlight-lord-lowden-clear
Effect reference: https://toontownrewritten.wiki/Lord_Lowden_Clear
Local sequence references: ref-MovieFire.py and ref-Toon.py.

Limits: the guest's walk-in, speech gesture and walk-out are adapted from available suit clips. Exact current TTR Lord Lowden Clear choreography and DNA were not recovered from the extracted asset library; this is not a claim of a frame-exact port. Cashbot body choice and sizing are scene adaptations.

Dedicated live check verifies the disguise, four cannons, absence of dust and breakup, one card spent, Cog removal and victory. A rendered group-Fire frame was inspected.
