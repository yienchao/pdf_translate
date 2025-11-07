"""Check what Element 19 actually is in the ORIGINAL PDF"""
import sys
sys.path.insert(0, '.')
import fitz

pdf_path = "original/A-001 - NOTES ET LÉGENDES.pdf"
doc = fitz.open(pdf_path)

# Extract raw text from the specific bbox of Element 19
# From previous output: BBox around element 19
# Let me extract it properly

from translate_clean import extract_text_from_pdf

text_elements = extract_text_from_pdf(pdf_path)

elem = text_elements[19]

print("="*80)
print("ELEMENT 19 - RAW FROM ORIGINAL PDF")
print("="*80)
print(f"Text extracted: {elem['text']}")
print(f"BBox: {elem['bbox']}")
print(f"Page: {elem['page']}")
print(f"Word count: {len(elem['text'].split())}")

# Now extract raw text at that exact location using PyMuPDF
page = doc[elem['page']]
bbox_rect = fitz.Rect(elem['bbox'])

# Get text at that specific area
raw_text = page.get_text("text", clip=bbox_rect)
print(f"\nRaw text from bbox: {raw_text.strip()}")

# Get detailed text with spans
blocks = page.get_text("dict", clip=bbox_rect)["blocks"]
print(f"\nDetailed blocks at this location:")
for block in blocks:
    if block.get("type") == 0:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                print(f"  Span: '{span.get('text', '')}'")

doc.close()
