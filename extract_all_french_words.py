"""Extract ALL French words not in dictionary from A-001"""
import sys
sys.path.insert(0, '.')

from translate_clean import extract_text_from_pdf, should_skip, translate_with_dict, has_french, TRANSLATION_DICT

pdf_path = "original/A-001 - NOTES ET LÉGENDES.pdf"
text_elements = extract_text_from_pdf(pdf_path)

# Find all French words not in dictionary
missing_words = set()

for elem in text_elements:
    text = elem["text"]

    if should_skip(text):
        continue

    # Check if in dictionary
    if translate_with_dict(text):
        continue

    # Check if French
    if has_french(text):
        # Add each word if it's short (1-3 words)
        if len(text.split()) <= 3:
            missing_words.add(text)

print(f"Found {len(missing_words)} French words/phrases not in dictionary\n")

# Sort by length
sorted_words = sorted(missing_words, key=lambda x: (len(x.split()), x))

print("=== Single words ===")
singles = [w for w in sorted_words if len(w.split()) == 1]
print(", ".join(singles[:50]))

print("\n\n=== 2-word phrases ===")
twos = [w for w in sorted_words if len(w.split()) == 2]
for w in twos[:30]:
    print(f"  {w}")

print(f"\n\nTotal: {len(singles)} single words, {len(twos)} 2-word phrases")

# Save to file
import json
output = {w: "" for w in sorted_words if len(w.split()) <= 2}
with open('A-001_missing_words.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nSaved {len(output)} items to A-001_missing_words.json")
