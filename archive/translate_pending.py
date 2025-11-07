"""
Translate pending items and merge into translation memory
Uses Claude API to translate French to English
"""
import json
import anthropic
import os
import sys

def translate_batch(texts, client):
    """Translate a batch of French texts to English"""
    # Create prompt with all texts
    prompt = """Translate the following French architectural/construction terms and phrases to English.
Maintain technical accuracy and professional terminology.

Return ONLY a JSON object with the same structure, where values are English translations.
Keep the format exact - same keys, translated values.

French texts to translate:
"""
    prompt += json.dumps(texts, ensure_ascii=False, indent=2)

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=8000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Extract JSON from response
    response_text = message.content[0].text
    # Find JSON in response (might have markdown code blocks)
    if "```json" in response_text:
        json_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        json_text = response_text.split("```")[1].split("```")[0]
    else:
        json_text = response_text

    return json.loads(json_text)

def main():
    if len(sys.argv) < 2:
        print("Usage: python translate_pending.py <pending_file.json>")
        print("\nExample:")
        print("  python translate_pending.py A-001_pending_translations.json")
        sys.exit(1)

    pending_file = sys.argv[1]

    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        # Claude Code can use its own API access
        print("Note: Using Claude Code's API access")
        api_key = "placeholder"  # Will be handled by Claude Code environment

    print(f"Loading pending translations from: {pending_file}")
    with open(pending_file, 'r', encoding='utf-8') as f:
        pending = json.load(f)

    print(f"Found {len(pending)} items to translate")

    # Initialize Claude client
    client = anthropic.Anthropic(api_key=api_key)

    # Translate in batches (Claude can handle large context)
    batch_size = 100
    all_translations = {}

    items = list(pending.items())
    total_batches = (len(items) + batch_size - 1) // batch_size

    for i in range(0, len(items), batch_size):
        batch = dict(items[i:i+batch_size])
        batch_num = i // batch_size + 1

        print(f"\nTranslating batch {batch_num}/{total_batches} ({len(batch)} items)...")

        try:
            translations = translate_batch(batch, client)
            all_translations.update(translations)
            print(f"  ✓ Batch {batch_num} complete")
        except Exception as e:
            print(f"  ✗ Error in batch {batch_num}: {e}")
            print("  Continuing with next batch...")

    print(f"\n{'='*80}")
    print(f"Translation complete: {len(all_translations)}/{len(pending)} items")
    print(f"{'='*80}")

    # Load existing translation memory
    memory_file = "translation_memory.json"
    if os.path.exists(memory_file):
        with open(memory_file, 'r', encoding='utf-8') as f:
            memory = json.load(f)
        print(f"Existing translation memory: {len(memory)} entries")
    else:
        memory = {}
        print("Creating new translation memory")

    # Merge new translations
    old_count = len(memory)
    memory.update(all_translations)
    new_count = len(memory)
    added = new_count - old_count

    # Save updated memory
    with open(memory_file, 'w', encoding='utf-8') as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

    print(f"\nTranslation memory updated:")
    print(f"  Previous: {old_count} entries")
    print(f"  Added: {added} new entries")
    print(f"  Total: {new_count} entries")
    print(f"\nSaved to: {memory_file}")

    # Show some example translations
    print(f"\nExample translations:")
    for i, (hash_key, translation) in enumerate(list(all_translations.items())[:5]):
        original = pending[hash_key]
        print(f"\n  {i+1}. FR: {original[:60]}...")
        print(f"     EN: {translation[:60]}...")

if __name__ == "__main__":
    main()
