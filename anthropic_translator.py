"""Anthropic API Translation Helper using Claude Haiku 4.5"""
import json
from anthropic import Anthropic

def translate_with_haiku(french_texts: dict, api_key: str) -> dict:
    """
    Translate French texts to English using Claude Haiku 4.5

    Args:
        french_texts: Dict of {index: french_text}
        api_key: Anthropic API key

    Returns:
        Dict of {index: english_translation}
    """
    client = Anthropic(api_key=api_key)

    # Prepare prompt
    prompt = f"""You are translating architectural/construction documents from French to English.

Translate the following French texts to English. Return ONLY a JSON object with the same keys.

**IMPORTANT RULES:**
- Complete translations only - NO French words in output
- Maintain technical terminology accuracy
- "SIC" means "AS SUCH" or "SUCH"
- Keep abbreviations like "mm", "GA", "TYP."
- Preserve formatting (parentheses, dashes, etc.)
- Material codes stay as-is (DOM, INTL, etc.)
- DO NOT use emojis or special Unicode characters - text only

French texts to translate:
{json.dumps(french_texts, ensure_ascii=False, indent=2)}

Return format:
{{
  "index1": "English translation 1",
  "index2": "English translation 2",
  ...
}}

Return ONLY the JSON, no markdown code blocks."""

    # Call Claude Haiku 4.5
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=8000,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )

    # Parse response
    response_text = message.content[0].text.strip()

    # Remove markdown code blocks if present
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1])  # Remove first and last lines
    if response_text.startswith("json"):
        response_text = response_text[4:].strip()

    # Parse JSON
    try:
        translations = json.loads(response_text)
        # Return translations with token usage
        return {
            "translations": translations,
            "input_tokens": message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens
        }
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse API response as JSON: {e}\n\nResponse:\n{response_text}")


def translate_batch(french_texts: dict, api_key: str, batch_size: int = 50) -> dict:
    """
    Translate texts in batches to avoid token limits

    Args:
        french_texts: Dict of {index: french_text}
        api_key: Anthropic API key
        batch_size: Number of texts per API call

    Returns:
        Dict with "translations" and token usage stats
    """
    all_translations = {}
    total_input_tokens = 0
    total_output_tokens = 0

    # Convert to list of items for batching
    items = list(french_texts.items())

    # Process in batches
    for i in range(0, len(items), batch_size):
        batch = dict(items[i:i + batch_size])
        result = translate_with_haiku(batch, api_key)
        all_translations.update(result["translations"])
        total_input_tokens += result["input_tokens"]
        total_output_tokens += result["output_tokens"]

    return {
        "translations": all_translations,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens
    }


if __name__ == "__main__":
    # Test
    test_texts = {
        "1": "NOTES GÉNÉRALES",
        "2": "SALLE D'EMBARQUEMENT - DOM",
        "3": "SIC, TOUS LES CONDUITS ÉLECTRIQUE ET MÉCANIQUE SONT ENCASTRÉS."
    }

    # You need to set your API key
    import os
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if api_key:
        result = translate_with_haiku(test_texts, api_key)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Set ANTHROPIC_API_KEY environment variable to test")
