"""
Translate multiple PDFs using Method 6
"""
from method6_ultimate_smart import translate_pdf_method6

# AR-001
print("\n" + "="*80)
print("TRANSLATING AR-001")
print("="*80)
translate_pdf_method6(
    r"C:\Users\yichao\Documents\pdfTranslate\AR-001 - LÉGENDES ET NOTES GÉNÉRALES.pdf",
    r"C:\Users\yichao\Documents\pdfTranslate\AR-001 - LEGENDS AND GENERAL NOTES.pdf"
)

# AR-130B4-C
print("\n" + "="*80)
print("TRANSLATING AR-130B4-C")
print("="*80)
translate_pdf_method6(
    r"C:\Users\yichao\Documents\pdfTranslate\AR-130B4-C - PAVILLON B - PLAN DE COTATIONS NIVEAU REZ-DE-JARDIN - SECTEUR B4.pdf",
    r"C:\Users\yichao\Documents\pdfTranslate\AR-130B4-C - PAVILION B - DIMENSION PLAN GROUND FLOOR LEVEL - SECTOR B4.pdf"
)

print("\n" + "="*80)
print("ALL TRANSLATIONS COMPLETE!")
print("="*80)
