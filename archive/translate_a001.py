#!/usr/bin/env python3
import json
import anthropic
import os

# Read the pending translations file
with open(r'c:\Users\yichao\Documents\pdfTranslate\A-001_pending_translations.json', encoding='utf-8') as f:
    pending_data = json.load(f)

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Prepare data for translation
items_to_translate = list(pending_data.items())
total_items = len(items_to_translate)
translations = {}
examples = []

print(f"Starting translation of {total_items} French architectural terms...")

# Process in batches to be efficient with API calls
batch_size = 50
for batch_start in range(0, total_items, batch_size):
    batch_end = min(batch_start + batch_size, total_items)
    batch = items_to_translate[batch_start:batch_end]

    # Create a formatted list of French terms with their hashes for the API
    french_terms = [f"{hash_key}: {text}" for hash_key, text in batch]
    terms_str = "\n".join(french_terms)

    # Call Claude to translate the batch
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4000,
        messages=[
            {
                "role": "user",
                "content": f"""You are a French to English translator specializing in architectural and construction terminology.

Translate the following French architectural terms to English. Maintain the exact same hash keys.
Return ONLY a valid JSON object with hash keys mapped to English translations.
Do not add any other text or explanation.

{terms_str}

Return as valid JSON:"""
            }
        ]
    )

    # Parse the response
    response_text = message.content[0].text

    # Try to extract JSON from response
    try:
        # Find JSON in response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            batch_translations = json.loads(json_str)
            translations.update(batch_translations)

            # Store first 3 examples
            if len(examples) < 3:
                for hash_key, text in batch:
                    if hash_key in batch_translations:
                        examples.append({
                            "hash": hash_key,
                            "french": text,
                            "english": batch_translations[hash_key]
                        })
                        if len(examples) == 3:
                            break
    except json.JSONDecodeError as e:
        print(f"Error parsing batch {batch_start}-{batch_end}: {e}")
        print(f"Response: {response_text[:200]}")

    print(f"Processed {min(batch_end, total_items)}/{total_items} items...")

# Write output file
output_path = r'c:\Users\yichao\Documents\pdfTranslate\A-001_translated.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(translations, f, ensure_ascii=False, indent=2)

print(f"\n✓ Translation complete!")
print(f"Total items translated: {len(translations)}")
print(f"\nExamples:")
for i, example in enumerate(examples, 1):
    print(f"{i}. French: {example['french']}")
    print(f"   English: {example['english']}\n")
