"""
AI-Powered Translation using Claude API
This provides intelligent French to English translation for any text
"""
import os
from anthropic import Anthropic

# Cache for translated phrases to avoid re-translating
TRANSLATION_CACHE = {}

def translate_with_ai(text, api_key=None):
    """
    Translate French text to English using Claude AI

    Args:
        text: French text to translate
        api_key: Anthropic API key (optional, will use env variable if not provided)

    Returns:
        Translated English text
    """
    # Check cache first
    if text in TRANSLATION_CACHE:
        return TRANSLATION_CACHE[text]

    # Get API key from environment or parameter
    if api_key is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        # Fallback: return original text if no API key
        print(f"Warning: No API key found, returning original text: {text[:50]}...")
        return text

    try:
        client = Anthropic(api_key=api_key)

        # Create translation prompt
        prompt = f"""Translate this French architectural/technical text to English.
Keep it concise and use standard architectural terminology.
Preserve any reference codes (like AR-XXX, numbers, etc.) exactly as they are.

French text: {text}

English translation (just the translation, nothing else):"""

        message = client.messages.create(
            model="claude-3-haiku-20240307",  # Fast and cost-effective
            max_tokens=500,
            temperature=0,  # Deterministic for consistency
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        translation = message.content[0].text.strip()

        # Cache the result
        TRANSLATION_CACHE[text] = translation

        return translation

    except Exception as e:
        print(f"AI translation error for '{text[:30]}...': {e}")
        return text  # Return original on error


def translate_batch_with_ai(texts, api_key=None):
    """
    Translate multiple French texts to English in a single API call (more efficient)

    Args:
        texts: List of French texts to translate
        api_key: Anthropic API key

    Returns:
        Dictionary mapping original text to translated text
    """
    # Check which texts need translation (not in cache)
    texts_to_translate = [t for t in texts if t not in TRANSLATION_CACHE]

    if not texts_to_translate:
        # All texts are cached
        return {t: TRANSLATION_CACHE[t] for t in texts}

    # Get API key
    if api_key is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        print("Warning: No API key found for batch translation")
        return {t: t for t in texts}  # Return originals

    try:
        client = Anthropic(api_key=api_key)

        # Create batch translation prompt
        numbered_texts = "\n".join([f"{i+1}. {text}" for i, text in enumerate(texts_to_translate)])

        prompt = f"""Translate these French architectural/technical texts to English.
Keep translations concise and use standard architectural terminology.
Preserve any reference codes (like AR-XXX, numbers, etc.) exactly as they are.
Return ONLY the numbered translations, one per line.

French texts:
{numbered_texts}

English translations (numbered list only):"""

        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=3000,
            temperature=0,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Parse the response
        translations_text = message.content[0].text.strip()
        translation_lines = translations_text.split('\n')

        result = {}

        # Map translations back to original texts
        for i, original in enumerate(texts_to_translate):
            # Try to find the corresponding translation
            if i < len(translation_lines):
                # Remove numbering (e.g., "1. " or "1) ")
                translated = translation_lines[i].strip()
                # Remove leading number and punctuation
                import re
                translated = re.sub(r'^\d+[\.\)]\s*', '', translated)

                result[original] = translated
                TRANSLATION_CACHE[original] = translated
            else:
                result[original] = original  # Fallback

        # Add cached translations
        for text in texts:
            if text in TRANSLATION_CACHE and text not in result:
                result[text] = TRANSLATION_CACHE[text]

        return result

    except Exception as e:
        print(f"Batch AI translation error: {e}")
        return {t: t for t in texts}  # Return originals on error


if __name__ == "__main__":
    # Test the AI translator
    print("Testing AI translator...")

    test_texts = [
        "LÉGENDES ET NOTES GÉNÉRALES",
        "DISPOSITIFS AU PÉRIMÈTRE DES PORTES",
        "ÉVIER DE BROSSAGE",
    ]

    print("\nSingle translations:")
    for text in test_texts:
        translated = translate_with_ai(text)
        print(f"  {text} -> {translated}")

    print("\nBatch translation:")
    batch_result = translate_batch_with_ai(test_texts)
    for orig, trans in batch_result.items():
        print(f"  {orig} -> {trans}")
