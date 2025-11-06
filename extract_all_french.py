"""
Extract ALL French text from original PDF
Categorize into: short text (add to dictionary) vs sentences (index for agent)
"""
import fitz
import json
import re

def should_skip(text):
    """Skip numbers, units, acronyms only"""
    if not text or not text.strip():
        return True

    # Skip if no alphabetic characters
    if not any(c.isalpha() for c in text):
        return True

    # Skip common units
    units = {'MM', 'CM', 'M', 'KG', 'LB', 'FT', 'IN', 'SQ', 'MIN', 'MAX', 'NO', 'QTY', 'TYP', 'REF'}
    if text.upper() in units:
        return True

    # Skip if just numbers with units (like "150 MM")
    if re.match(r'^[\d\s\.]+[A-Z]{1,3}$', text.upper()):
        return True

    return False

def is_sentence(text):
    """4+ words = sentence"""
    words = text.split()
    return len(words) >= 4

def bboxes_overlap(bbox1, bbox2, threshold=5):
    y_overlap = not (bbox1[3] < bbox2[1] or bbox2[3] < bbox1[1])
    if not y_overlap:
        return False
    x_gap = bbox2[0] - bbox1[2]
    return -10 <= x_gap <= threshold

# Open original French PDF
pdf_path = "A-001 - NOTES ET LÉGENDES.pdf"
print(f"Extracting ALL French text from: {pdf_path}\n")

doc = fitz.open(pdf_path)

short_texts = {}  # {french: ""} - for dictionary
sentences = {}    # {index: french} - for agent translation

for page_num in range(len(doc)):
    print(f"Processing page {page_num + 1}/{len(doc)}...")
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
                        })

    # Merge overlapping spans
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

        # Categorize
        if not should_skip(merged_text):
            if is_sentence(merged_text):
                # Sentence - index for agent
                index = len(sentences)
                sentences[index] = merged_text
                print(f"  [SENTENCE {index}] {merged_text[:60]}...")
            else:
                # Short text - add to dictionary
                short_texts[merged_text] = ""
                print(f"  [DICT] {merged_text}")

        i = j

doc.close()

print(f"\n{'='*80}")
print(f"EXTRACTION COMPLETE")
print(f"{'='*80}")
print(f"Short texts for dictionary: {len(short_texts)}")
print(f"Sentences for agent: {len(sentences)}")

# Save short texts to append to dictionary
with open('A-001_new_dictionary_entries.json', 'w', encoding='utf-8') as f:
    json.dump(short_texts, f, ensure_ascii=False, indent=2)

# Save sentences for agent translation
with open('A-001_sentences_indexed.json', 'w', encoding='utf-8') as f:
    json.dump(sentences, f, ensure_ascii=False, indent=2)

print(f"\nSaved:")
print(f"  - A-001_new_dictionary_entries.json ({len(short_texts)} entries)")
print(f"  - A-001_sentences_indexed.json ({len(sentences)} sentences)")
print(f"\nNext steps:")
print(f"1. Translate A-001_new_dictionary_entries.json manually or with agent")
print(f"2. Merge into translations.json")
print(f"3. Translate A-001_sentences_indexed.json with agent")
print(f"4. Save as A-001_sentences.json")
