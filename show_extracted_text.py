"""Show first 10 text elements extracted by current logic"""
import sys
sys.path.insert(0, '.')

from translate_clean import extract_text_from_pdf

pdf_path = "original/A-001 - NOTES ET LÉGENDES.pdf"
text_elements = extract_text_from_pdf(pdf_path)

print(f"Total text elements extracted: {len(text_elements)}\n")
print("="*80)
print("FIRST 10 TEXT ELEMENTS (after merging spans)")
print("="*80)

for i, elem in enumerate(text_elements[:10]):
    print(f"\n--- Element {i} ---")
    print(f"Page: {elem['page']}")
    print(f"BBox: {elem['bbox']}")
    print(f"Size: {elem['size']}")
    print(f"Word count: {len(elem['text'].split())}")
    print(f"Text: {elem['text']}")
