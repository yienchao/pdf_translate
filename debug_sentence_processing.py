"""Debug why complete sentences appear as Frenglish"""
import sys
sys.path.insert(0, '.')

from translate_clean import extract_text_from_pdf, should_skip, translate_with_dict
import json

# Extract text from A-001
pdf_path = "original/A-001 - NOTES ET LÉGENDES.pdf"
text_elements = extract_text_from_pdf(pdf_path)

print(f"Total text elements: {len(text_elements)}\n")

# Look for the problematic sentence
search_terms = ["POSITION", "CADRES", "PORTES", "INSTALLER"]

print("=== Searching for sentence with POSITION/CADRES/PORTES/INSTALLER ===\n")
found = []
for idx, elem in enumerate(text_elements):
    text = elem["text"]
    if all(term in text.upper() for term in search_terms):
        found.append((idx, elem))
        print(f"Index {idx}: ({len(text.split())} words)")
        print(f"  Text: {text}")
        print(f"  Page: {elem['page']}")
        print()

if not found:
    print("Not found as complete sentence. Searching for fragments...\n")
    for idx, elem in enumerate(text_elements):
        text = elem["text"]
        if any(term in text.upper() for term in search_terms):
            print(f"Index {idx}: {text}")

print("\n=== Now simulating translation logic ===\n")

# Load current translations
with open('method9_data/A-001_to_translate.json', 'r', encoding='utf-8') as f:
    to_translate = json.load(f)

with open('method9_data/A-001_indexed.json', 'r', encoding='utf-8') as f:
    indexed = json.load(f)

# Build text -> translation lookup
text_to_translation = {}
for idx_str, french_text in to_translate.items():
    if idx_str in indexed:
        text_to_translation[french_text] = indexed[idx_str]

print(f"Loaded {len(text_to_translation)} text->translation mappings\n")

# Process each element as the script would
for idx, elem in enumerate(text_elements):
    text = elem["text"]

    # Skip the irrelevant ones for brevity
    if not any(term in text.upper() for term in ["POSITION", "CADRES", "SIC", "REPORT"]):
        continue

    print(f"\n--- Element {idx} ---")
    print(f"Original: {text}")
    print(f"Word count: {len(text.split())}")

    # Check if skipped
    if should_skip(text):
        print(f"  -> SKIPPED by should_skip()")
        continue

    # Check dictionary
    dict_translation = translate_with_dict(text)
    if dict_translation:
        print(f"  -> Dictionary: {dict_translation}")
        continue

    # Check indexed
    if text in text_to_translation:
        print(f"  -> Indexed: {text_to_translation[text]}")
    else:
        print(f"  -> NOT FOUND in indexed translations")
        print(f"  -> Would need translation")

print("\n=== Checking word-by-word dictionary lookups ===\n")
# Check if the sentence is being processed word by word
test_sentence = "SIC, POSITION DES CADRES OF PORTES : INSTALLER LA FACE INTERNE DU CADRE À 150 mm DU WALL"
words = test_sentence.split()
print(f"Test sentence: {test_sentence}\n")
for word in words[:15]:  # First 15 words
    cleaned = word.strip('.,;:()[]{}!?-')
    translation = translate_with_dict(cleaned)
    if translation:
        print(f"  {cleaned} -> {translation}")
    else:
        print(f"  {cleaned} -> NOT IN DICT")
