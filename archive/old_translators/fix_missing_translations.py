"""
Fix missing translations by adding corrupted character variants
"""
import json

# Load existing translations
with open('translations.json', 'r', encoding='utf-8') as f:
    translations = json.load(f)

# Add the two missing translations with corrupted characters as they appear in PDF
missing = {
    "APPEL D�OFFRES � LOT F0740B -": "CALL FOR TENDERS – LOT F0740B -",
    "FR-X = �L�VATION TYPE FONTAINE D�EAU, SE R�F�RER �": "FR-X = ELEVATION TYPE WATER FOUNTAIN, REFER TO"
}

# Add missing translations
for french, english in missing.items():
    translations[french] = english
    print(f"Added: '{french}' -> '{english}'")

# Save updated translations
with open('translations.json', 'w', encoding='utf-8') as f:
    json.dump(translations, f, ensure_ascii=False, indent=2)

print(f"\nTotal translations: {len(translations)}")
print("Translations file updated!")
