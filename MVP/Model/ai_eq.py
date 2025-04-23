import re
from PyQt6.QtWidgets import QLineEdit, QMenu, QAction

# Hardcoded EQ keyword → action mappings
EQ_PRESETS = {
    "bass": ["bassy", "deep", "low end", "thumpy", "rumble"],
    "treble": ["tinny", "thin", "bright", "sharp", "sizzly"]
}

def apply_eq_from_text(eq_model, text):
    """
    Applies EQ adjustments based on user text input using EqualizerModel.
    """
    lowered = text.lower()

    # Bass boost
    if any(re.search(rf"\b{word}\b", lowered) for word in EQ_PRESETS["bass"]):
        eq_model.set_gain("Low (20-250 Hz)", 6)
        print("Applying bass boost")

    # Treble boost
    if any(re.search(rf"\b{word}\b", lowered) for word in EQ_PRESETS["treble"]):
        eq_model.set_gain("High (4000-20000 Hz)", 5)
        print("Applying treble boost")

    # Future: Add reverb, echo, notch filtering, etc.
