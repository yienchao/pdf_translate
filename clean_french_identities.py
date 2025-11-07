"""Remove French identity mappings (French=French) from dictionary"""
import json

dict_path = "method9_data/translations.json"

# Load current dictionary
with open(dict_path, 'r', encoding='utf-8') as f:
    translations = json.load(f)

print(f"Original dictionary: {len(translations)} entries")

# French-specific words that indicate text is French, not English
french_indicators = {
    'salle', 'embarquement', 'entreposage', 'fauteuils', 'roulants',
    'allaitement', 'vestiaire', 'local', 'niveau', 'façade',
    'électrique', 'mécanique', 'éclairage', 'plafond', 'plancher',
    'cloison', 'dalle', 'mur', 'porte', 'fenêtre', 'toiture',
    'revêtement', 'isolant', 'étanche', 'menuiserie', 'quincaillerie',
    'vestibule', 'corridor', 'bureau', 'cuisine', 'toilette',
    'ascenseur', 'escalier', 'rampe', 'sortie', 'entrée',
    'chambre', 'salon', 'salle', 'pièce', 'local',
    'est', 'sont', 'doit', 'doivent', 'peut', 'peuvent',
    'tous', 'toutes', 'les', 'des', 'au', 'aux', 'du',
    'avec', 'sans', 'pour', 'dans', 'sur', 'sous', 'entre'
}

# Identify French identity mappings
french_identities = {}
keep_identities = {}
clean_translations = {}

for french, english in translations.items():
    if french == english:
        # Check if it contains French-specific words
        text_lower = french.lower()
        is_french = any(fr_word in text_lower for fr_word in french_indicators)

        if is_french:
            french_identities[french] = english
        else:
            # Keep legitimate same-language words
            keep_identities[french] = english
            clean_translations[french] = english
    else:
        # Keep normal translations
        clean_translations[french] = english

print(f"\nFound {len(french_identities)} French identity mappings to remove:")
for i, (k, v) in enumerate(list(french_identities.items())[:15]):
    print(f"  {k}")
if len(french_identities) > 15:
    print(f"  ... and {len(french_identities) - 15} more")

print(f"\nKeeping {len(keep_identities)} legitimate identities (same in both languages):")
for k in list(keep_identities.keys())[:10]:
    print(f"  {k}")
if len(keep_identities) > 10:
    print(f"  ... and {len(keep_identities) - 10} more")

print(f"\nClean dictionary: {len(clean_translations)} entries")

# Backup original
backup_path = dict_path.replace('.json', '_before_identity_clean.json')
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump(translations, f, ensure_ascii=False, indent=2)
print(f"\nBackup saved to: {backup_path}")

# Save cleaned dictionary
with open(dict_path, 'w', encoding='utf-8') as f:
    json.dump(clean_translations, f, ensure_ascii=False, indent=2)
print(f"Cleaned dictionary saved: {dict_path}")

# Save removed French identities for review
removed_path = "method9_data/french_identities_removed.json"
with open(removed_path, 'w', encoding='utf-8') as f:
    json.dump(french_identities, f, ensure_ascii=False, indent=2)
print(f"Removed French identities saved to: {removed_path}")
