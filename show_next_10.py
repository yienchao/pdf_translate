"""Show next 10 text elements (10-20) and classify them"""
import sys
sys.path.insert(0, '.')
import os
import json

from translate_clean import extract_text_from_pdf, should_skip, translate_with_dict

pdf_path = "original/A-001 - NOTES ET LÉGENDES.pdf"
text_elements = extract_text_from_pdf(pdf_path)

# Load indexed translations to check
indexed_file = "method9_data/A-001_indexed.json"
to_translate_file = "method9_data/A-001_to_translate.json"

indexed = {}
to_translate = {}
if os.path.exists(indexed_file):
    with open(indexed_file, 'r', encoding='utf-8') as f:
        indexed = json.load(f)
if os.path.exists(to_translate_file):
    with open(to_translate_file, 'r', encoding='utf-8') as f:
        to_translate = json.load(f)

print("="*80)
print("ELEMENTS 10-20 (and their classification)")
print("="*80)

for i in range(10, 20):
    elem = text_elements[i]
    text = elem['text']
    word_count = len(text.split())

    print(f"\n--- Element {i} ---")
    print(f"Text: {text}")
    print(f"Word count: {word_count}")

    # Classify
    if should_skip(text):
        print(f"Classification: SKIP (should_skip = True)")
    else:
        dict_trans = translate_with_dict(text)
        if dict_trans:
            print(f"Classification: DICTIONARY")
            print(f"  Translation: {dict_trans}")
        elif word_count <= 10:
            print(f"Classification: NEEDS DICTIONARY (≤10 words, not in dict)")
            # Check if in to_translate
            if str(i) in to_translate:
                print(f"  -> In to_translate.json")
                if str(i) in indexed:
                    print(f"  -> Has indexed translation: {indexed[str(i)]}")
        else:
            print(f"Classification: NEEDS INDEXED (11+ words)")
            # Check if in to_translate
            if str(i) in to_translate:
                print(f"  -> In to_translate.json")
                if str(i) in indexed:
                    print(f"  -> Has indexed translation: {indexed[str(i)]}")
