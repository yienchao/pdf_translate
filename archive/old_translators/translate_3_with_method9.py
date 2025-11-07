from method9_optimized import translate_pdf_method9

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

    translate_pdf_method9(input_path, output_path)

print(f"\n{'='*80}")
print("ALL 3 PDFS TRANSLATED!")
print(f"{'='*80}")
