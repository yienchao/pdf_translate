"""Show next 50 text elements (51-100) and classify them"""
import sys
sys.path.insert(0, '.')

from translate_clean import extract_text_from_pdf, should_skip

pdf_path = "original/A-001 - NOTES ET LÉGENDES.pdf"
text_elements = extract_text_from_pdf(pdf_path)

print("="*80)
print("ELEMENTS 51-100 - ORIGINAL TEXT + CLASSIFICATION")
print("="*80)

for i in range(51, 101):
    elem = text_elements[i]
    text = elem['text']
    word_count = len(text.split())

    # Determine classification based on current logic
    if should_skip(text):
        classification = "SKIP"
    elif word_count <= 10:
        classification = "DICT"
    else:
        classification = "INDEXED"

    print(f"{i:3d} | {classification:7s} | {word_count:2d} words | {text[:80]}")
