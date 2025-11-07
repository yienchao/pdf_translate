#!/usr/bin/env python3
"""Debug script to extract and inspect text from A-001 PDF"""
import fitz
import json
import hashlib
from pathlib import Path

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
print(f"Opening PDF: {source_pdf}")
doc = fitz.open(source_pdf)

print(f"PDF has {len(doc)} pages\n")

# Extract text from first page
page = doc[0]
text_dict = page.get_text("dict")
blocks = text_dict.get("blocks", [])

print("=" * 80)
print("TEXT ELEMENTS ON PAGE 1")
print("=" * 80)

all_text = []
for block in blocks:
    if block.get("type") == 0:  # Text block
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                original_text = span.get("text", "")
                if original_text.strip():
                    text_hash = get_text_hash(original_text)
                    has_translation = text_hash in translations
                    all_text.append({
                        "text": original_text,
                        "hash": text_hash,
                        "has_translation": has_translation,
                        "translation": translations.get(text_hash, "N/A")
                    })

# Print all text
print(f"\nTotal text elements: {len(all_text)}\n")

# Separate translated and untranslated
translated = [t for t in all_text if t["has_translation"]]
untranslated = [t for t in all_text if not t["has_translation"]]

print(f"\nTRANSLATED TEXT ({len(translated)}):")
print("-" * 80)
for item in translated:
    print(f"Original: {item['text']}")
    print(f"Translation: {item['translation']}")
    print()

print(f"\nUNTRANSLATED TEXT ({len(untranslated)}):")
print("-" * 80)
for item in untranslated:
    print(f"Text: {item['text']}")
    print(f"Hash: {item['hash']}")
    print()

# Check first few translation hashes from the file
print("\nSample translation hashes from JSON:")
print("-" * 80)
for i, (hash_key, translation) in enumerate(list(translations.items())[:5]):
    print(f"Hash: {hash_key}")
    print(f"Translation: {translation}")
    print()

doc.close()
