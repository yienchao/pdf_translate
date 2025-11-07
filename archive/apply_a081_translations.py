"""
Apply translations to A-081 PDF
Uses the hash-based translation memory system
"""
import fitz
import json
import hashlib
import os
import sys

def normalize_text(text):
    """Normalize text for consistent hashing"""
    normalized = ' '.join(text.split())
    return normalized

def hash_text(text):
    """Create hash of text for dictionary lookup"""
    normalized = normalize_text(text)
    hash_obj = hashlib.sha256(normalized.encode('utf-8'))
    return hash_obj.hexdigest()

def should_skip(text):
    """Check if text should be skipped (numbers, codes, etc.)"""
    if not text or not text.strip():
        return True
    if not any(c.isalpha() for c in text):
        return True

    # Skip units
    units = {'MM', 'CM', 'M', 'KG', 'LB', 'FT', 'IN', 'SQ', 'MIN', 'MAX', 'NO', 'QTY', 'TYP', 'REF'}
    if text.upper() in units:
        return True

    # Skip technical codes ending with "..." or "."
    if text.endswith('...') or text.endswith('....') or text.endswith('......'):
        return True

    # Skip very short codes
    clean = text.strip('.°')
    if len(clean) <= 3 and not ' ' in text:
        return True

    # Skip technical codes with special chars
    if len(text) <= 4 and '°' in text:
        return True

    # Skip short technical codes
    if len(text) <= 3 and text.islower() and text.isalpha():
        return True

    return False

def bboxes_overlap(bbox1, bbox2, threshold=5):
    """Check if two bboxes overlap or are close"""
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

def apply_translations(input_path, output_path, translations_dict):
    """Apply translations to PDF"""
    print("="*80)
    print("APPLYING TRANSLATIONS TO A-081 PDF")
    print("="*80)
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print(f"Translations available: {len(translations_dict)}")

    doc = fitz.open(input_path)
    total_pages = len(doc)
    print(f"Total pages: {total_pages}\n")

    # Phase 1: Extract all text
    print("PHASE 1: EXTRACTING TEXT")
    print("-"*80)

    all_text_elements = []
    stats = {'total': 0, 'skipped': 0, 'translated': 0}

    for page_num in range(total_pages):
        print(f"Page {page_num + 1}/{total_pages}...")
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
            stats['total'] += 1

            if should_skip(text) or repl.get("is_superscript"):
                repl["translated"] = text
                repl["page"] = page_num
                all_text_elements.append(repl)
                stats['skipped'] += 1
            else:
                text_hash = hash_text(text)
                if text_hash in translations_dict:
                    repl["translated"] = translations_dict[text_hash]
                    repl["page"] = page_num
                    all_text_elements.append(repl)
                    stats['translated'] += 1
                else:
                    # Keep original if no translation found
                    repl["translated"] = text
                    repl["page"] = page_num
                    all_text_elements.append(repl)
                    print(f"  Warning: No translation for: {text[:50]}")

    print(f"\nPhase 1 Complete:")
    print(f"  Total elements: {stats['total']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Translated: {stats['translated']}")

    # Phase 2: Apply translations to PDF
    print("\n" + "="*80)
    print("PHASE 2: APPLYING TRANSLATIONS")
    print("="*80)

    for page_num in range(total_pages):
        print(f"Page {page_num + 1}/{total_pages}...")
        page = doc[page_num]

        page_elements = [e for e in all_text_elements if e["page"] == page_num]

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

    # Save the translated PDF
    print("\n" + "="*80)
    print(f"Saving to: {output_path}")
    doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()

    print("="*80)
    print("TRANSLATION COMPLETE!")
    print("="*80)
    print(f"Output PDF: {output_path}")

def main():
    # Load translations
    print("Loading translations...")
    with open("A-081_translations.json", 'r', encoding='utf-8') as f:
        translations = json.load(f)
    print(f"Loaded {len(translations)} translations\n")

    # Apply to PDF
    input_pdf = "A-081 - BORDEREAU DES FINIS.pdf"
    output_pdf = "A-081 - FINISHES SCHEDULE.pdf"

    apply_translations(input_pdf, output_pdf, translations)

if __name__ == "__main__":
    main()
