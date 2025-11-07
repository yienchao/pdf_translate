"""
Apply translations to A-081 PDF - Final version
Uses better text replacement by covering and overlaying
"""
import fitz
import json
import hashlib

def normalize_text(text):
    """Normalize text for consistent hashing"""
    normalized = ' '.join(text.split())
    return normalized

def hash_text(text):
    """Create hash of text for dictionary lookup"""
    normalized = normalize_text(text)
    hash_obj = hashlib.sha256(normalized.encode('utf-8'))
    return hash_obj.hexdigest()

def apply_translations_final(input_path, output_path, translations_dict):
    """Apply translations to PDF with better text overlay"""
    print("="*80)
    print("A-081 PDF TRANSLATION - FINAL APPLICATION")
    print("="*80)
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print(f"Translations available: {len(translations_dict)}")

    doc = fitz.open(input_path)
    total_pages = len(doc)
    print(f"Total pages: {total_pages}\n")

    stats = {'total': 0, 'translated': 0, 'skipped': 0}

    # Font configuration
    try:
        font = fitz.Font("helv")
    except:
        font = fitz.Font()

    for page_num in range(total_pages):
        print(f"Processing page {page_num + 1}/{total_pages}...")
        page = doc[page_num]

        # Get all text instances
        text_dict = page.get_text("dict")
        blocks = text_dict.get("blocks", [])

        replacements = []

        # Extract all text with location info
        for block in blocks:
            if block.get("type") == 0:  # Text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        if text:
                            replacements.append({
                                "original": text,
                                "bbox": span.get("bbox"),
                                "size": span.get("size"),
                                "color": span.get("color", 0),
                                "font": span.get("font", "")
                            })

        # Process replacements
        print(f"  Found {len(replacements)} text elements")

        # Sort by position
        replacements.sort(key=lambda r: (round(r["bbox"][1], 1), r["bbox"][0]))

        translated_count = 0
        for repl in replacements:
            original = repl["original"]
            text_hash = hash_text(original)

            # Look up translation
            if text_hash in translations_dict:
                translated = translations_dict[text_hash]
                bbox = repl["bbox"]

                # Create white rectangle to cover original text
                rect = fitz.Rect(bbox[0] - 1, bbox[1] - 1, bbox[2] + 1, bbox[3] + 1)
                page.draw_rect(rect, color=None, fill=(1, 1, 1))

                # Insert translated text
                font_size = repl["size"]

                # Try to scale font if needed
                try:
                    orig_width = font.text_length(original, fontsize=font_size)
                    trans_width = font.text_length(translated, fontsize=font_size)
                    if trans_width > orig_width:
                        scale = orig_width / trans_width
                        font_size = font_size * max(scale, 0.7)
                except:
                    pass

                # Get color
                color_int = repl["color"]
                color_rgb = (
                    ((color_int >> 16) & 0xFF) / 255.0,
                    ((color_int >> 8) & 0xFF) / 255.0,
                    (color_int & 0xFF) / 255.0
                )

                # Insert text at the same position
                try:
                    page.insert_text(
                        (bbox[0], bbox[3] - 1),
                        translated,
                        fontsize=font_size,
                        color=color_rgb,
                        render_mode=0
                    )
                    translated_count += 1
                except Exception as e:
                    pass

                stats['translated'] += 1
            else:
                stats['skipped'] += 1

            stats['total'] += 1

        print(f"  Translated: {translated_count}/{len(replacements)}")

    # Save PDF
    print(f"\nSaving to: {output_path}")
    doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()

    print("="*80)
    print("TRANSLATION COMPLETE!")
    print("="*80)
    print(f"Statistics:")
    print(f"  Total elements: {stats['total']}")
    print(f"  Translated: {stats['translated']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"\nOutput file: {output_path}")

def main():
    # Load translations
    print("Loading translations...\n")
    with open("A-081_translations.json", 'r', encoding='utf-8') as f:
        translations = json.load(f)
    print(f"Loaded {len(translations)} translations\n")

    # Apply to PDF
    input_pdf = "A-081 - BORDEREAU DES FINIS.pdf"
    output_pdf = "A-081 - FINISHES SCHEDULE.pdf"

    apply_translations_final(input_pdf, output_pdf, translations)

if __name__ == "__main__":
    main()
