"""
Add complete phrases that appear in A-081
"""
import json

# Load dictionary
with open('translations.json', 'r', encoding='utf-8') as f:
    master = json.load(f)

print(f"Starting with {len(master)} translations")

# Add complete phrases as they appear in the PDF
new_phrases = {
    # Complete room names
    "Zone fauteuils roulants vestibule - DOM": "Wheelchair zone vestibule - DOM",
    "Zone fauteuils roulants rampe": "Wheelchair zone ramp",
    "Zone fauteuils roulants vestibule - INTL": "Wheelchair zone vestibule - INTL",
    "Room d'embarquement - DOM": "Boarding room - DOM",
    "Room d'embarquement - INTL": "Boarding room - INTL",

    # Individual words that are missing
    "fauteuils": "wheelchair",
    "roulants": "rolling"
}

before = len(master)
master.update(new_phrases)

# Save
with open('translations.json', 'w', encoding='utf-8') as f:
    json.dump(master, f, ensure_ascii=False, indent=2)

print(f"Added {len(master) - before} new translations")
print(f"Total: {len(master)} translations")
print("\nAdded phrases:")
for k, v in new_phrases.items():
    print(f"  {k} -> {v}")
