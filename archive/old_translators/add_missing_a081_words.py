"""
Add missing words from A-081 screenshot
"""
import json

# Load dictionary
with open('translations.json', 'r', encoding='utf-8') as f:
    master = json.load(f)

print(f"Starting with {len(master)} translations")

# Add missing words and phrases
new_translations = {
    "Entreposage": "Storage",
    "d'embarquement": "boarding",
    "Room d'embarquement": "Boarding room",
    "Zone fauteuils roulants vestibule": "Wheelchair zone vestibule",
    "Zone fauteuils roulants rampe": "Wheelchair zone ramp",
    "fauteuils": "wheelchairs",
    "roulants": "rolling",
    "embarquement": "boarding",
    "Departure corridor": "Departure corridor",
    "Water entry room": "Water entry room"
}

before = len(master)
master.update(new_translations)

# Save
with open('translations.json', 'w', encoding='utf-8') as f:
    json.dump(master, f, ensure_ascii=False, indent=2)

print(f"Added {len(master) - before} new translations")
print(f"Total: {len(master)} translations")
