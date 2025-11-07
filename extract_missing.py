"""Extract text that needs translation from A-001"""
import sys
sys.path.insert(0, '.')

from translate_clean import extract_text_from_pdf, should_skip, has_french, translate_with_dict

# Extract text from A-001
pdf_path = "original/A-001 - NOTES ET LÉGENDES.pdf"
text_elements = extract_text_from_pdf(pdf_path)

print(f"Total text elements: {len(text_elements)}")

# Find elements that need translation
missing = {}
for idx, elem in enumerate(text_elements):
    text = elem["text"]
    word_count = len(text.split())

    # Skip
    if should_skip(text):
        continue

    # Try dictionary
    translated = translate_with_dict(text)
    if translated:
        continue

    # Check if French
    if has_french(text):
        if word_count <= 10:
            missing[str(idx)] = text

print(f"\nFound {len(missing)} items needing translation")
print("\nFirst 20 items:")
for i, (idx, text) in enumerate(list(missing.items())[:20]):
    print(f"  {idx}: {text}")

# Save to file
import json
with open('A-001_missing.json', 'w', encoding='utf-8') as f:
    json.dump(missing, f, ensure_ascii=False, indent=2)

print(f"\nSaved to A-001_missing.json")
