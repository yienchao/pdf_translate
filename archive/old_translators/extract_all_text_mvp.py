"""
MVP: Extract ALL unique text from all 5 PDFs FIRST
Then translate everything in ONE batch
"""
import fitz
import json
import re

def should_skip(text):
    """Skip numbers, units, and symbols"""
    if not text or not text.strip():
        return True
    if not any(c.isalpha() for c in text):
        return True
    units = {'MM', 'CM', 'M', 'KG', 'LB', 'FT', 'IN', 'SQ', 'MIN', 'MAX', 'NO', 'QTY', 'TYP', 'REF'}
    if text.upper() in units:
        return True
    # Skip if already English (no accented characters and common English words)
    if not any(c in text for c in 'ÀÂÆÇÉÈÊËÏÎÔÙÛÜàâæçéèêëïîôùûüÿœ'):
        common_english = ['THE', 'AND', 'OR', 'OF', 'TO', 'FOR', 'WITH', 'AT', 'BY', 'FROM', 'AS', 'ON', 'IN']
        if text.upper() in common_english:
            return True
    return False

def bboxes_overlap(bbox1, bbox2, threshold=5):
    """Check if two bounding boxes overlap"""
    y_overlap = not (bbox1[3] < bbox2[1] or bbox2[3] < bbox1[1])
    if not y_overlap:
        return False
    x_gap = bbox2[0] - bbox1[2]
    return -10 <= x_gap <= threshold

def extract_text_from_pdf(pdf_path):
    """Extract all unique text blocks from a PDF"""
    print(f"\nExtracting from: {pdf_path}")

    doc = fitz.open(pdf_path)
    all_texts = set()

    for page_num in range(len(doc)):
        page = doc[page_num]
        text_instances = page.get_text("dict")
        blocks = text_instances.get("blocks", [])

        replacements = []

        for block in blocks:
            if block.get("type") == 0:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        original_text = span.get("text", "")
                        if original_text.strip():
                            replacements.append({
                                "original": original_text,
                                "bbox": span.get("bbox"),
                                "size": span.get("size"),
                            })

        # Merge overlapping spans (same as translation logic)
        replacements.sort(key=lambda r: (round(r["bbox"][1], 1), r["bbox"][0]))

        i = 0
        while i < len(replacements):
            current = replacements[i]
            merged_text = current["original"]
            bbox = list(current["bbox"])

            j = i + 1
            while j < len(replacements):
                next_span = replacements[j]
                if bboxes_overlap(bbox, next_span["bbox"]):
                    x_gap = next_span["bbox"][0] - bbox[2]
                    if x_gap > 1:
                        merged_text += " " + next_span["original"]
                    else:
                        merged_text += next_span["original"]

                    bbox[2] = max(bbox[2], next_span["bbox"][2])
                    bbox[3] = max(bbox[3], next_span["bbox"][3])
                    j += 1
                else:
                    break

            # Add to set if not skippable
            if not should_skip(merged_text):
                all_texts.add(merged_text)

            i = j

    doc.close()
    print(f"  Found {len(all_texts)} unique text blocks")
    return all_texts

# List of 5 PDFs (French versions)
pdfs = [
    "A-001 - NOTES ET LÉGENDES.pdf",
    "A-081 - BORDEREAU DES FINIS.pdf",
    "A-302 - ÉLÉVATIONS EXTÉRIEURES.pdf",
    "A-501 - ÉLÉMENTS TYPIQUES D'ENVELOPPE.pdf",
]

# Try to find A-530 French version with different possible names
import os
pdf_dir = "C:\\Users\\yichao\\Documents\\pdfTranslate"
for filename in os.listdir(pdf_dir):
    if filename.startswith("A-530") and "DETAIL" in filename.upper() and filename.endswith(".pdf"):
        # Check if it's French (has accents or French words)
        if any(c in filename for c in "ÀÂÆÇÉÈÊËÏÎÔÙÛÜ") or "DÉTAILS" in filename:
            pdfs.append(filename)
            break
        # Also check the actual name from translate_all_five.py
        if filename == "A-530 - DETAILS D'ENVELOPE (SECTION).pdf":
            pdfs.append(filename)
            break

print("="*80)
print("MVP: EXTRACTING ALL TEXT FROM ALL 5 PDFs")
print("="*80)

all_unique_texts = set()

for pdf_name in pdfs:
    pdf_path = f"C:\\Users\\yichao\\Documents\\pdfTranslate\\{pdf_name}"
    texts = extract_text_from_pdf(pdf_path)
    all_unique_texts.update(texts)

print(f"\n{'='*80}")
print(f"TOTAL UNIQUE TEXT BLOCKS ACROSS ALL 5 PDFs: {len(all_unique_texts)}")
print(f"{'='*80}")

# Create dictionary template for translation
translation_dict = {}
for text in sorted(all_unique_texts):
    translation_dict[text] = ""

# Save to file for agent translation
with open('all_texts_to_translate.json', 'w', encoding='utf-8') as f:
    json.dump(translation_dict, f, ensure_ascii=False, indent=2)

print(f"\nSaved to: all_texts_to_translate.json")
print(f"\nNext step: Use Task agent to translate all_texts_to_translate.json")
print("Then these translations will become the master dictionary!")

# Show sample of what needs translation
sample = list(sorted(all_unique_texts))[:20]
print(f"\nSample texts to translate (first 20):")
for i, text in enumerate(sample, 1):
    print(f"  {i}. {text[:80]}")
