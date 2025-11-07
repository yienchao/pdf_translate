"""
Directly translate A-081 pending translations and apply to PDF
Uses Claude API to translate French to English
"""
import json
import anthropic
import os
import sys
import fitz
import hashlib

def normalize_text(text):
    """Normalize text for consistent hashing"""
    normalized = ' '.join(text.split())
    return normalized

def hash_text(text):
    """Create hash of text for dictionary lookup"""
    normalized = normalize_text(text)
    hash_obj = hashlib.sha256(normalized.encode('utf-8'))
    return hash_obj.hexdigest()

def translate_batch(texts, client):
    """Translate a batch of French texts to English"""
    # Create prompt with all texts
    prompt = """Translate the following French architectural/construction terms and phrases to English.
Maintain technical accuracy and professional terminology.
Keep numbers and codes as-is.

Return ONLY a JSON object with the same structure, where values are English translations.
Keep the format exact - same keys, translated values.

French texts to translate:
"""
    prompt += json.dumps(texts, ensure_ascii=False, indent=2)

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=16000,
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
    print("="*80)
    print("A-081 TRANSLATION SYSTEM")
    print("="*80)

    # Load pending translations
    pending_file = "A-081_pending_translations.json"
    print(f"\nLoading pending translations from: {pending_file}")
    with open(pending_file, 'r', encoding='utf-8') as f:
        pending = json.load(f)

    print(f"Found {len(pending)} items to translate")

    # Initialize Claude client
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # Translate in batches
    batch_size = 100
    all_translations = {}

    items = list(pending.items())
    total_batches = (len(items) + batch_size - 1) // batch_size

    print(f"\n{'='*80}")
    print(f"PHASE 1: TRANSLATING {len(pending)} ITEMS")
    print(f"{'='*80}\n")

    for i in range(0, len(items), batch_size):
        batch = dict(items[i:i+batch_size])
        batch_num = i // batch_size + 1

        print(f"Translating batch {batch_num}/{total_batches} ({len(batch)} items)...")

        try:
            translations = translate_batch(batch, client)
            all_translations.update(translations)
            print(f"  OK - Batch {batch_num} complete")
        except Exception as e:
            print(f"  ERROR in batch {batch_num}: {e}")
            print("  Continuing with next batch...")

    print(f"\n{'='*80}")
    print(f"TRANSLATION COMPLETE: {len(all_translations)}/{len(pending)} items")
    print(f"{'='*80}\n")

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
    print(f"  Saved to: {memory_file}")

    # Save translations to A-081 translations file
    a081_translations_file = "A-081_translations.json"
    with open(a081_translations_file, 'w', encoding='utf-8') as f:
        json.dump(all_translations, f, ensure_ascii=False, indent=2)
    print(f"  Saved to: {a081_translations_file}")

    # Show some example translations
    print(f"\nExample translations (first 5):")
    for i, (hash_key, translation) in enumerate(list(all_translations.items())[:5]):
        original = pending[hash_key]
        print(f"\n  {i+1}. FR: {original[:60]}")
        print(f"     EN: {translation[:60]}")

    print("\n" + "="*80)
    print("TRANSLATIONS READY FOR PDF APPLICATION")
    print("="*80)

if __name__ == "__main__":
    main()
