"""Remove Frenglish entries from translations.json"""
import json
import os

dict_path = "method9_data/translations.json"

# Load current dictionary
with open(dict_path, 'r', encoding='utf-8') as f:
    translations = json.load(f)

print(f"Original dictionary: {len(translations)} entries")

# Detect Frenglish: translation contains French words mixed with English
# French indicators: DE, DES, LES, ET, OU, LA, LE, DANS, SUR, POUR, AVEC, etc.
# English indicators: OF, THE, AND, OR, IN, ON, FOR, WITH, etc.

french_words = {'DE', 'DES', 'LES', 'ET', 'OU', 'LA', 'LE', 'DANS', 'SUR', 'POUR',
                'AVEC', 'SONT', 'EST', 'AU', 'AUX', 'DU', 'À', 'PAR', 'ENTRE'}
english_words = {'OF', 'THE', 'AND', 'OR', 'IN', 'ON', 'FOR', 'WITH', 'ARE', 'IS',
                 'AT', 'BY', 'BETWEEN', 'TO', 'FROM'}

frenglish_entries = {}
clean_entries = {}

for french, english in translations.items():
    # Check if translation has both French and English words
    translation_words = set(english.upper().split())

    has_french = bool(translation_words & french_words)
    has_english = bool(translation_words & english_words)

    # Frenglish = mix of both
    if has_french and has_english:
        frenglish_entries[french] = english
    else:
        clean_entries[french] = english

print(f"\nFound {len(frenglish_entries)} Frenglish entries to remove:")
for i, (k, v) in enumerate(list(frenglish_entries.items())[:10]):
    print(f"  {k[:60]} -> {v[:60]}")
if len(frenglish_entries) > 10:
    print(f"  ... and {len(frenglish_entries) - 10} more")

print(f"\nClean dictionary: {len(clean_entries)} entries")

# Backup original
backup_path = dict_path.replace('.json', '_backup.json')
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump(translations, f, ensure_ascii=False, indent=2)
print(f"\nBackup saved to: {backup_path}")

# Save cleaned dictionary
with open(dict_path, 'w', encoding='utf-8') as f:
    json.dump(clean_entries, f, ensure_ascii=False, indent=2)
print(f"Cleaned dictionary saved: {dict_path}")

# Save removed entries for review
removed_path = "method9_data/frenglish_removed.json"
with open(removed_path, 'w', encoding='utf-8') as f:
    json.dump(frenglish_entries, f, ensure_ascii=False, indent=2)
print(f"Removed entries saved to: {removed_path}")
