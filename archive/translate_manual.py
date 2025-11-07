#!/usr/bin/env python3
import json
import os
from anthropic import Anthropic

# Read the input file
with open(r'c:\Users\yichao\Documents\pdfTranslate\A-001_pending_translations.json', 'r', encoding='utf-8') as f:
    pending_data = json.load(f)

# Initialize Anthropic client - will use ANTHROPIC_API_KEY environment variable
client = Anthropic()

# Prepare data for translation
items_to_translate = list(pending_data.items())
total_items = len(items_to_translate)
translations = {}

print(f"Starting translation of {total_items} French architectural terms...")

# Process in batches
batch_size = 40
for batch_start in range(0, total_items, batch_size):
    batch_end = min(batch_start + batch_size, total_items)
    batch = items_to_translate[batch_start:batch_end]

    # Create a formatted list for translation
    french_terms = [f"{i+1}. {text}" for i, (_, text) in enumerate(batch)]
    terms_str = "\n".join(french_terms)

    # Call Claude to translate the batch
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"""You are a professional French to English translator specializing in architectural and construction terminology.

Translate the following French architectural terms to English. Be precise and professional.

For each numbered item, provide ONLY the English translation. Format your response exactly as:
1. [English translation]
2. [English translation]
etc.

Do not include the French text in your response, only the numbered English translations.

French terms:
{terms_str}"""
            }
        ]
    )

    # Parse the response
    response_text = message.content[0].text
    response_lines = response_text.strip().split('\n')

    # Extract translations
    translation_lines = []
    for line in response_lines:
        line = line.strip()
        if line and line[0].isdigit() and '.' in line:
            # Extract the translation after the number
            parts = line.split('.', 1)
            if len(parts) > 1:
                translation = parts[1].strip()
                translation_lines.append(translation)

    # Map translations to hash keys
    for i, (hash_key, _) in enumerate(batch):
        if i < len(translation_lines):
            translations[hash_key] = translation_lines[i]
            print(f"✓ Item {batch_start + i + 1}/{total_items}")
        else:
            print(f"⚠ Item {batch_start + i + 1}/{total_items} - translation missing")

    print(f"  Batch {batch_start // batch_size + 1} complete ({batch_start + 1}-{batch_end} of {total_items})")

# Write output file
output_path = r'c:\Users\yichao\Documents\pdfTranslate\A-001_translated.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(translations, f, ensure_ascii=False, indent=2)

print(f"\n✓ Translation complete!")
print(f"✓ Total items translated: {len(translations)}/{total_items}")
print(f"✓ Saved to: {output_path}")
