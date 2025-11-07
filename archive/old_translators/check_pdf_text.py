import fitz
import os

pdfs = [
    "A-001 - LÉGENDES ET NOTES GÉNÉRALES.pdf",
    "A-014 - DÉTAILS D'ASSEMBLAGE TYPIQUES - SYSTÈMES INT. - COUPE-FEU ET_OU ACOUSTIQUE.pdf",
    "A-015 - DÉTAILS D'ASSEMBLAGE TYPES - SYSTÈMES INT. - COUPE-FEU ET_OU ACOUSTIQUE.pdf",
    "A-500 - PLANS AGRANDIS ET ÉLÉVATIONS DES WC TYPIQUES.pdf",
    "A-600 - PLANS AGRANDIS ET COUPES DES ESCALIERS D'ISSUE ET ARCHITECTURAL.pdf",
]

for pdf in pdfs:
    if os.path.exists(pdf):
        doc = fitz.open(pdf)
        page = doc[0]
        text = page.get_text()
        text_dict = page.get_text("dict")
        blocks = text_dict.get("blocks", [])
        text_blocks = [b for b in blocks if b.get("type") == 0]

        print(f"\n{pdf}:")
        print(f"  Total chars: {len(text)}")
        print(f"  Total blocks: {len(blocks)}")
        print(f"  Text blocks: {len(text_blocks)}")
        print(f"  Image blocks: {len([b for b in blocks if b.get('type') == 1])}")

        if len(text) > 0:
            print(f"  Sample: {text[:100]}")
    else:
        print(f"\n{pdf}: FILE NOT FOUND")
