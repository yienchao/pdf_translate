"""
Method 10: HYBRID Translation
- Dictionary for single words and short phrases (fast)
- Task agent for complete sentences (accurate, no Franglish)
- Best of both worlds!
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

# Pre-compile ALL patterns (including complete sentences now)
COMPILED_PATTERNS = []
print("Compiling all patterns (words, phrases, and sentences)...")
for french, english in sorted(TRANSLATION_DICT.items(), key=lambda x: len(x[0]), reverse=True):
    # For text with corrupted encoding (�), don't use word boundaries
    # They don't work properly with the Unicode replacement character
    if '\ufffd' in french or '�' in french or len(french.split()) >= 3:
        # No word boundary for corrupted text or multi-word phrases
        pattern = re.compile(re.escape(french), re.IGNORECASE)
        COMPILED_PATTERNS.append((pattern, english))
    else:
        # Use word boundary for clean single words
        try:
            pattern = re.compile(r'\b' + re.escape(french) + r'\b', re.IGNORECASE)
            COMPILED_PATTERNS.append((pattern, english))
        except:
            pattern = re.compile(re.escape(french), re.IGNORECASE)
            COMPILED_PATTERNS.append((pattern, english))

print(f"Ready! {len(COMPILED_PATTERNS)} patterns compiled (words + sentences)")

# Cache for sentences translated by agents
SENTENCE_CACHE = {}

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
        'AVEC', 'POUR', 'PAR', 'DANS', 'QUI', 'QUE', 'UN', 'UNE', 'SONT', 'EST',
        'TOUS', 'TOUTES', 'TOUT'
    ]

    words = re.findall(r'\b[A-ZÀ-ÿ]{2,}\b', text.upper())

    for word in words:
        if word in french_indicators:
            return True
        # Check for accented characters (both proper and corrupted)
        if any(c in word for c in 'ÀÂÆÇÉÈÊËÏÎÔÙÛÜàâæçéèêëïîôùûüÿœ�'):
            return True

    return False

def is_sentence(text):
    """Check if text is a complete sentence (multiple words)"""
    words = text.split()
    return len(words) >= 4  # 4+ words = sentence, use agent

def translate_sentence_with_agent(text):
    """
    For now, collect sentences to translate in batch
    In production, this would call Claude API
    """
    # Check cache
    if text in SENTENCE_CACHE:
        return SENTENCE_CACHE[text]

    # Mark for agent translation
    print(f"  [SENTENCE] Needs agent: {text[:60]}...")

    # For now, return original and collect for batch
    SENTENCE_CACHE[text] = text  # Will be translated in batch
    return text

def translate_text_hybrid(text):
    """Hybrid: Dictionary for words, agents for sentences"""
    if should_skip(text):
        return text

    # First, try dictionary translation
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

    # Check if it's a sentence and still has French
    if is_sentence(translated) and has_french_words(translated):
        # Use agent for complete sentence
        translated = translate_sentence_with_agent(text)

    return translated

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

        merged_translated = translate_text_hybrid(merged_text)

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

def translate_pdf_hybrid(input_path, output_path):
    """Method 10: Hybrid dictionary + agents"""
    print("="*80)
    print("METHOD 10: HYBRID TRANSLATION (Dictionary + Agents)")
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
                            replacements.append({
                                "original": original_text,
                                "bbox": span.get("bbox"),
                                "size": span.get("size"),
                                "color": span.get("color", 0),
                            })

        print(f"Found {len(replacements)} text elements")

        replacements = merge_overlapping_spans(replacements)
        print(f"After merging: {len(replacements)} text elements")

        # Redact original
        for repl in replacements:
            bbox = repl["bbox"]
            rect = fitz.Rect(bbox)
            page.add_redact_annot(rect)

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

            if translated_width > original_width:
                scale_factor = original_width / translated_width
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

    # Report sentences that need agent translation
    if SENTENCE_CACHE:
        print(f"\n{'='*80}")
        print(f"FOUND {len(SENTENCE_CACHE)} SENTENCES THAT NEED AGENT TRANSLATION")
        print(f"{'='*80}")

        # Save to file for batch translation
        with open('sentences_for_agents.json', 'w', encoding='utf-8') as f:
            json.dump(SENTENCE_CACHE, f, ensure_ascii=False, indent=2)

        print("Saved to: sentences_for_agents.json")
        print("\nSample (first 10):")
        for i, text in enumerate(list(SENTENCE_CACHE.keys())[:10], 1):
            print(f"  {i}. {text[:80]}")

        print("\nNext steps:")
        print("1. Translate sentences_for_agents.json with Task agent")
        print("2. Merge into translations.json")
        print("3. Re-run translation")

    print(f"\nSaving to: {output_path}")
    doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()
    print("Method 10 hybrid complete!")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python method10_hybrid.py <input_pdf> <output_pdf>")
        sys.exit(1)

    translate_pdf_hybrid(sys.argv[1], sys.argv[2])
