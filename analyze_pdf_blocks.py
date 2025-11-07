"""Analyze how PyMuPDF groups text into blocks"""
import fitz

pdf_path = "original/A-001 - NOTES ET LÉGENDES.pdf"
doc = fitz.open(pdf_path)

# Look at first page
page = doc[0]
blocks = page.get_text("dict")["blocks"]

print(f"Total blocks on page 1: {len(blocks)}\n")

# Show structure of first 10 text blocks
text_blocks = [b for b in blocks if b.get("type") == 0]
print(f"Text blocks: {len(text_blocks)}\n")

for i, block in enumerate(text_blocks[:10]):
    print(f"=== Block {i} ===")
    print(f"BBox: {block['bbox']}")
    print(f"Lines in block: {len(block.get('lines', []))}")

    # Collect all text in this block
    block_text = []
    for line in block.get("lines", []):
        line_text = []
        for span in line.get("spans", []):
            line_text.append(span.get("text", ""))
        block_text.append("".join(line_text))

    # Show full block text
    full_text = "\n".join(block_text)
    print(f"Text:\n{full_text}")
    print(f"Word count: {len(full_text.split())}")
    print()

doc.close()

print("\n" + "="*80)
print("KEY INSIGHT:")
print("PyMuPDF 'blocks' are natural textboxes/paragraphs!")
print("We should merge text at BLOCK level, not just span level!")
print("="*80)
