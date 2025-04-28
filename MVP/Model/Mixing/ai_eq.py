import re

EQ_PRESETS = {
    "bass": [r"\bbassy\b", r"\bdeep\b", r"\blow\s*end\b", r"\brumbl\w*", r"\bthump\w*"],
    "treble": [r"\btin(ny)?\b", r"\bthin\b", r"\bbright\b", r"\bsharp\b", r"\bsizzl\w*"],
    "acoustic": [r"\bacoustic\b"],
    "flat": [r"\bflat\b", r"\brevert\b", r"\boriginal\b"],
    "classical": [r"\bclassical\b"],
    "electronic": [r"\belectronic\b", r"\bedm\b", r"\bhouse\b", r"\btrap\b", r"\bdub\w*", r"\bsynth\w*", r"\bclub\b"],
    "hip-hop": [r"\bhip.hop\b", r"\brap\b", r"\bfunk.*"],
    "pop": [r"\bpop\b", r"\bradio\b"],
    "rock": [r"\brock\b", r"\bmetal\b", r"\bpunk\b", r"\broll\b", r"\bgrunge\b"],
    "vocal": [r"\bvocal\b", r"\bvoice\b", r"\bsing.*", r"\blyric.*", r"\bacapella.*"]
}

def apply_eq_from_text(eq_model, text):
    """
    Applies EQ adjustments based on user text input using EqualizerModel.
    """
    text = text.lower()

    if any(re.search(pattern, text) for pattern in EQ_PRESETS["bass"]):
        print("AI EQ: Applying Bass Boost + Suppress Treble & Mid")
        eq_model.set_gain("Low (20-250 Hz)", 6)
        eq_model.set_gain("Mid (250-4000 Hz)", -4)
        eq_model.set_gain("High (4000-20000 Hz)", -6)

    elif any(re.search(pattern, text) for pattern in EQ_PRESETS["treble"]):
        print("AI EQ: Applying Treble Boost + Suppress Mid & Bass")
        eq_model.set_gain("Low (20-250 Hz)", -5)
        eq_model.set_gain("Mid (250-4000 Hz)", -3)
        eq_model.set_gain("High (4000-20000 Hz)", 6)

    elif any(re.search(pattern, text) for pattern in EQ_PRESETS["acoustic"]):
        print("AI EQ: Applying Treble Boost + Suppress Mid & Bass")
        eq_model.set_gain("Low (20-250 Hz)", 4)
        eq_model.set_gain("Mid (250-4000 Hz)", -2)
        eq_model.set_gain("High (4000-20000 Hz)", 4)

    elif any(re.search(pattern, text) for pattern in EQ_PRESETS["flat"]):
        print("AI EQ: Applying Treble Boost + Suppress Mid & Bass")
        eq_model.set_gain("Low (20-250 Hz)", 0)
        eq_model.set_gain("Mid (250-4000 Hz)", 0)
        eq_model.set_gain("High (4000-20000 Hz)", 0)

    elif any(re.search(pattern, text) for pattern in EQ_PRESETS["classical"]):
        print("AI EQ: Applying Treble Boost + Suppress Mid & Bass")
        eq_model.set_gain("Low (20-250 Hz)", 6)
        eq_model.set_gain("Mid (250-4000 Hz)", -4)
        eq_model.set_gain("High (4000-20000 Hz)", 4)

    elif any(re.search(pattern, text) for pattern in EQ_PRESETS["electronic"]):
        print("AI EQ: Applying Treble Boost + Suppress Mid & Bass")
        eq_model.set_gain("Low (20-250 Hz)", 6)
        eq_model.set_gain("Mid (250-4000 Hz)", -6)
        eq_model.set_gain("High (4000-20000 Hz)", 6)

    elif any(re.search(pattern, text) for pattern in EQ_PRESETS["hip-hop"]):
        print("AI EQ: Applying Treble Boost + Suppress Mid & Bass")
        eq_model.set_gain("Low (20-250 Hz)", 6)
        eq_model.set_gain("Mid (250-4000 Hz)", -5)
        eq_model.set_gain("High (4000-20000 Hz)", 3)

    elif any(re.search(pattern, text) for pattern in EQ_PRESETS["pop"]):
        print("AI EQ: Applying Treble Boost + Suppress Mid & Bass")
        eq_model.set_gain("Low (20-250 Hz)", -4)
        eq_model.set_gain("Mid (250-4000 Hz)", 5)
        eq_model.set_gain("High (4000-20000 Hz)", -2)

    elif any(re.search(pattern, text) for pattern in EQ_PRESETS["rock"]):
        print("AI EQ: Applying Treble Boost + Suppress Mid & Bass")
        eq_model.set_gain("Low (20-250 Hz)", 5)
        eq_model.set_gain("Mid (250-4000 Hz)", -3)
        eq_model.set_gain("High (4000-20000 Hz)", 6)

    elif any(re.search(pattern, text) for pattern in EQ_PRESETS["vocal"]):
        print("AI EQ: Applying Treble Boost + Suppress Mid & Bass")
        eq_model.set_gain("Low (20-250 Hz)", -5)
        eq_model.set_gain("Mid (250-4000 Hz)", 6)
        eq_model.set_gain("High (4000-20000 Hz)", 2)

    else:
        print("No EQ match found in input.")
