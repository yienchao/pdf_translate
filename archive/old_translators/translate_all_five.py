from method9_optimized import translate_pdf_method9

pdfs = [
    ("A-001 - NOTES ET LÉGENDES.pdf", "A-001 - NOTES AND LEGENDS.pdf"),
    ("A-081 - BORDEREAU DES FINIS.pdf", "A-081 - SCHEDULE OF FINISHES.pdf"),
    ("A-302 - ÉLÉVATIONS EXTÉRIEURES.pdf", "A-302 - EXTERIOR ELEVATIONS.pdf"),
    ("A-501 - ÉLÉMENTS TYPIQUES D'ENVELOPPE.pdf", "A-501 - TYPICAL ENVELOPE ELEMENTS.pdf"),
    ("A-530 - DETAILS D'ENVELOPE (SECTION).pdf", "A-530 - ENVELOPE DETAILS (SECTION).pdf"),
]

for i, (input_name, output_name) in enumerate(pdfs, 1):
    print(f"\n{'='*80}")
    print(f"TRANSLATING {i}/5: {input_name}")
    print(f"{'='*80}")

    input_path = f"C:\\Users\\yichao\\Documents\\pdfTranslate\\{input_name}"
    output_path = f"C:\\Users\\yichao\\Documents\\pdfTranslate\\{output_name}"

    try:
        translate_pdf_method9(input_path, output_path)
        print(f"Success: {output_name}")
    except Exception as e:
        print(f"Error: {e}")

print(f"\n{'='*80}")
print("ALL 5 PDFS TRANSLATED!")
print(f"{'='*80}")
