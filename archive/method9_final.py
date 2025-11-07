"""
Method 9 FINAL: Always re-extract + Growing dictionary
- Re-extract text every run (always correct, handles PDF evolution)
- Growing dictionary (translations.json accumulates over time)
- Indexed format (fast integer lookups)
- Simple workflow: run once to extract, translate, run again to apply
"""
import fitz
import json
import os
import sys

# Load dictionary
print("Loading dictionary...")
with open('method9_data/translations.json', 'r', encoding='utf-8') as f:
    TRANSLATION_DICT = json.load(f)

print(f"Dictionary loaded: {len(TRANSLATION_DICT)} entries")

def should_skip(text):
    if not text or not text.strip():
        return True
    if not any(c.isalpha() for c in text):
        return True

    # Skip units
    units = {'MM', 'CM', 'M', 'KG', 'LB', 'FT', 'IN', 'SQ', 'MIN', 'MAX', 'NO', 'QTY', 'TYP', 'REF'}
    if text.upper() in units:
        return True

    # Skip technical codes/acronyms (2-4 chars with special chars like �)
    if len(text) <= 4 and '�' in text:
        return True

    # Skip short technical codes (2-3 lowercase letters)
    if len(text) <= 3 and text.islower() and text.isalpha():
        return True

    return False

def is_sentence(text):
    """Check if text is a sentence (7+ words)"""
    words = text.split()
    return len(words) >= 7

def has_french(text):
    """Quick check if text likely has French"""
    french_indicators = [
        'DE', 'ET', 'LE', 'LA', 'LES', 'DU', 'DES', 'AU', 'AUX', 'EN', 'SUR',
        'AVEC', 'POUR', 'PAR', 'DANS', 'TOUS', 'TOUTES', 'TOUT', 'SONT', 'EST'
    ]
    words = text.upper().split()
    for word in words:
        if word in french_indicators:
            return True
        # Check for accented characters (proper or corrupted)
        if any(c in word for c in 'ÀÂÆÇÉÈÊËÏÎÔÙÛÜàâæçéèêëïîôùûüÿœ�'):
            return True
    return False

def translate_short_text(text):
    """Use dictionary for short text (1-6 words)"""
    # Try exact match first
    if text in TRANSLATION_DICT:
        return TRANSLATION_DICT[text]

    # Try case-insensitive
    for key, value in TRANSLATION_DICT.items():
        if key.lower() == text.lower():
            # Match case
            if text.isupper():
                return value.upper()
            elif text.islower():
                return value.lower()
            else:
                return value

    # No match, return original
    return text

def bboxes_overlap(bbox1, bbox2, threshold=5):
    y_overlap = not (bbox1[3] < bbox2[1] or bbox2[3] < bbox1[1])
    if not y_overlap:
        return False
    x_gap = bbox2[0] - bbox1[2]
    return -10 <= x_gap <= threshold

def merge_overlapping_spans(replacements):
    normal_text = []
    superscripts = []

    for r in replacements:
        bbox_height = r["bbox"][3] - r["bbox"][1]
        if r["size"] < 7 or bbox_height < 7:
            superscripts.append({
                "original": r["original"],
                "bbox": r["bbox"],
                "size": r["size"],
                "color": r["color"],
                "is_superscript": True
            })
        else:
            normal_text.append(r)

    normal_text.sort(key=lambda r: (round(r["bbox"][1], 1), r["bbox"][0]))

    merged = []
    i = 0

    while i < len(normal_text):
        current = normal_text[i]
        merged_text = current["original"]
        bbox = list(current["bbox"])

        j = i + 1
        while j < len(normal_text):
            next_span = normal_text[j]
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

        merged.append({
            "original": merged_text,
            "bbox": bbox,
            "size": current["size"],
            "color": current["color"],
            "is_superscript": False
        })

        i = j

    merged.extend(superscripts)
    return merged

def translate_pdf_final(input_path, output_path):
    """Method 9 FINAL: Always re-extract with growing dictionary"""
    print("="*80)
    print("METHOD 9 FINAL: ALWAYS RE-EXTRACT + GROWING DICTIONARY")
    print("="*80)

    # Get PDF code
    pdf_code = os.path.basename(input_path).split(' - ')[0]
    sentences_file = f"method9_data/{pdf_code}_sentences.json"
    to_translate_file = f"method9_data/{pdf_code}_to_translate.json"

    print(f"PDF: {input_path}")
    print(f"Code: {pdf_code}")

    # PHASE 1: ALWAYS extract text (no cache)
    print(f"\nPhase 1: Extracting text from PDF...")
    doc = fitz.open(input_path)
    total_pages = len(doc)
    print(f"Total pages: {total_pages}")

    all_elements = []
    sentences_to_translate = {}  # {index: french_text}

    for page_num in range(total_pages):
        print(f"  Extracting page {page_num + 1}/{total_pages}...")
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
                                "color": span.get("color", 0),
                            })

        replacements = merge_overlapping_spans(replacements)

        for repl in replacements:
            text = repl["original"]
            index = len(all_elements)

            element = {
                "index": index,
                "page": page_num,
                "original": text,
                "bbox": repl["bbox"],
                "size": repl["size"],
                "color": repl["color"],
                "is_superscript": repl.get("is_superscript", False)
            }

            if should_skip(text) or repl.get("is_superscript"):
                element["translated"] = text
                element["type"] = "skip"
            elif is_sentence(text):
                # Check if already in growing dictionary
                if text in TRANSLATION_DICT:
                    element["translated"] = TRANSLATION_DICT[text]
                    element["type"] = "sentence_cached"
                else:
                    # Try dictionary lookup first (case-insensitive)
                    translated = translate_short_text(text)
                    if translated != text:
                        # Found in dictionary
                        element["translated"] = translated
                        element["type"] = "sentence_dict"
                    elif has_french(text):
                        # Not in dict and has French indicators - needs manual translation
                        element["type"] = "sentence"
                        element["needs_translation"] = True
                        sentences_to_translate[str(index)] = text
                        print(f"  [SENTENCE {index}] {text[:60]}...")
                    else:
                        # Not in dict, no French indicators - keep original
                        element["translated"] = text
                        element["type"] = "english_sentence"
            else:
                # Short text - translate with dictionary
                translated = translate_short_text(text)
                element["translated"] = translated
                element["type"] = "short"

            all_elements.append(element)

    print(f"\nPhase 1 complete:")
    print(f"  Total text elements: {len(all_elements)}")
    print(f"  Sentences needing translation: {len(sentences_to_translate)}")

    # PHASE 2: Check if translations exist
    if sentences_to_translate:
        if not os.path.exists(sentences_file):
            # Save sentences to translate
            print(f"\nSaving sentences to translate: {to_translate_file}")
            with open(to_translate_file, 'w', encoding='utf-8') as f:
                json.dump(sentences_to_translate, f, ensure_ascii=False, indent=2)

            print(f"\n**ACTION REQUIRED:**")
            print(f"1. Translate {to_translate_file}")
            print(f"   Format: {{\"0\": \"english translation\", \"1\": \"another translation\"}}")
            print(f"2. Save as {sentences_file}")
            print(f"3. Re-run this script")
            print("\nExiting...")
            doc.close()
            return

        print(f"\nPhase 2: Loading translations from {sentences_file}")
        with open(sentences_file, 'r', encoding='utf-8') as f:
            translations = json.load(f)

        # Apply translations by index
        new_translations = {}
        for elem in all_elements:
            if elem.get("needs_translation"):
                idx = str(elem["index"])
                translated = translations.get(idx, elem["original"])
                elem["translated"] = translated
                # Collect new translations for dictionary
                new_translations[elem["original"]] = translated

        # PHASE 2.5: Update growing dictionary
        if new_translations:
            print(f"\nPhase 2.5: Adding {len(new_translations)} translations to dictionary...")
            TRANSLATION_DICT.update(new_translations)
            with open('method9_data/translations.json', 'w', encoding='utf-8') as f:
                json.dump(TRANSLATION_DICT, f, ensure_ascii=False, indent=2)
            print(f"  Dictionary now has {len(TRANSLATION_DICT)} entries")

    # PHASE 3: Apply to PDF
    print(f"\nPhase 3: Applying translations to PDF...")

    for page_num in range(total_pages):
        print(f"  Page {page_num + 1}/{total_pages}...")
        page = doc[page_num]

        page_elements = [e for e in all_elements if e["page"] == page_num]

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

        success = 0
        for elem in page_elements:
            bbox = elem["bbox"]
            translated_text = elem.get("translated", elem["original"])
            font_size = elem["size"]

            # Calculate font size adjustment
            try:
                orig_width = font.text_length(elem["original"], fontsize=font_size)
                trans_width = font.text_length(translated_text, fontsize=font_size)
                if trans_width > orig_width:
                    scale = max(orig_width / trans_width, 0.7)
                    font_size = font_size * scale
            except:
                pass

            color_int = elem["color"]
            color = (
                ((color_int >> 16) & 0xFF) / 255.0,
                ((color_int >> 8) & 0xFF) / 255.0,
                (color_int & 0xFF) / 255.0
            )

            try:
                page.insert_text(
                    (bbox[0], bbox[3] - 1),
                    translated_text,
                    fontsize=font_size,
                    color=color,
                    render_mode=0
                )
                success += 1
            except:
                pass

        print(f"    Inserted {success}/{len(page_elements)} elements")

    print(f"\nSaving: {output_path}")
    doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()
    print("Complete!")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python method9_final.py <input_pdf> <output_pdf>")
        sys.exit(1)

    translate_pdf_final(sys.argv[1], sys.argv[2])
