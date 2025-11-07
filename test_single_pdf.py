"""Test translation on a single PDF"""
import sys
sys.path.insert(0, '.')

from translate_clean import process_pdf

# Test on A-063
input_pdf = "original/A-063 - BORDEREAU DES PORTES, CADRES ET OUVERTURES.pdf"
output_pdf = "translated_pdfs/A-063 - SCHEDULE TEST.pdf"

print("Testing improved skip logic on A-063...")
success = process_pdf(input_pdf, output_pdf)
print(f"\nTest complete: {'SUCCESS' if success else 'FAILED'}")
