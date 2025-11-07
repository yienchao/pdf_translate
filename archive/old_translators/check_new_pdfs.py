import fitz

pdfs = [
    "A-001 - NOTES ET LÉGENDES.pdf",
    "A-081 - BORDEREAU DES FINIS.pdf",
    "A-530 - DÉTAILS D'ENVELOPPE (COUPE).pdf",
]

for pdf in pdfs:
    doc = fitz.open(pdf)
    page = doc[0]
    text = page.get_text()
    text_dict = page.get_text("dict")
    blocks = text_dict.get("blocks", [])
    text_blocks = [b for b in blocks if b.get("type") == 0]

    print(f"\n{pdf}:")
    print(f"  Total chars: {len(text)}")
    print(f"  Text blocks: {len(text_blocks)}")
    print(f"  Image blocks: {len([b for b in blocks if b.get('type') == 1])}")

    if len(text) > 0:
        print(f"  HAS TEXT - Can translate!")
        print(f"  Sample: {text[:150]}")
    else:
        print(f"  NO TEXT - Image-only PDF")
