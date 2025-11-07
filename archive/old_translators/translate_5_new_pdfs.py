"""
Translate the 5 new PDFs with Method 8
"""
from method8_overlap_fix import translate_pdf_method8

pdfs = [
    ("A-001 - LÉGENDES ET NOTES GÉNÉRALES.pdf", "A-001 - LEGENDS AND GENERAL NOTES.pdf"),
    ("A-014 - DÉTAILS D'ASSEMBLAGE TYPIQUES - SYSTÈMES INT. - COUPE-FEU ET_OU ACOUSTIQUE.pdf",
     "A-014 - TYPICAL ASSEMBLY DETAILS - INT. SYSTEMS - FIRE AND_OR ACOUSTIC.pdf"),
    ("A-015 - DÉTAILS D'ASSEMBLAGE TYPES - SYSTÈMES INT. - COUPE-FEU ET_OU ACOUSTIQUE.pdf",
     "A-015 - TYPICAL ASSEMBLY DETAILS - INT. SYSTEMS - FIRE AND_OR ACOUSTIC.pdf"),
    ("A-500 - PLANS AGRANDIS ET ÉLÉVATIONS DES WC TYPIQUES.pdf",
     "A-500 - ENLARGED PLANS AND ELEVATIONS OF TYPICAL WC.pdf"),
    ("A-600 - PLANS AGRANDIS ET COUPES DES ESCALIERS D'ISSUE ET ARCHITECTURAL.pdf",
     "A-600 - ENLARGED PLANS AND SECTIONS OF EXIT AND ARCHITECTURAL STAIRS.pdf"),
]

for i, (input_name, output_name) in enumerate(pdfs, 1):
    print(f"\n{'='*80}")
    print(f"TRANSLATING {i}/5: {input_name}")
    print(f"{'='*80}")

    input_path = f"C:\\Users\\yichao\\Documents\\pdfTranslate\\{input_name}"
    output_path = f"C:\\Users\\yichao\\Documents\\pdfTranslate\\{output_name}"

    try:
        translate_pdf_method8(input_path, output_path)
        print(f"[OK] Successfully translated: {output_name}")
    except Exception as e:
        print(f"[ERROR] Error translating {input_name}: {e}")

print(f"\n{'='*80}")
print("ALL 5 PDFS TRANSLATED!")
print(f"{'='*80}")
