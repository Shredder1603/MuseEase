import re

EQ_PRESETS = {
    "bass": [r"\bbassy\b", r"\bdeep\b", r"\blow\s*end\b", r"\brumbl\w*", r"\bthump\w*"],
    "treble": [r"\btin(ny)?\b", r"\bthin\b", r"\bbright\b", r"\bsharp\b", r"\bsizzl\w*"]
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

    else:
        print("No EQ match found in input.")
