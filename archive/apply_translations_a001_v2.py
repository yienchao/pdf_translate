#!/usr/bin/env python3
"""
Apply translations to A-001 PDF and create English version.
Version 2: Do not merge spans, translate each span individually.
"""
import fitz  # PyMuPDF
import json
import hashlib
from pathlib import Path

def get_text_hash(text):
    """Generate a hash for text to match translations"""
    return hashlib.sha256(text.strip().encode()).hexdigest()

def load_translations(json_path):
    """Load translation dictionary from JSON file"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading translations: {e}")
        return {}

def translate_pdf(source_pdf, output_pdf, translations):
    """
    Translate PDF by translating each span individually without merging.
    """
    print(f"Opening source PDF: {source_pdf}")
    doc = fitz.open(source_pdf)

    total_pages = len(doc)
    total_replacements = 0
    total_skipped = 0

    for page_num in range(total_pages):
        page = doc[page_num]
        page_replacements = 0

        print(f"\nProcessing page {page_num + 1}/{total_pages}...")

        # Extract all text elements WITHOUT merging
        text_dict = page.get_text("dict")
        blocks = text_dict.get("blocks", [])

        text_elements = []

        for block in blocks:
            if block.get("type") == 0:  # Text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        original_text = span.get("text", "")
                        if original_text.strip():
                            text_elements.append({
                                "original": original_text,
                                "bbox": span.get("bbox", []),
                                "size": span.get("size", 11),
                                "color": span.get("color", 0),
                                "font": span.get("font", "helv"),
                                "flags": span.get("flags", 0),
                            })

        # Prepare font for text insertion
        try:
            font = fitz.Font("helv")
        except:
            font = fitz.Font()

        # Process each text element
        for elem in text_elements:
            original_text = elem["original"]
            text_hash = get_text_hash(original_text)

            if text_hash not in translations:
                total_skipped += 1
                continue

            translated_text = translations[text_hash]
            bbox = elem["bbox"]
            font_size = elem["size"]
            color_int = elem["color"]

            # Skip if translation is same as original
            if translated_text.strip() == original_text.strip():
                continue

            # Convert color from int to RGB tuple
            try:
                color = (
                    ((color_int >> 16) & 0xFF) / 255.0,
                    ((color_int >> 8) & 0xFF) / 255.0,
                    (color_int & 0xFF) / 255.0
                )
            except:
                color = (0, 0, 0)  # Default to black

            try:
                # Cover original text with white rectangle (shrink by 0.5pt on each side)
                rect = fitz.Rect(bbox[0] + 0.5, bbox[1] + 0.5, bbox[2] - 0.5, bbox[3] - 0.5)
                page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

                # Calculate adjusted font size if needed to fit translated text
                try:
                    orig_width = font.text_length(original_text, fontsize=font_size)
                    trans_width = font.text_length(translated_text, fontsize=font_size)
                    if trans_width > orig_width and orig_width > 0:
                        scale = max(orig_width / trans_width, 0.7)
                        font_size = font_size * scale
                except:
                    pass

                # Insert translated text at the same position
                point = fitz.Point(bbox[0], bbox[1])
                page.insert_text(
                    point,
                    translated_text,
                    fontsize=font_size,
                    fontname="helv",
                    color=color,
                    fontfile=None
                )

                page_replacements += 1
                total_replacements += 1

            except Exception as e:
                print(f"  Error translating '{original_text[:40]}': {e}")

        print(f"  Replacements: {page_replacements}")

    # Save the translated document
    print(f"\nSaving translated PDF to: {output_pdf}")
    doc.save(output_pdf, deflate=True)
    doc.close()

    # Print summary
    print(f"\n" + "=" * 70)
    print(f"Translation Complete!")
    print(f"=" * 70)
    print(f"Total replacements made: {total_replacements}")
    print(f"Total text elements (not translated or same as original): {total_skipped}")
    print(f"Pages processed: {total_pages}")
    print(f"\nOutput: {output_pdf}")

    return total_replacements

def main():
    # File paths
    base_path = r"c:\Users\yichao\Documents\pdfTranslate"
    source_pdf = Path(base_path) / "A-001 - NOTES ET LÉGENDES.pdf"
    output_pdf = Path(base_path) / "A-001 - NOTES AND LEGENDS.pdf"
    translations_json = Path(base_path) / "A-001_translations.json"

    print("=" * 70)
    print("PDF TRANSLATION - A-001 NOTES AND LEGENDS (Version 2)")
    print("=" * 70)

    # Load translations
    print(f"\nLoading translations from: {translations_json}")
    translations = load_translations(str(translations_json))
    print(f"Loaded {len(translations)} translation entries")

    if len(translations) == 0:
        print("ERROR: No translations found. Please check the translations JSON file.")
        return False

    # Apply translations
    print(f"\nSource PDF: {source_pdf}")
    print(f"Output PDF: {output_pdf}")
    print(f"\nStarting translation process...")

    translate_pdf(str(source_pdf), str(output_pdf), translations)

    # Verify output exists
    if Path(output_pdf).exists():
        print(f"\nSuccess! Output file created: {output_pdf}")
        return True
    else:
        print(f"\nError: Output file was not created!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
