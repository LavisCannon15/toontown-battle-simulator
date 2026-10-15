# Damage number color audit

Reference: Open Toontown `toontown/suit/DistributedSuitBase.py`, showHpText, retained in work/ref-DistributedSuitBase.py (lines 401–436).

| Type | Reference bonus argument | RGBA |
| --- | --- | --- |
| Base damage | 0 | (0.9, 0, 0, 1), red |
| Same-track combo | 1 | (1, 1, 0, 1), yellow |
| Lure knockback | 2 | (1, 0.5, 0, 1), orange |
| Healing | 0, positive amount | (0, 0.9, 0, 1), green |

MovieThrow and MovieSquirt pass bonus 2 for kbbonus and bonus 1 for hpbonus. Their bonus sequences wait 0.75 seconds for each nonzero bonus, showing knockback before combo. The simulator now passes these types through to the text renderer and retains the reference rise/hold/fade durations (1.0 / 0.85 / 0.1 seconds).

The reference also has a blue base-damage override for matching interactive street-prop bonuses. The simulator does not model that street-prop mechanic; this patch does not invent or enable it. These are verified classic source colors; extracted textures alone do not specify text color logic.

Remaining limitation: multiple Toons' base damage is still combined at the final contact for a target. This color fix does not implement individual-hit number scheduling.
