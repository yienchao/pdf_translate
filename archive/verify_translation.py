#!/usr/bin/env python3
"""Verify if the translated PDF has English text"""
import fitz

# File paths
source_pdf = r"c:\Users\yichao\Documents\pdfTranslate\A-001 - NOTES ET LÉGENDES.pdf"
output_pdf = r"c:\Users\yichao\Documents\pdfTranslate\A-001 - NOTES AND LEGENDS.pdf"

print("=" * 80)
print("COMPARING SOURCE AND TRANSLATED PDFs")
print("=" * 80)

# Extract sample text from both
source_doc = fitz.open(source_pdf)
output_doc = fitz.open(output_pdf)

source_page = source_doc[0]
output_page = output_doc[0]

source_text_dict = source_page.get_text("dict")
output_text_dict = output_page.get_text("dict")

source_blocks = source_text_dict.get("blocks", [])
output_blocks = output_text_dict.get("blocks", [])

print(f"\nSource PDF:")
print(f"  Pages: {len(source_doc)}")
print(f"  Blocks: {len(source_blocks)}")

print(f"\nOutput PDF:")
print(f"  Pages: {len(output_doc)}")
print(f"  Blocks: {len(output_blocks)}")

# Extract sample text
print(f"\nSample text from SOURCE (first 20 lines):")
print("-" * 80)

source_lines = []
for block in source_blocks[:3]:
    if block.get("type") == 0:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span.get("text", "").strip()
                if text and len(text) > 3:
                    source_lines.append(text)

for i, line in enumerate(source_lines[:20], 1):
    print(f"{i:2d}. {line[:70]}")

print(f"\nSample text from OUTPUT (first 20 lines):")
print("-" * 80)

output_lines = []
for block in output_blocks[:3]:
    if block.get("type") == 0:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span.get("text", "").strip()
                if text and len(text) > 3:
                    output_lines.append(text)

for i, line in enumerate(output_lines[:20], 1):
    print(f"{i:2d}. {line[:70]}")

# Check for English keywords
english_keywords = ["LEGENDS", "SYMBOLS", "NOTES", "GENERAL", "PARTITION", "WALL",
                   "CEILING", "EXISTING", "DOOR", "FLOOR", "WINDOW"]

print(f"\nSearching for English keywords in OUTPUT:")
print("-" * 80)

found_keywords = []
for line in output_lines:
    for keyword in english_keywords:
        if keyword in line.upper():
            if line not in found_keywords:
                found_keywords.append(line)
                break

print(f"Found {len(found_keywords)} lines with English keywords:")
for line in found_keywords[:15]:
    print(f"  - {line[:70]}")

source_doc.close()
output_doc.close()

print("\n" + "=" * 80)
print("Verification complete!")
