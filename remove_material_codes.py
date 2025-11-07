"""Remove faulty material code translations from dictionary"""
import json

# Load dictionary
with open('method9_data/translations.json', 'r', encoding='utf-8') as f:
    translations = json.load(f)

# Faulty entries to remove (short corrupted material codes)
faulty_keys = [
    "pbé", "bbé", "pmé", "bé", "ebé",
    "béS", "béD", "béS /", "béP /", "béS / béP /"
]

removed = []
for key in faulty_keys:
    if key in translations:
        removed.append(f"{key}: {translations[key]}")
        del translations[key]

print(f"Removed {len(removed)} faulty material code entries:")
for item in removed:
    print(f"  - {item}")

# Save cleaned dictionary
with open('method9_data/translations.json', 'w', encoding='utf-8') as f:
    json.dump(translations, f, ensure_ascii=False, indent=2)

print(f"\nDictionary cleaned: {len(translations)} entries remaining")
