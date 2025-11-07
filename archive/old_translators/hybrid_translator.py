"""
Hybrid Translator: Dictionary + AI Fallback
Fast dictionary lookup with AI-powered fallback for unknown terms
"""
from translation_dictionary import TRANSLATION_DICT
from ai_translator import translate_with_ai
import re

def translate_text_hybrid(text, use_ai=True, api_key=None):
    """
    Translate French text using dictionary first, then AI fallback

    Args:
        text: French text to translate
        use_ai: Whether to use AI for unknown terms (default: True)
        api_key: Anthropic API key for AI translation

    Returns:
        Translated English text
    """
    original_text = text
    translated = text

    # Step 1: Try dictionary translation (fast)
    # Sort by length (longest first) to avoid partial matches
    sorted_terms = sorted(TRANSLATION_DICT.items(), key=lambda x: len(x[0]), reverse=True)

    for french, english in sorted_terms:
        # Case-insensitive replacement
        pattern = re.compile(re.escape(french), re.IGNORECASE)
        translated = pattern.sub(english, translated)

    # Step 2: Check if translation happened
    if translated == original_text and use_ai:
        # Nothing was translated by dictionary, try AI
        print(f"  [AI] Translating: {text[:50]}...")
        translated = translate_with_ai(text, api_key)

    return translated


def translate_batch_hybrid(texts, use_ai=True, api_key=None):
    """
    Translate multiple texts using hybrid approach

    Args:
        texts: List of French texts
        use_ai: Whether to use AI for unknown terms
        api_key: Anthropic API key

    Returns:
        Dictionary mapping original text to translation
    """
    results = {}
    ai_needed = []

    # Step 1: Try dictionary for all texts
    for text in texts:
        translated = text

        sorted_terms = sorted(TRANSLATION_DICT.items(), key=lambda x: len(x[0]), reverse=True)
        for french, english in sorted_terms:
            pattern = re.compile(re.escape(french), re.IGNORECASE)
            translated = pattern.sub(english, translated)

        if translated == text and use_ai:
            # No dictionary match, needs AI
            ai_needed.append(text)
        else:
            results[text] = translated

    # Step 2: Batch translate remaining texts with AI
    if ai_needed and use_ai:
        print(f"  [AI] Translating {len(ai_needed)} unknown terms...")
        from ai_translator import translate_batch_with_ai
        ai_results = translate_batch_with_ai(ai_needed, api_key)
        results.update(ai_results)

    return results


if __name__ == "__main__":
    # Test hybrid translator
    print("Testing hybrid translator...")

    # Test with known dictionary terms
    print("\n1. Dictionary terms (should be instant):")
    test1 = "LÉGENDES ET NOTES GÉNÉRALES"
    result1 = translate_text_hybrid(test1, use_ai=False)
    print(f"  {test1}")
    print(f"  -> {result1}")

    # Test with unknown term (would use AI)
    print("\n2. Unknown term (would use AI if enabled):")
    test2 = "Quelque chose de complètement nouveau"
    result2_no_ai = translate_text_hybrid(test2, use_ai=False)
    print(f"  Without AI: {test2} -> {result2_no_ai}")

    # Note: To test with AI, you need to set ANTHROPIC_API_KEY environment variable
    # result2_ai = translate_text_hybrid(test2, use_ai=True)
    # print(f"  With AI: {test2} -> {result2_ai}")
