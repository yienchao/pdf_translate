"""
Simple script to remove bad translations from dictionary
- Removes identity mappings (French → French)
- Keeps only real translations (French → English)
"""
import json

# Load dictionary
with open('method12_data/translations.json', 'r', encoding='utf-8') as f:
    old_dict = json.load(f)

print(f"Original dictionary: {len(old_dict)} entries")

# Keep only real translations
clean_dict = {}
removed = 0

for french, english in old_dict.items():
    # Remove if identical (not translated)
    if french == english:
        removed += 1
        continue

    # Remove if still has lots of French words
    french_words = ['VOIR', 'POUR', 'DANS', 'AVEC', 'PORTE', 'CADRE', 'BÉTON', 'PLAFOND']
    if any(word in english.upper() for word in french_words):
        # Check if it's actually still French
        if any(word in french.upper() for word in french_words):
            removed += 1
            continue

    # Keep good translation
    clean_dict[french] = english

print(f"Cleaned dictionary: {len(clean_dict)} entries")
print(f"Removed: {removed} bad translations")

# Save cleaned dictionary
with open('method12_data/translations_clean.json', 'w', encoding='utf-8') as f:
    json.dump(clean_dict, f, ensure_ascii=False, indent=2)

# Backup original
with open('method12_data/translations_backup.json', 'w', encoding='utf-8') as f:
    json.dump(old_dict, f, ensure_ascii=False, indent=2)

print("\nDone!")
print("- Backup saved: method12_data/translations_backup.json")
print("- Clean version: method12_data/translations_clean.json")
print("\nTo use: rename translations_clean.json to translations.json")
