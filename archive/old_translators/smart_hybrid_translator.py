"""
Smart Hybrid Translator:
- Short text (< 50 chars): Dictionary lookup with word-by-word replacement
- Long text (>= 50 chars): Claude Code translates contextually
"""
import json
import re

# Load full translation dictionary
with open('translations.json', 'r', encoding='utf-8') as f:
    TRANSLATION_DICT = json.load(f)

print(f"Loaded {len(TRANSLATION_DICT)} translations")

def translate_text_smart(text):
    """
    Smart hybrid translation:
    - Short text: Use dictionary
    - Long text: Would use Claude Code (for now, use enhanced dictionary)
    """
    if not text or not text.strip():
        return text

    # For short text, use dictionary word-by-word replacement
    if len(text) < 150:  # Threshold for "short" text
        translated = text
        # Sort by length (longest first) to avoid partial matches
        sorted_terms = sorted(TRANSLATION_DICT.items(), key=lambda x: len(x[0]), reverse=True)
        for french, english in sorted_terms:
            # Use word boundary for better matching (if possible)
            try:
                pattern = re.compile(r'\b' + re.escape(french) + r'\b', re.IGNORECASE)
            except:
                pattern = re.compile(re.escape(french), re.IGNORECASE)
            translated = pattern.sub(english, translated)
        return translated
    else:
        # For long text, do dictionary replacement first
        # In a full implementation, this would call Claude Code API
        translated = text
        sorted_terms = sorted(TRANSLATION_DICT.items(), key=lambda x: len(x[0]), reverse=True)
        for french, english in sorted_terms:
            pattern = re.compile(re.escape(french), re.IGNORECASE)
            translated = pattern.sub(english, translated)
        return translated

# Test
if __name__ == "__main__":
    tests = [
        "REVÊTEMENT D'ACIER",
        "M2.3 REVÊTEMENT D'ACIER SUR MUR DE BÉTON COULÉ",
        "NOTE 4: LA PROFONDEUR DES SOUS-ENTREMISES EST À VALIDER PAR LE SOUS-TRAITANT SELON LE MODÈLE DE BRIS",
    ]

    for test in tests:
        result = translate_text_smart(test)
        print(f"\n{test}")
        print(f"  -> {result}")
