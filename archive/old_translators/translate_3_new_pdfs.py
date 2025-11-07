"""
Translate the 3 new PDFs with Method 8
"""
from method8_overlap_fix import translate_pdf_method8

pdfs = [
    ("A-001 - NOTES ET LÉGENDES.pdf", "A-001 - NOTES AND LEGENDS.pdf"),
    ("A-081 - BORDEREAU DES FINIS.pdf", "A-081 - SCHEDULE OF FINISHES.pdf"),
    ("A-530 - DÉTAILS D'ENVELOPPE (COUPE).pdf", "A-530 - ENVELOPE DETAILS (SECTION).pdf"),
]

for i, (input_name, output_name) in enumerate(pdfs, 1):
    print(f"\n{'='*80}")
    print(f"TRANSLATING {i}/3: {input_name}")
    print(f"{'='*80}")

    input_path = f"C:\\Users\\yichao\\Documents\\pdfTranslate\\{input_name}"
    output_path = f"C:\\Users\\yichao\\Documents\\pdfTranslate\\{output_name}"

    try:
        translate_pdf_method8(input_path, output_path)
        print(f"[OK] Successfully translated: {output_name}")
    except Exception as e:
        print(f"[ERROR] Error translating {input_name}: {e}")

print(f"\n{'='*80}")
print("ALL 3 PDFS TRANSLATED!")
print(f"{'='*80}")
