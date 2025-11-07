"""Translate pending items using Claude API"""
import json
import sys
import os
from anthropic import Anthropic

# Get pending file from command line or use default
pending_file = sys.argv[1] if len(sys.argv) > 1 else 'A-001_pending_translations.json'

# Load pending
print(f"Loading pending translations from: {pending_file}")
with open(pending_file, 'r', encoding='utf-8') as f:
    pending = json.load(f)

# Load existing translation memory
try:
    with open('translation_memory.json', 'r', encoding='utf-8') as f:
        memory = json.load(f)
    print(f"Loaded existing translation memory: {len(memory)} translations")
except:
    memory = {}
    print("Starting fresh translation memory")

# Initialize Claude client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

print(f"\nTranslating {len(pending)} items using Claude API...")
print("=" * 80)

# Translate each item
count = 0
for hash_key, french_text in pending.items():
    count += 1

    # Keep acronyms as-is
    if french_text in ['SIC', 'DRF', 'FVX', 'MAO', 'TIC', 'YUL', 'ADM', 'béS', 'béD']:
        memory[hash_key] = french_text
        print(f"[{count}/{len(pending)}] ACRONYM: {french_text} -> {french_text}")
        continue

    # Translate with Claude
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": f"""Translate this French architectural/airport text to English.

Rules:
- Keep technical acronyms as-is: SIC, DRF, FVX, MAO, TIC, YUL, ADM, DOM, INTL, ASFC
- Keep codes like "cc1.1", "béS", "béD" unchanged
- Keep numbers, dates, dimensions unchanged
- Keep (spécifier) as (specify)
- Be concise and professional
- Return ONLY the English translation, no explanations

French text: {french_text}

English:"""
            }]
        )

        english = response.content[0].text.strip()
        memory[hash_key] = english

        # Show progress
        print(f"[{count}/{len(pending)}] {french_text[:50]:50} -> {english[:50]}")

    except Exception as e:
        print(f"[{count}/{len(pending)}] ERROR: {french_text[:50]} - {e}")
        # Fallback: keep original
        memory[hash_key] = french_text

# Save translation memory
with open('translation_memory.json', 'w', encoding='utf-8') as f:
    json.dump(memory, f, ensure_ascii=False, indent=2)

print("=" * 80)
print(f"Translation complete!")
print(f"Total translations in memory: {len(memory)}")
print(f"Saved to: translation_memory.json")
