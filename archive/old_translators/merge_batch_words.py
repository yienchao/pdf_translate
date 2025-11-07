"""
Merge batch-translated words into main dictionary
"""
import json

# Load dictionary
with open('translations.json', 'r', encoding='utf-8') as f:
    master = json.load(f)

print(f"Starting with {len(master)} translations")

# Load batch translations
with open('batch_words_to_translate.json', 'r', encoding='utf-8') as f:
    batch_words = json.load(f)

# Check if translations are complete
empty = [k for k, v in batch_words.items() if not v]
if empty:
    print(f"\nWARNING: {len(empty)} words still need translation!")
    print("Please fill in translations before merging.")
    exit(1)

# Merge
before = len(master)
master.update(batch_words)
after = len(master)

# Save
with open('translations.json', 'w', encoding='utf-8') as f:
    json.dump(master, f, ensure_ascii=False, indent=2)

print(f"Added {after - before} new translations")
print(f"Total: {len(master)} translations")
print("\nDictionary updated!")
