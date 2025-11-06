"""
Method 11: Indexed Sentence Translation
- Short text (1-3 words): Dictionary lookup
- Sentences (4+ words): Collect with index, batch translate with agent, replace
- Clean and simple!
"""
import fitz
import json
import re
import os
import sys

# Load dictionary
print("Loading dictionary...")
with open('translations.json', 'r', encoding='utf-8') as f:
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
    # Examples: pb�, bb�, m�, b�S, etc.
    if len(text) <= 4 and '�' in text:
        return True

    # Skip short technical codes (2-3 lowercase letters)
    if len(text) <= 3 and text.islower() and text.isalpha():
        return True

    return False

def is_sentence(text):
    """Check if text is a sentence (4+ words)"""
    words = text.split()
    return len(words) >= 4

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
    """Use dictionary for short text (1-3 words)"""
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

def translate_pdf_indexed(input_path, output_path):
    """Method 11: Indexed sentence translation"""
    print("="*80)
    print("METHOD 11: INDEXED SENTENCE TRANSLATION")
    print("="*80)
    print(f"Opening PDF: {input_path}")

    # Get PDF code for per-PDF sentence cache (e.g., "A-001", "A-530")
    pdf_code = os.path.basename(input_path).split(' - ')[0]
    sentences_cache = f"{pdf_code}_sentences.json"

    doc = fitz.open(input_path)
    total_pages = len(doc)
    print(f"Total pages: {total_pages}")
    print(f"Sentence cache: {sentences_cache}")

    # Collect all sentences that need agent translation
    sentences_to_translate = {}  # {index: text}
    all_text_elements = []  # All text elements with their info

    # PHASE 1: Extract and categorize all text
    for page_num in range(total_pages):
        print(f"\nPhase 1: Extracting text from page {page_num + 1}/{total_pages}...")
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

            if should_skip(text) or repl.get("is_superscript"):
                # Keep as-is
                repl["translated"] = text
                repl["page"] = page_num
                all_text_elements.append(repl)
            elif is_sentence(text) and has_french(text):
                # Sentence with French - needs agent translation
                index = len(sentences_to_translate)
                sentences_to_translate[index] = text
                repl["translated"] = f"__SENTENCE_{index}__"  # Placeholder
                repl["page"] = page_num
                all_text_elements.append(repl)
                print(f"  [SENTENCE {index}] {text[:60]}...")
            else:
                # Short text - use dictionary
                translated = translate_short_text(text)
                repl["translated"] = translated
                repl["page"] = page_num
                all_text_elements.append(repl)

    print(f"\nPhase 1 complete:")
    print(f"  Total text elements: {len(all_text_elements)}")
    print(f"  Sentences needing agent: {len(sentences_to_translate)}")

    # PHASE 2: Batch translate sentences with agent
    if sentences_to_translate:
        # Check if translations already exist (per-PDF cache)
        if not os.path.exists(sentences_cache):
            print(f"\nPhase 2: Translating {len(sentences_to_translate)} sentences...")

            # Save for agent translation with PDF-specific name
            indexed_file = sentences_cache.replace('_sentences.json', '_sentences_indexed.json')
            with open(indexed_file, 'w', encoding='utf-8') as f:
                json.dump(sentences_to_translate, f, ensure_ascii=False, indent=2)

            print(f"Saved to: {indexed_file}")
            print("\n**ACTION REQUIRED:**")
            print(f"1. Translate {indexed_file} with Task agent")
            print(f"2. Save translations to {sentences_cache}")
            print("3. Re-run this script to complete translation")
            print("\nExiting for now...")
            return
        else:
            print(f"\nPhase 2: Using existing {sentences_cache}")

    # PHASE 3: Apply translations
    print(f"\nPhase 3: Applying translations...")

    # Load translated sentences from per-PDF cache
    try:
        with open(sentences_cache, 'r', encoding='utf-8') as f:
            translated_sentences = json.load(f)
    except:
        print(f"ERROR: {sentences_cache} not found!")
        print(f"Please translate the indexed file first.")
        return

    # Replace placeholders with actual translations
    for elem in all_text_elements:
        if elem["translated"].startswith("__SENTENCE_"):
            index = int(elem["translated"].replace("__SENTENCE_", "").replace("__", ""))
            elem["translated"] = translated_sentences.get(str(index), elem["original"])

    # Apply to PDF
    for page_num in range(total_pages):
        print(f"\nApplying to page {page_num + 1}/{total_pages}...")
        page = doc[page_num]

        page_elements = [e for e in all_text_elements if e["page"] == page_num]

        # Cover original text with white rectangles (preserve strikethrough)
        for elem in page_elements:
            bbox = elem["bbox"]
            # Reduce rectangle size slightly (1pt margin reduction on each side)
            rect = fitz.Rect(bbox[0] + 0.5, bbox[1] + 0.5, bbox[2] - 0.5, bbox[3] - 0.5)
            # Draw white rectangle to cover original text
            page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

        # Insert translated text
        try:
            font = fitz.Font("helv")
        except:
            font = fitz.Font()

        success = 0
        for elem in page_elements:
            bbox = elem["bbox"]
            translated_text = elem["translated"]
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

        print(f"  Inserted {success}/{len(page_elements)} text elements")

    print(f"\nSaving to: {output_path}")
    doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()
    print("Method 11 complete!")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python method11_indexed_sentences.py <input_pdf> <output_pdf>")
        sys.exit(1)

    translate_pdf_indexed(sys.argv[1], sys.argv[2])
