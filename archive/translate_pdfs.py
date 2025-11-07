"""
PDF Translation Script
- Processes PDFs from original/ folder
- Outputs to translated_pdfs/ folder
- Uses Claude Code agents for translation
- Simple, solid logic
"""
import fitz
import json
import os
from pathlib import Path

# Folders
ORIGINAL_FOLDER = "original"
TRANSLATED_FOLDER = "translated_pdfs"
DATA_FOLDER = "method9_data"

# Load dictionaries
TRANSLATION_DICT = {}

# Load base dictionary (common French words)
BASE_DICT_PATH = "base_french_dict.json"
if os.path.exists(BASE_DICT_PATH):
    with open(BASE_DICT_PATH, 'r', encoding='utf-8') as f:
        TRANSLATION_DICT.update(json.load(f))
    print(f"Base dictionary loaded: {len(TRANSLATION_DICT)} entries")

# Load growing dictionary (learned translations)
DICT_PATH = f"{DATA_FOLDER}/translations.json"
if os.path.exists(DICT_PATH):
    with open(DICT_PATH, 'r', encoding='utf-8') as f:
        TRANSLATION_DICT.update(json.load(f))
    print(f"Total dictionary: {len(TRANSLATION_DICT)} entries")
else:
    print("No learned dictionary yet")

def should_skip(text):
    """Check if text should be skipped (empty, numbers only, units)"""
    if not text or not text.strip():
        return True
    if not any(c.isalpha() for c in text):
        return True

    units = {'MM', 'CM', 'M', 'KG', 'LB', 'FT', 'IN', 'SQ', 'MIN', 'MAX', 'NO', 'QTY', 'TYP', 'REF'}
    if text.upper() in units:
        return True

    if len(text) <= 4 and '�' in text:
        return True

    return False

def is_long_text(text):
    """Check if text is long (4+ words) - needs agent translation"""
    return len(text.split()) >= 4

def has_french(text):
    """Check if text likely has French"""
    french_words = [
        'DE', 'ET', 'LE', 'LA', 'LES', 'DU', 'DES', 'AU', 'AUX', 'EN', 'SUR',
        'AVEC', 'POUR', 'PAR', 'DANS', 'TOUS', 'TOUTES', 'TOUT', 'SONT', 'EST',
        'VOIR', 'NOUVEAU', 'NOUVELLE', 'ÊTRE', 'SANS', 'SOUS', 'ENTRE', 'AUTRE',
        'INGÉNIERIE', 'BÉTON', 'PLAFOND', 'PLANCHER', 'PORTE', 'MUR', 'CLOISON',
        'REVÊTEMENT', 'ÉQUIPEMENTS', 'MÉTALLIQUE', 'ACIER', 'FEUILLE'
    ]
    words = text.upper().split()
    for word in words:
        # Remove punctuation for checking
        clean_word = word.strip('.,;:()[]{}!?')
        if clean_word in french_words:
            return True
        if any(c in word for c in 'ÀÂÆÇÉÈÊËÏÎÔÙÛÜàâæçéèêëïîôùûüÿœ�'):
            return True
    return False

def translate_with_dict(text):
    """Use dictionary for text"""
    # Exact match
    if text in TRANSLATION_DICT:
        return TRANSLATION_DICT[text]

    # Case-insensitive search
    text_lower = text.lower()
    for key, value in TRANSLATION_DICT.items():
        if key.lower() == text_lower:
            # Match the case of original text
            if text.isupper():
                return value.upper()
            elif text.islower():
                return value.lower()
            elif text[0].isupper():  # Title case
                return value.capitalize()
            return value

    # Try partial match for phrases (split by spaces/punctuation)
    words = text.split()
    if len(words) > 1:
        translated_words = []
        for word in words:
            # Remove punctuation
            clean = word.strip('.,;:()[]{}!?-')
            punct = word[len(clean):] if len(word) > len(clean) else ''

            # Translate the clean word
            trans = translate_with_dict(clean)
            if trans:
                translated_words.append(trans + punct)
            else:
                translated_words.append(word)

        result = ' '.join(translated_words)
        if result != text:
            return result

    return None

def merge_text_spans(spans):
    """Merge adjacent text spans into logical blocks"""
    if not spans:
        return []

    # Sort by vertical position, then horizontal
    spans.sort(key=lambda s: (round(s["bbox"][1], 1), s["bbox"][0]))

    merged = []
    current = spans[0].copy()
    current["bbox"] = list(current["bbox"])  # Convert tuple to list

    for next_span in spans[1:]:
        # Check if same line (Y position similar)
        same_line = abs(current["bbox"][1] - next_span["bbox"][1]) < 2
        # Check if close horizontally (small gap for same word/phrase)
        x_gap = next_span["bbox"][0] - current["bbox"][2]
        close_horizontal = -1 <= x_gap <= 5  # Tighter threshold

        if same_line and close_horizontal:
            # Merge
            if x_gap > 0.5:
                current["text"] += " " + next_span["text"]
            else:
                current["text"] += next_span["text"]
            current["bbox"][2] = max(current["bbox"][2], next_span["bbox"][2])
        else:
            # Save current and start new
            merged.append(current)
            current = next_span.copy()
            current["bbox"] = list(current["bbox"])  # Convert tuple to list

    merged.append(current)
    return merged

def extract_text_from_pdf(pdf_path):
    """Extract all text with positions from PDF"""
    doc = fitz.open(pdf_path)
    all_text = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]

        page_spans = []
        for block in blocks:
            if block.get("type") == 0:  # Text block
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

        # Merge adjacent spans
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
    """Process single PDF: extract, translate, apply"""
    print(f"\n{'='*80}")
    print(f"Processing: {os.path.basename(input_path)}")
    print('='*80)

    pdf_code = os.path.basename(input_path).split(' - ')[0]
    sentences_file = f"{DATA_FOLDER}/{pdf_code}_sentences.json"
    to_translate_file = f"{DATA_FOLDER}/{pdf_code}_to_translate.json"

    # Extract text
    print("Extracting text...")
    text_elements = extract_text_from_pdf(input_path)
    print(f"Found {len(text_elements)} text elements")

    # Process each text element
    needs_translation = {}

    for idx, elem in enumerate(text_elements):
        text = elem["text"]

        # Skip non-text
        if should_skip(text):
            elem["translated"] = text
            elem["type"] = "skip"
            continue

        # Try dictionary first (for all text)
        translated = translate_with_dict(text)

        if translated:
            # Found in dictionary
            elem["translated"] = translated
            elem["type"] = "dict"
        elif has_french(text):
            # Has French but not in dictionary - needs translation
            elem["type"] = "needs_translation"
            needs_translation[str(idx)] = text
        else:
            # No French detected - keep as is
            elem["translated"] = text
            elem["type"] = "english"

    print(f"Elements needing translation: {len(needs_translation)}")

    # Check if we need manual translation
    if needs_translation:
        if not os.path.exists(sentences_file):
            print(f"\nSaving texts to translate: {to_translate_file}")
            with open(to_translate_file, 'w', encoding='utf-8') as f:
                json.dump(needs_translation, f, ensure_ascii=False, indent=2)

            print(f"\nACTION REQUIRED:")
            print(f"1. Use Claude Code agent to translate {to_translate_file}")
            print(f"2. Save result as {sentences_file}")
            print(f"3. Re-run this script")
            return False

        # Load translations
        print(f"Loading translations from {sentences_file}")
        with open(sentences_file, 'r', encoding='utf-8') as f:
            translations = json.load(f)

        # Apply translations
        new_dict_entries = {}
        for idx, elem in enumerate(text_elements):
            if elem.get("type") == "needs_translation":
                original = elem["text"]
                translated = translations.get(str(idx), original)
                elem["translated"] = translated
                new_dict_entries[original] = translated

        # Update dictionary
        if new_dict_entries:
            print(f"Adding {len(new_dict_entries)} entries to dictionary")
            TRANSLATION_DICT.update(new_dict_entries)
            with open(DICT_PATH, 'w', encoding='utf-8') as f:
                json.dump(TRANSLATION_DICT, f, ensure_ascii=False, indent=2)

    # Apply to PDF
    print("Applying translations to PDF...")
    doc = fitz.open(input_path)

    for page_num in range(len(doc)):
        page = doc[page_num]
        page_elements = [e for e in text_elements if e["page"] == page_num]

        # Remove original text by redacting it
        for elem in page_elements:
            bbox = elem["bbox"]
            rect = fitz.Rect(bbox[0], bbox[1], bbox[2], bbox[3])
            page.add_redact_annot(rect, fill=(1, 1, 1))

        # Apply redactions to actually remove the text
        page.apply_redactions()

        # Insert translated text
        font = fitz.Font("helv")
        success_count = 0
        for elem in page_elements:
            translated = elem.get("translated", elem["text"])
            bbox = elem["bbox"]
            size = elem["size"]

            # Skip if no translation
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
                    color=color
                )
                success_count += 1
            except Exception as e:
                # Log failures for debugging
                if "VOIR" in elem["text"] or "ING" in elem["text"]:
                    print(f"    Failed to insert: {elem['text'][:50]}")

        if page_num == 0:  # Log first page only
            print(f"    Inserted {success_count}/{len(page_elements)} texts")

    print(f"Saving to: {output_path}")
    doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()
    print("Done!")
    return True

def main():
    """Process all PDFs in original folder"""
    # Ensure folders exist
    os.makedirs(TRANSLATED_FOLDER, exist_ok=True)
    os.makedirs(DATA_FOLDER, exist_ok=True)

    # Get all PDFs
    pdf_files = list(Path(ORIGINAL_FOLDER).glob("*.pdf"))
    print(f"\nFound {len(pdf_files)} PDFs in {ORIGINAL_FOLDER}/")

    for pdf_path in pdf_files:
        output_path = os.path.join(TRANSLATED_FOLDER, pdf_path.name)
        output_path = output_path.replace("LÉGENDES", "LEGENDS").replace("ÉTANCHÉITÉ", "WATERPROOFING")

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
