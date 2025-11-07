"""
Collect ALL untranslated words from all 5 PDFs in one pass
"""
import fitz
import json
import re

# Load current dictionary
with open('translations.json', 'r', encoding='utf-8') as f:
    TRANSLATION_DICT = json.load(f)

# Pre-compile patterns
COMPILED_PATTERNS = []
sorted_terms = sorted(TRANSLATION_DICT.items(), key=lambda x: len(x[0]), reverse=True)
for french, english in sorted_terms:
    try:
        pattern = re.compile(r'\b' + re.escape(french) + r'\b', re.IGNORECASE)
        COMPILED_PATTERNS.append((pattern, english))
    except:
        pattern = re.compile(re.escape(french), re.IGNORECASE)
        COMPILED_PATTERNS.append((pattern, english))

def should_skip(text):
    if not text or not text.strip():
        return True
    if not any(c.isalpha() for c in text):
        return True
    units = {'MM', 'CM', 'M', 'KG', 'LB', 'FT', 'IN', 'SQ', 'MIN', 'MAX', 'NO', 'QTY'}
    if text.upper() in units:
        return True
    return False

def has_french_words(text):
    """Check if text has French words"""
    french_indicators = [
        'DE', 'ET', 'LE', 'LA', 'LES', 'DU', 'DES', 'AU', 'AUX', 'EN', 'SUR',
        'AVEC', 'POUR', 'PAR', 'DANS', 'QUI', 'QUE', 'UN', 'UNE', 'SONT', 'EST'
    ]

    words = re.findall(r'\b[A-ZÀ-ÿ]{2,}\b', text.upper())

    for word in words:
        if word in french_indicators:
            return True
        if any(c in word for c in 'ÀÂÆÇÉÈÊËÏÎÔÙÛÜàâæçéèêëïîôùûüÿœ'):
            return True

    return False

def translate_text(text):
    """Translate with dictionary"""
    if should_skip(text):
        return text

    is_upper = text.isupper()
    is_lower = text.islower()

    translated = text
    for pattern, english in COMPILED_PATTERNS:
        if pattern.search(translated):
            if is_lower:
                translated = pattern.sub(english.lower(), translated)
            elif is_upper:
                translated = pattern.sub(english.upper(), translated)
            else:
                translated = pattern.sub(english, translated)

    return translated

def bboxes_overlap(bbox1, bbox2, threshold=5):
    y_overlap = not (bbox1[3] < bbox2[1] or bbox2[3] < bbox1[1])
    if not y_overlap:
        return False
    x_gap = bbox2[0] - bbox1[2]
    return -10 <= x_gap <= threshold

pdfs = [
    "A-001 - NOTES ET LÉGENDES.pdf",
    "A-081 - BORDEREAU DES FINIS.pdf",
    "A-302 - ÉLÉVATIONS EXTÉRIEURES.pdf",
    "A-501 - ÉLÉMENTS TYPIQUES D'ENVELOPPE.pdf",
    "A-530 - DETAILS D'ENVELOPE (SECTION).pdf",
]

all_untranslated = {}

print("="*80)
print("COLLECTING ALL UNTRANSLATED TEXTS FROM 5 PDFs")
print("="*80)

for pdf_name in pdfs:
    pdf_path = f"C:\\Users\\yichao\\Documents\\pdfTranslate\\{pdf_name}"
    print(f"\nChecking: {pdf_name}")

    try:
        doc = fitz.open(pdf_path)

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
                                })

            # Merge overlapping
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

                # Translate and check if French remains
                if not should_skip(merged_text):
                    translated = translate_text(merged_text)
                    if has_french_words(translated):
                        all_untranslated[merged_text] = ""

                i = j

        doc.close()
        print(f"  Found {sum(1 for k in all_untranslated if k in [r['original'] for r in replacements])} untranslated in this PDF")

    except Exception as e:
        print(f"  Error: {e}")

print(f"\n{'='*80}")
print(f"TOTAL UNTRANSLATED TEXTS ACROSS ALL 5 PDFs: {len(all_untranslated)}")
print(f"{'='*80}")

# Save
with open('all_untranslated.json', 'w', encoding='utf-8') as f:
    json.dump(all_untranslated, f, ensure_ascii=False, indent=2)

print(f"\nSaved to: all_untranslated.json")
print(f"\nSample (first 20):")
for i, text in enumerate(list(all_untranslated.keys())[:20], 1):
    print(f"  {i}. {text[:80]}")
