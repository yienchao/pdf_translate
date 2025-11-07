"""
Batch translate multiple PDFs with auto-growing dictionary
For 700 PDFs, this runs Method 9 on each one
"""
import os
import glob
from method9_optimized import translate_pdf_method9

# Find all French PDFs
pdf_folder = r"C:\Users\yichao\Documents\pdfTranslate"
french_pdfs = glob.glob(os.path.join(pdf_folder, "*.pdf"))

# Filter to only French PDFs (those with French words in filename)
french_indicators = ['NOTES', 'LÉGENDES', 'BORDEREAU', 'FINIS', 'DÉTAILS', 'ENVELOPPE', 'COUPE']
french_pdfs = [p for p in french_pdfs if any(indicator in os.path.basename(p) for indicator in french_indicators)]

print(f"Found {len(french_pdfs)} French PDFs to translate")

for i, pdf_path in enumerate(french_pdfs, 1):
    print(f"\n{'='*80}")
    print(f"TRANSLATING {i}/{len(french_pdfs)}: {os.path.basename(pdf_path)}")
    print(f"{'='*80}")

    # Generate output filename
    base = os.path.basename(pdf_path)
    name_without_ext = os.path.splitext(base)[0]

    # Common filename translations
    common_translations = {
        "NOTES": "NOTES",
        "LÉGENDES": "LEGENDS",
        "BORDEREAU": "SCHEDULE",
        "FINIS": "FINISHES",
        "DÉTAILS": "DETAILS",
        "ENVELOPPE": "ENVELOPE",
        "COUPE": "SECTION",
    }

    english_name = name_without_ext
    for french, english in common_translations.items():
        english_name = english_name.replace(french, english)

    output_path = os.path.join(pdf_folder, english_name + ".pdf")

    try:
        translate_pdf_method9(pdf_path, output_path)
        print(f"✓ Success: {english_name}.pdf")
    except Exception as e:
        print(f"✗ Error: {e}")
        continue

print(f"\n{'='*80}")
print(f"BATCH TRANSLATION COMPLETE!")
print(f"{'='*80}")
