"""
Method 9: Optimized Translation
- Pre-compile all regex patterns (MUCH faster)
- Skip numbers, units, acronyms (2-4 uppercase letters)
- Smart font sizing
- Overlap detection
"""
import fitz
import json
import re

# Load FULL translation dictionary and PRE-COMPILE all regex patterns
print("Loading FULL dictionary and compiling patterns...")
with open('translations.json', 'r', encoding='utf-8') as f:
    TRANSLATION_DICT = json.load(f)

# Pre-compile regex patterns (huge speed boost - this is the key optimization!)
COMPILED_PATTERNS = []
sorted_terms = sorted(TRANSLATION_DICT.items(), key=lambda x: len(x[0]), reverse=True)

print(f"Compiling {len(TRANSLATION_DICT)} regex patterns...")
for french, english in sorted_terms:
    try:
        pattern = re.compile(r'\b' + re.escape(french) + r'\b', re.IGNORECASE)
        COMPILED_PATTERNS.append((pattern, english))
    except:
        pattern = re.compile(re.escape(french), re.IGNORECASE)
        COMPILED_PATTERNS.append((pattern, english))

print(f"Ready! {len(TRANSLATION_DICT)} translations with pre-compiled patterns")

def should_skip(text):
    """
    Skip:
    - Numbers only
    - Units (mm, cm, m, etc.)
    - DO NOT SKIP ACRONYMS (translate them!)
    """
    if not text or not text.strip():
        return True

    # Skip if all numbers/punctuation
    if not any(c.isalpha() for c in text):
        return True

    # Skip units
    units = {'MM', 'CM', 'M', 'KG', 'LB', 'FT', 'IN', 'SQ', 'MIN', 'MAX', 'NO', 'QTY'}
    if text.upper() in units:
        return True

    return False

def translate_text_optimized(text):
    """
    Fast translation using pre-compiled patterns
    Respects case: if French is lowercase, English is lowercase too
    """
    if not text or not text.strip() or should_skip(text):
        return text

    # Check if text is all uppercase, all lowercase, or mixed
    is_upper = text.isupper()
    is_lower = text.islower()

    translated = text
    for pattern, english in COMPILED_PATTERNS:
        if pattern.search(translated):
            # Respect case
            if is_lower:
                translated = pattern.sub(english.lower(), translated)
            elif is_upper:
                translated = pattern.sub(english.upper(), translated)
            else:
                # Mixed case - keep dictionary case
                translated = pattern.sub(english, translated)

    return translated

def bboxes_overlap(bbox1, bbox2, threshold=5):
    """Check if two bounding boxes overlap"""
    y_overlap = not (bbox1[3] < bbox2[1] or bbox2[3] < bbox1[1])
    if not y_overlap:
        return False

    x_gap = bbox2[0] - bbox1[2]
    return -10 <= x_gap <= threshold

def merge_overlapping_spans(replacements):
    """Merge overlapping text spans"""
    normal_text = []
    superscripts = []

    for r in replacements:
        bbox_height = r["bbox"][3] - r["bbox"][1]
        if r["size"] < 7 or bbox_height < 7:
            superscripts.append({
                "original": r["original"],
                "translated": r["original"],
                "bbox": r["bbox"],
                "size": r["size"],
                "color": r["color"]
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

        merged_translated = translate_text_optimized(merged_text)

        merged.append({
            "original": merged_text,
            "translated": merged_translated,
            "bbox": bbox,
            "size": current["size"],
            "color": current["color"]
        })

        i = j

    merged.extend(superscripts)
    return merged

def translate_pdf_method9(input_path, output_path):
    """Method 9: Optimized translation"""
    print("="*80)
    print("METHOD 9: OPTIMIZED TRANSLATION")
    print("="*80)
    print(f"Opening PDF: {input_path}")

    doc = fitz.open(input_path)
    total_pages = len(doc)
    print(f"Total pages: {total_pages}")

    for page_num in range(total_pages):
        print(f"\nProcessing page {page_num + 1}/{total_pages}...")
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
                            translated_text = translate_text_optimized(original_text)

                            replacements.append({
                                "original": original_text,
                                "translated": translated_text,
                                "bbox": span.get("bbox"),
                                "size": span.get("size"),
                                "color": span.get("color", 0),
                            })

        print(f"Found {len(replacements)} text elements")

        replacements = merge_overlapping_spans(replacements)
        print(f"After merging: {len(replacements)} text elements")

        # Redact original French text (remove it completely)
        for repl in replacements:
            bbox = repl["bbox"]
            rect = fitz.Rect(bbox)
            # Redact with NO fill color - just remove the text
            page.add_redact_annot(rect)

        # Apply all redactions at once
        page.apply_redactions()

        success_count = 0

        try:
            font = fitz.Font("helv")
        except:
            font = fitz.Font()

        for repl in replacements:
            bbox = repl["bbox"]
            original_text = repl["original"]
            translated_text = repl["translated"]
            original_font_size = repl["size"]

            try:
                original_width = font.text_length(original_text, fontsize=original_font_size)
                translated_width = font.text_length(translated_text, fontsize=original_font_size)
            except:
                original_width = len(original_text) * original_font_size * 0.6
                translated_width = len(translated_text) * original_font_size * 0.6

            # Calculate font size adjustment to fit text
            # Keep height similar by adjusting font size proportionally
            if translated_width > original_width:
                scale_factor = original_width / translated_width
                # Apply minimum 70% scaling to keep text readable
                scale_factor = max(scale_factor, 0.7)
                adjusted_font_size = original_font_size * scale_factor
            else:
                adjusted_font_size = original_font_size

            color_int = repl["color"]
            color = (
                ((color_int >> 16) & 0xFF) / 255.0,
                ((color_int >> 8) & 0xFF) / 255.0,
                (color_int & 0xFF) / 255.0
            )

            try:
                page.insert_text(
                    (bbox[0], bbox[3] - 1),
                    translated_text,
                    fontsize=adjusted_font_size,
                    color=color,
                    render_mode=0
                )
                success_count += 1
            except:
                try:
                    page.insert_text(
                        (bbox[0], bbox[3] - 1),
                        translated_text,
                        fontsize=adjusted_font_size,
                        color=color
                    )
                    success_count += 1
                except:
                    pass

        print(f"  Successfully inserted {success_count}/{len(replacements)} text elements")

    # Detect remaining French words
    untranslated = {}
    french_indicators = ['DE', 'ET', 'LE', 'LA', 'LES', 'DU', 'DES', 'AU', 'AUX', 'EN', 'SUR', 'AVEC', 'POUR', 'PAR', 'DANS']

    for block in text_instances.get("blocks", []):
        if block.get("type") == 0:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "")
                    if text.strip():
                        # Check for French indicators or accents
                        words = re.findall(r'\b[A-ZÀ-ÿ]{2,}\b', text.upper())
                        has_french = any(w in french_indicators for w in words) or any(c in text for c in 'ÀÂÆÇÉÈÊËÏÎÔÙÛÜàâæçéèêëïîôùûü�')

                        if has_french and text not in TRANSLATION_DICT:
                            untranslated[text] = text

    if untranslated:
        print(f"\n{'='*80}")
        print(f"FOUND {len(untranslated)} TEXTS WITH REMAINING FRENCH")
        print(f"{'='*80}")
        print("\nSample (first 10):")
        for i, text in enumerate(list(untranslated.keys())[:10], 1):
            print(f"  {i}. {text}")

        with open('untranslated_french_words.json', 'w', encoding='utf-8') as f:
            json.dump(untranslated, f, ensure_ascii=False, indent=2)

        print(f"\nSaved to: untranslated_french_words.json")
        print("Translate these and add to dictionary, then re-run!")

    print(f"\nSaving to: {output_path}")
    doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()
    print("Method 9 complete!")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python method9_optimized.py <input_pdf>")
        sys.exit(1)

    input_pdf = sys.argv[1]
    import os
    base = os.path.basename(input_pdf)
    name_without_ext = os.path.splitext(base)[0]

    common_translations = {
        "NOTES": "NOTES",
        "LÉGENDES": "LEGENDS",
        "BORDEREAU": "SCHEDULE",
        "FINIS": "FINISHES",
        "DÉTAILS": "DETAILS",
        "DETAILS": "DETAILS",
        "ENVELOPPE": "ENVELOPE",
        "ENVELOPE": "ENVELOPE",
        "COUPE": "SECTION",
        "SECTION": "SECTION",
    }

    english_name = name_without_ext
    for french, english in common_translations.items():
        english_name = english_name.replace(french, english)

    output_pdf = os.path.join(os.path.dirname(input_pdf), english_name + ".pdf")

    translate_pdf_method9(input_pdf, output_pdf)
