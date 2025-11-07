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
    """Skip empty, numbers only, units, acronyms, technical codes"""
    if not text or not text.strip():
        return True

    # Skip if no letters (pure numbers, symbols, etc.)
    if not any(c.isalpha() for c in text):
        return True

    # Skip common units and measurement abbreviations
    units = {'MM', 'CM', 'M', 'KG', 'LB', 'FT', 'IN', 'SQ', 'MIN', 'MAX', 'NO', 'QTY', 'TYP', 'REF',
             'GA', 'CAL', 'PSI', 'KPA', 'MPH', 'KPH', 'DEG', 'TEMP', 'DIA', 'THK', 'EA'}
    if text.upper().strip('.,;:()[]{}!?-') in units:
        return True

    # Skip material codes ONLY if they match specific patterns
    # Examples: "ac", "aci", "pbo", "bbé", "pmé" (architectural material abbreviations)
    # But DON'T skip French words like "au", "de", "ou", "et"
    if len(text) <= 4 and not text.isupper():
        # Skip only if it has numbers (like "1a", "2b")
        if any(c.isdigit() for c in text):
            return True
        # Skip ONLY known material code patterns (very specific)
        # Material codes are typically consonant-heavy abbreviations
        material_codes = {'ac', 'aci', 'al', 'ar', 'asp', 'bo', 'br', 'bv', 'bz',
                         'ca', 'cc', 'cf', 'cg', 'ci', 'cp', 'cr', 'cs', 'ct', 'cu', 'cv',
                         'ea', 'ec', 'ei', 'pbo', 'pfs', 'pi', 'pla', 'prt', 'ps', 'pt', 'pvb',
                         'rm', 'rv', 'st', 'ta', 'tc', 'te', 'ti', 'tm', 'tn', 'tep', 'tr',
                         'vac', 'vc', 'vcr'}
        if text.lower() in material_codes:
            return True

    # Skip reference codes like "PL1", "MF2", "A-505", "G485"
    import re
    if re.match(r'^[A-Z]{1,3}\d+[a-z]?$', text, re.IGNORECASE):  # PL1, MF2, A505
        return True
    if re.match(r'^[A-Z]-\d+[a-z]?$', text, re.IGNORECASE):  # A-505, G-123
        return True

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

    # NOTE: Indexed files should be manually deleted when PDFs change
    # For this run, use existing indexed file if present

    # Extract text
    print("Extracting text...")
    text_elements = extract_text_from_pdf(input_path)
    print(f"Found {len(text_elements)} text elements")

    # Process each element
    needs_translation = {}  # indexed: {index: french_text}

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
        else:
            # NOT in dictionary - assume it's French and needs translation
            if word_count <= 10:
                # Short/medium phrase - needs to go in dictionary
                elem["type"] = "needs_dict"
                needs_translation[str(idx)] = text
            else:
                # Long sentence (11+ words) - needs indexed translation
                elem["type"] = "needs_indexed"
                needs_translation[str(idx)] = text

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

        # Build complete text -> translation lookup from indexed file
        # The indexed file contains translations at OLD index positions
        # We need to match by text content since indices may have changed
        indexed_to_translate = {}
        if os.path.exists(to_translate_file):
            with open(to_translate_file, 'r', encoding='utf-8') as f:
                indexed_to_translate = json.load(f)

        # Build reverse lookup: text -> translation from indexed file
        text_to_translation = {}
        for idx_str, french_text in indexed_to_translate.items():
            if idx_str in translations:
                text_to_translation[french_text] = translations[idx_str]

        # Apply translations to ALL elements (not just newly detected ones)
        for idx, elem in enumerate(text_elements):
            original = elem["text"]

            # Skip if already translated from dictionary
            if elem.get("type") == "dict":
                continue

            # Try to find translation by text content
            if original in text_to_translation:
                elem["translated"] = text_to_translation[original]
                elem["type"] = "indexed"  # Mark as translated from indexed file
            elif elem.get("type") in ["needs_dict", "needs_indexed"]:
                # New item not in indexed file - keep as needs translation
                pass

        # DO NOT auto-add indexed translations to dictionary
        # Dictionary should only contain manually verified translations
        # Indexed files are regenerated fresh each run

    # Apply to PDF
    print("Applying translations to PDF...")
    doc = fitz.open(input_path)

    for page_num in range(len(doc)):
        page = doc[page_num]
        page_elements = [e for e in text_elements if e["page"] == page_num]

        # Cover original text with white rectangles (EXPANDED to fully cover)
        for elem in page_elements:
            bbox = elem["bbox"]
            # Expand rectangle by 1 point on all sides to ensure full coverage
            rect = fitz.Rect(bbox[0] - 1, bbox[1] - 1, bbox[2] + 1, bbox[3] + 1)
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
