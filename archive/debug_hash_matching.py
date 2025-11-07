#!/usr/bin/env python3
"""Debug hash matching between PDF text and translations"""
import fitz
import json
import hashlib

def get_text_hash(text):
    """Generate a hash for text to match translations"""
    return hashlib.sha256(text.strip().encode()).hexdigest()

# File paths
source_pdf = r"c:\Users\yichao\Documents\pdfTranslate\A-001 - NOTES ET LÉGENDES.pdf"
translations_json = r"c:\Users\yichao\Documents\pdfTranslate\A-001_translations.json"

# Load translations
print("Loading translations...")
with open(translations_json, 'r', encoding='utf-8') as f:
    translations = json.load(f)

print(f"Loaded {len(translations)} translations\n")

# Open PDF
doc = fitz.open(source_pdf)
page = doc[0]

# Extract just a few text elements for debugging
text_dict = page.get_text("dict")
blocks = text_dict.get("blocks", [])

print("=" * 100)
print("DETAILED HASH MATCHING DEBUG")
print("=" * 100)

found_matches = 0
tested = 0

for block in blocks:
    if block.get("type") == 0:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                original_text = span.get("text", "")
                if not original_text.strip() or len(original_text.strip()) < 5:
                    continue

                tested += 1
                text_hash = get_text_hash(original_text)

                # Check if this hash is in translations
                if text_hash in translations:
                    found_matches += 1
                    translation = translations[text_hash]
                    print(f"MATCH #{found_matches}:")
                    print(f"  Text: {original_text[:80]}")
                    print(f"  Hash: {text_hash}")
                    print(f"  Translation: {translation[:80]}")
                    print()

                # Sample some hashes to compare
                if tested <= 10:
                    print(f"Sample #{tested}:")
                    print(f"  Text: {original_text[:80]}")
                    print(f"  Hash: {text_hash}")
                    print(f"  In translations? {text_hash in translations}")
                    print()

print(f"\nSummary:")
print(f"  Tested: {tested}")
print(f"  Matches: {found_matches}")
print(f"  Match rate: {found_matches / tested * 100:.1f}%")

# Check if any translation hash keys look like they match the PDF text
print("\nComparing first 10 translation hashes to PDF text hashes...")
pdf_hashes = set()
for block in blocks:
    if block.get("type") == 0:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span.get("text", "")
                if text.strip():
                    pdf_hashes.add(get_text_hash(text))

trans_hashes = set(translations.keys())
matching_hashes = pdf_hashes & trans_hashes

print(f"\nHash analysis:")
print(f"  PDF text hashes: {len(pdf_hashes)}")
print(f"  Translation hashes: {len(trans_hashes)}")
print(f"  Matching hashes: {len(matching_hashes)}")
print(f"  Match rate: {len(matching_hashes) / len(pdf_hashes) * 100:.1f}%")

doc.close()
