#!/usr/bin/env python3
"""Advanced verification - extract text with rawtext to see all text objects"""
import fitz
import re

output_pdf = r"c:\Users\yichao\Documents\pdfTranslate\A-001 - NOTES AND LEGENDS.pdf"

print("=" * 80)
print("ADVANCED PDF VERIFICATION")
print("=" * 80)

doc = fitz.open(output_pdf)
page = doc[0]

# Get raw text
raw_text = page.get_text()

print(f"\nFirst 3000 characters of extracted text:\n")
print(raw_text[:3000])

# Look for English keywords
english_keywords = ["LEGEND", "SYMBOL", "NOTE", "GENERAL", "PARTITION", "WALL",
                   "CEILING", "EXISTING", "DOOR", "FLOOR", "WINDOW", "SHEET",
                   "SEE", "ENGINEERING", "DOCUMENTS", "ROOFING", "STAIRS", "ELECTRICAL"]

print("\n" + "=" * 80)
print("ENGLISH KEYWORDS FOUND:")
print("=" * 80)

found = []
for keyword in english_keywords:
    if keyword in raw_text.upper():
        # Find context around keyword
        idx = raw_text.upper().find(keyword)
        context_start = max(0, idx - 40)
        context_end = min(len(raw_text), idx + len(keyword) + 40)
        context = raw_text[context_start:context_end].replace('\n', ' ')
        found.append((keyword, context))

if found:
    print(f"\nFound {len(found)} English keywords:")
    for keyword, context in found[:20]:
        print(f"\n{keyword}:")
        print(f"  ...{context}...")
else:
    print("\nNo English keywords found!")

# Check for French indicators still present
print("\n" + "=" * 80)
print("FRENCH TEXT INDICATORS:")
print("=" * 80)

french_words = ["GÉNÉRAL", "LÉGENDE", "NOTES", "CLOISON", "MURAL", "ESCALIER", "CÂBLE"]
french_found = []

for word in french_words:
    if word in raw_text.upper():
        french_found.append(word)
        print(f"  ✓ Found French: {word}")

if not french_found:
    print("  No French words found!")
else:
    print(f"\nTotal French words found: {len(french_found)}")

doc.close()
