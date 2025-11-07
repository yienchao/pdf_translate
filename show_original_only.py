"""Show ONLY original text from PDF - NO translations"""
import sys
sys.path.insert(0, '.')

from translate_clean import extract_text_from_pdf

pdf_path = "original/A-001 - NOTES ET LÉGENDES.pdf"
text_elements = extract_text_from_pdf(pdf_path)

print("="*80)
print("ELEMENTS 10-20 - ORIGINAL TEXT FROM PDF ONLY")
print("="*80)

for i in range(10, 20):
    elem = text_elements[i]
    text = elem['text']
    word_count = len(text.split())

    print(f"\n--- Element {i} ---")
    print(f"Word count: {word_count}")
    print(f"Original text: {text}")
