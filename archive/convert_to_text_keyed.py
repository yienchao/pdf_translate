"""Convert numeric-indexed translations to text-keyed format"""
import json
import sys

if len(sys.argv) < 4:
    print("Usage: python convert_to_text_keyed.py <french_indexed.json> <english_indexed.json> <output.json>")
    sys.exit(1)

french_file = sys.argv[1]
english_file = sys.argv[2]
output_file = sys.argv[3]

# Load both files
with open(french_file, 'r', encoding='utf-8') as f:
    french = json.load(f)

with open(english_file, 'r', encoding='utf-8') as f:
    english = json.load(f)

# Convert to text-keyed format
text_keyed = {}
for idx, french_text in french.items():
    if idx in english:
        text_keyed[french_text] = english[idx]
    else:
        print(f"Warning: No English translation for index {idx}")
        text_keyed[french_text] = french_text  # Keep French as fallback

# Save
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(text_keyed, f, ensure_ascii=False, indent=2)

print(f"Converted {len(text_keyed)} entries")
print(f"Saved to: {output_file}")
