"""Test translation on 3 specific PDFs"""
import sys
sys.path.insert(0, '.')

from translate_clean import process_pdf

# Test PDFs
test_pdfs = [
    ("original/A-001 - NOTES ET LÉGENDES.pdf", "translated_pdfs/A-001 - NOTES AND LEGENDS.pdf"),
    ("original/A-062 - DÉTAILS PORTES ET CADRES.pdf", "translated_pdfs/A-062 - DETAILS DOORS AND FRAMES.pdf"),
    ("original/A-063 - BORDEREAU DES PORTES, CADRES ET OUVERTURES.pdf", "translated_pdfs/A-063 - SCHEDULE.pdf"),
]

print("Testing improved skip logic on 3 PDFs...\n")

for input_pdf, output_pdf in test_pdfs:
    print(f"\nProcessing: {input_pdf}")
    success = process_pdf(input_pdf, output_pdf)
    if not success:
        print(f"FAILED: {input_pdf}")
        break

print("\n" + "="*80)
print("TEST COMPLETE!")
print("="*80)
