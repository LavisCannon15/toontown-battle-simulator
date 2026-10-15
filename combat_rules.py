"""Documented battle rules; unknown live values are not fabricated here."""
# The live post-95 curve is intentionally unpublished (TTR v4.3.3).
ACCURACY_LIMITATION = 'Legacy 95% cap: TTR soft-cap thresholds are unpublished.'

def capped_accuracy(raw):
    return max(5, min(95, raw))

def cog_accuracy(base, accuracy_down=False):
    return max(5, base - (75 if accuracy_down else 0))

def doodle_values(points, trick_index, happy=True):
    """PetTricks/DistributedPetProxyAI interpolation; matches current wiki tables.
    Mood is explicit. Full trait-driven fatigue drift is not reconstructed.
    """
    aptitude=max(0,min(10000,points))/10000
    low,high=(50,97) if happy else (10,60)
    chance=(low+(high-low)*aptitude)*(1-.1*trick_index)
    minimum=5+trick_index
    return int(minimum*(1+aptitude)),chance

