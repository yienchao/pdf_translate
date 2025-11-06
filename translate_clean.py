"""
Clean PDF Translation System
- Dictionary: 7 words and less (shared, grows over time)
- Indexed JSON: 8+ words (per-PDF, regenerated each run)
- Uses white rectangle redaction (method 9 proven approach)
"""
import fitz
import json
import os
from pathlib import Path

# Folders
ORIGINAL_FOLDER = "original"
TRANSLATED_FOLDER = "translated_pdfs"
DATA_FOLDER = "method9_data"

# Load base dictionary
TRANSLATION_DICT = {}
BASE_DICT_PATH = "base_french_dict.json"
if os.path.exists(BASE_DICT_PATH):
    with open(BASE_DICT_PATH, 'r', encoding='utf-8') as f:
        TRANSLATION_DICT.update(json.load(f))

# Load growing dictionary
DICT_PATH = f"{DATA_FOLDER}/translations.json"
if os.path.exists(DICT_PATH):
    with open(DICT_PATH, 'r', encoding='utf-8') as f:
        TRANSLATION_DICT.update(json.load(f))

print(f"Dictionary loaded: {len(TRANSLATION_DICT)} entries")

def should_skip(text):
    """Skip empty, numbers only, units"""
    if not text or not text.strip():
        return True
    if not any(c.isalpha() for c in text):
        return True

    units = {'MM', 'CM', 'M', 'KG', 'LB', 'FT', 'IN', 'SQ', 'MIN', 'MAX', 'NO', 'QTY', 'TYP', 'REF'}
    if text.upper() in units:
        return True

    # Don't skip corrupted chars - normalize_accents() will handle them
    # if len(text) <= 4 and '�' in text:
    #     return True

    return False

def has_french(text):
    """Assume everything is French unless it's clearly English/acronyms"""
    # Exceptions: acronyms and very short English words
    english_exceptions = {
        'DOM', 'INTL', 'REV', 'NO', 'TYP', 'MAX', 'MIN', 'REF', 'SQ',
        'FT', 'IN', 'MM', 'CM', 'KG', 'LB', 'GA', 'CAL', 'ID', 'QTY',
        'SEE', 'NEW', 'EXISTING', 'LEVEL', 'ZONE', 'TYPE', 'CODE',
        'AND', 'OR', 'OF', 'TO', 'AT', 'BY', 'FOR', 'WITH', 'FROM'
    }

    # If text is all uppercase and 2-4 chars, likely an acronym
    if text.isupper() and 2 <= len(text) <= 4 and text.isalpha():
        if text in english_exceptions:
            return False

    # If all words are English exceptions, it's English
    words = text.upper().split()
    if all(word.strip('.,;:()[]{}!?-') in english_exceptions for word in words):
        return False

    # Everything else: assume French
    return True

def normalize_accents(text):
    """Normalize corrupted PDF accents (� → proper letters)"""
    # Map replacement character to common French accents
    replacements = {
        'ING�NIERIE': 'INGÉNIERIE',
        'Ing�nierie': 'Ingénierie',
        'VITR�ES': 'VITRÉES',
        'Vitr�es': 'Vitrées',
        'VITR�E': 'VITRÉE',
        'D�TAILS': 'DÉTAILS',
        'D�tail': 'Détail',
        'ENCASTR�': 'ENCASTRÉ',
        '�L�MENT': 'ÉLÉMENT',
        '�QUIPEMENTS': 'ÉQUIPEMENTS',
        '�TAGE': 'ÉTAGE',
        '�PAISSEUR': 'ÉPAISSEUR',
        'L�GENDES': 'LÉGENDES',
        '�TANCHE': 'ÉTANCHE',
    }

    # Try exact replacements first
    for corrupted, proper in replacements.items():
        if corrupted in text:
            text = text.replace(corrupted, proper)

    # General replacement: � → É (most common)
    text = text.replace('�', 'É')

    return text

def translate_with_dict(text):
    """Lookup in dictionary (exact match or case-insensitive)"""
    # Normalize accents for PDF corrupted text
    normalized = normalize_accents(text)

    # Exact match
    if normalized in TRANSLATION_DICT:
        return TRANSLATION_DICT[normalized]

    # Case-insensitive
    text_lower = normalized.lower()
    for key, value in TRANSLATION_DICT.items():
        if key.lower() == text_lower:
            # Match case
            if text.isupper():
                return value.upper()
            elif text.islower():
                return value.lower()
            elif text[0].isupper():
                return value.capitalize()
            return value

    return None

def merge_text_spans(spans):
    """Merge adjacent text spans"""
    if not spans:
        return []

    spans.sort(key=lambda s: (round(s["bbox"][1], 1), s["bbox"][0]))

    merged = []
    current = spans[0].copy()
    current["bbox"] = list(current["bbox"])

    for next_span in spans[1:]:
        same_line = abs(current["bbox"][1] - next_span["bbox"][1]) < 2
        x_gap = next_span["bbox"][0] - current["bbox"][2]
        close_horizontal = -1 <= x_gap <= 5

        if same_line and close_horizontal:
            if x_gap > 0.5:
                current["text"] += " " + next_span["text"]
            else:
                current["text"] += next_span["text"]
            current["bbox"][2] = max(current["bbox"][2], next_span["bbox"][2])
        else:
            merged.append(current)
            current = next_span.copy()
            current["bbox"] = list(current["bbox"])

    merged.append(current)
    return merged

def extract_text_from_pdf(pdf_path):
    """Extract all text with positions"""
    doc = fitz.open(pdf_path)
    all_text = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]

        page_spans = []
        for block in blocks:
            if block.get("type") == 0:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        if text:
                            page_spans.append({
                                "text": text,
                                "bbox": list(span["bbox"]),
                                "size": span["size"],
                                "color": span.get("color", 0)
                            })

        merged = merge_text_spans(page_spans)

        for item in merged:
            all_text.append({
                "page": page_num,
                "text": item["text"],
                "bbox": item["bbox"],
                "size": item["size"],
                "color": item["color"]
            })

    doc.close()
    return all_text

def process_pdf(input_path, output_path):
    """Process single PDF with clean dictionary + indexed JSON logic"""
    print(f"\n{'='*80}")
    print(f"Processing: {os.path.basename(input_path)}")
    print('='*80)

    pdf_code = os.path.basename(input_path).split(' - ')[0]
    indexed_file = f"{DATA_FOLDER}/{pdf_code}_indexed.json"
    to_translate_file = f"{DATA_FOLDER}/{pdf_code}_to_translate.json"

    # Extract text
    print("Extracting text...")
    text_elements = extract_text_from_pdf(input_path)
    print(f"Found {len(text_elements)} text elements")

    # Process each element
    needs_translation = {}  # indexed: {0: french_text, 1: french_text}
    new_dict_entries = {}   # for dictionary: {french: english}

    for idx, elem in enumerate(text_elements):
        text = elem["text"]
        word_count = len(text.split())

        # Skip
        if should_skip(text):
            elem["translated"] = text
            elem["type"] = "skip"
            continue

        # Try dictionary (all text)
        translated = translate_with_dict(text)

        if translated:
            elem["translated"] = translated
            elem["type"] = "dict"
        elif has_french(text):
            # French but not in dictionary
            if word_count <= 10:
                # Short/medium phrase - needs to go in dictionary
                elem["type"] = "needs_dict"
                needs_translation[str(idx)] = text
            else:
                # Long sentence (11+ words) - needs indexed translation
                elem["type"] = "needs_indexed"
                needs_translation[str(idx)] = text
        else:
            # No French detected
            elem["translated"] = text
            elem["type"] = "english"

    print(f"Elements needing translation: {len(needs_translation)}")

    # Check if we need translations
    if needs_translation:
        if not os.path.exists(indexed_file):
            # Save for translation
            print(f"\nSaving texts to translate: {to_translate_file}")
            with open(to_translate_file, 'w', encoding='utf-8') as f:
                json.dump(needs_translation, f, ensure_ascii=False, indent=2)

            print(f"\nACTION REQUIRED:")
            print(f"1. Translate {to_translate_file}")
            print(f"2. Save result as {indexed_file}")
            print(f"3. Re-run this script")
            return False

        # Load translations
        print(f"Loading translations from {indexed_file}")
        with open(indexed_file, 'r', encoding='utf-8') as f:
            translations = json.load(f)

        # Apply translations
        for idx, elem in enumerate(text_elements):
            if elem.get("type") in ["needs_dict", "needs_indexed"]:
                original = elem["text"]
                translated = translations.get(str(idx), original)
                elem["translated"] = translated

                # Add to dictionary if 10 words or less
                word_count = len(original.split())
                if word_count <= 10:
                    new_dict_entries[original] = translated

        # Update dictionary with new entries (10 words and less only)
        if new_dict_entries:
            print(f"Adding {len(new_dict_entries)} new entries to dictionary")
            TRANSLATION_DICT.update(new_dict_entries)
            with open(DICT_PATH, 'w', encoding='utf-8') as f:
                json.dump(TRANSLATION_DICT, f, ensure_ascii=False, indent=2)
            print(f"Dictionary now has {len(TRANSLATION_DICT)} entries")

    # Apply to PDF
    print("Applying translations to PDF...")
    doc = fitz.open(input_path)

    for page_num in range(len(doc)):
        page = doc[page_num]
        page_elements = [e for e in text_elements if e["page"] == page_num]

        # Cover original text with white rectangles
        for elem in page_elements:
            bbox = elem["bbox"]
            rect = fitz.Rect(bbox[0] + 0.5, bbox[1] + 0.5, bbox[2] - 0.5, bbox[3] - 0.5)
            page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

        # Insert translated text
        try:
            font = fitz.Font("helv")
        except:
            font = fitz.Font()

        success_count = 0
        for elem in page_elements:
            translated = elem.get("translated", elem["text"])
            bbox = elem["bbox"]
            size = elem["size"]

            if not translated:
                continue

            # Color conversion
            color_int = elem["color"]
            color = (
                ((color_int >> 16) & 0xFF) / 255.0,
                ((color_int >> 8) & 0xFF) / 255.0,
                (color_int & 0xFF) / 255.0
            )

            try:
                page.insert_text(
                    (bbox[0], bbox[3] - 1),
                    translated,
                    fontsize=size,
                    color=color,
                    render_mode=0
                )
                success_count += 1
            except:
                pass

        if page_num == 0:
            print(f"  Inserted {success_count}/{len(page_elements)} texts on page 1")

    print(f"Saving to: {output_path}")
    doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()
    print("Done!")
    return True

def translate_filename(filename):
    """Translate French words in filename using dictionary"""
    # Split filename into parts: "A-001 - NOTES ET LÉGENDES.pdf"
    # Keep PDF code (A-001), translate the rest
    parts = filename.rsplit('.pdf', 1)
    if len(parts) != 2:
        return filename

    name_part = parts[0]

    # Split by spaces and hyphens, keeping separators
    import re
    words = re.split(r'(\s+|-)', name_part)

    translated_words = []
    for word in words:
        if not word or word.isspace() or word == '-':
            translated_words.append(word)
        else:
            # Normalize and translate
            normalized = normalize_accents(word)
            translation = translate_with_dict(normalized)
            if translation:
                translated_words.append(translation)
            else:
                translated_words.append(word)

    return ''.join(translated_words) + '.pdf'

def main():
    """Process all PDFs"""
    os.makedirs(TRANSLATED_FOLDER, exist_ok=True)
    os.makedirs(DATA_FOLDER, exist_ok=True)

    pdf_files = list(Path(ORIGINAL_FOLDER).glob("*.pdf"))
    print(f"\nFound {len(pdf_files)} PDFs in {ORIGINAL_FOLDER}/")

    for pdf_path in pdf_files:
        # Translate filename using dictionary
        translated_name = translate_filename(pdf_path.name)
        output_path = os.path.join(TRANSLATED_FOLDER, translated_name)

        success = process_pdf(str(pdf_path), output_path)
        if not success:
            print(f"\nStopped - translation needed for {pdf_path.name}")
            break
    else:
        print(f"\n{'='*80}")
        print("ALL PDFS PROCESSED!")
        print('='*80)

if __name__ == "__main__":
    main()
