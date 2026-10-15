# Throw Book trajectory correction

The previous generic `prop_movie` moved the book along a straight 0.4-second line toward a fixed torso point, then removed it. Its scale was correct and is preserved at recipe value 0.01, multiplied by the Cog's actor scale.

`throw_book_movie.py` now retains the 3.03-second release, uses a 1.2-second ballistic arc, and finds a landing point from the rendered Toon head and the book's bottom bounds. A hit reparents the book to the head with world transforms preserved for a short contact hold. A miss ends on the ground behind the Toon and uses a jump dodge. Damage occurs at arrival (4.23 seconds), not the obsolete 3.43-second impact. No model normalization or flight growth was added.

Evidence: the retained classic MovieSuitAttacks dispatches THROW_BOOK to doDefault; it does not provide modern choreography. TTR's documented behavior confirms head landing and jump dodge: https://toontownrewritten.wiki/Throw_Book . The arc uses our source-derived ballistic helper. Flight duration, contact hold and detailed modern timing are a reconstruction, not verified TTR source constants.

Verified with the real extracted lawBook model against both outer Toon targets, hit and miss: unchanged held/released world scale, visibly curved trajectory, head/ground contact, health delayed until impact, cleanup, and cancellation without damage. Rendered head-contact frame inspected. Test: `tests/check_throw_book.py`.
