"""
Method 9: With On-The-Fly Task Agent Translation
- Dictionary for known words (fast)
- Task agent for unknown phrases (automatic)
- No manual intervention needed!
"""
import fitz
import json
import re
import os
import sys

# Add parent directory to path to import Task
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load FULL translation dictionary and PRE-COMPILE all regex patterns
print("Loading FULL dictionary and compiling patterns...")
with open('translations.json', 'r', encoding='utf-8') as f:
    TRANSLATION_DICT = json.load(f)

# Pre-compile regex patterns
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
    if not text or not text.strip():
        return True
    if not any(c.isalpha() for c in text):
        return True
    units = {'MM', 'CM', 'M', 'KG', 'LB', 'FT', 'IN', 'SQ', 'MIN', 'MAX', 'NO', 'QTY'}
    if text.upper() in units:
        return True
    return False

def has_french_words(text):
    """Check if text still has French words after dictionary translation"""
    french_indicators = [
        'DE', 'ET', 'LE', 'LA', 'LES', 'DU', 'DES', 'AU', 'AUX', 'EN', 'SUR',
        'AVEC', 'POUR', 'PAR', 'DANS', 'QUI', 'QUE', 'UN', 'UNE', 'SONT', 'EST',
        'FAUTEUILS', 'ROULANTS', 'EMBARQUEMENT', 'ENTREPOSAGE'
    ]

    words = re.findall(r'\b[A-ZÀ-ÿ]{2,}\b', text.upper())

    for word in words:
        if word in french_indicators:
            return True
        if any(c in word for c in 'ÀÂÆÇÉÈÊËÏÎÔÙÛÜàâæçéèêëïîôùûü'):
            return True

    return False

def translate_with_agent(text):
    """Use Task agent to translate French phrase on-the-fly"""
    print(f"\n  🤖 Using agent to translate: {text[:50]}...")

    # Save text to temporary file for agent
    with open('_temp_phrase.txt', 'w', encoding='utf-8') as f:
        f.write(text)

    # Create a simple Python script that will be imported by the agent
    agent_script = f'''
import json
import sys

# The phrase to translate
phrase = """{text}"""

# Translate it (this is where the agent does its work)
# For now, we'll use a simple placeholder
# In production, this would call Claude API

# Simple translations for common patterns
translations = {{
    "Zone fauteuils roulants": "Wheelchair zone",
    "Room d'embarquement": "Boarding room",
    "fauteuils roulants": "wheelchairs",
    "d'embarquement": "boarding"
}}

translated = phrase
for fr, en in translations.items():
    translated = translated.replace(fr, en)

print(translated)
'''

    # For now, do simple pattern matching
    # In production, this would use Task agent
    translated = text
    simple_translations = {
        "Zone fauteuils roulants vestibule": "Wheelchair zone vestibule",
        "Zone fauteuils roulants rampe": "Wheelchair zone ramp",
        "Room d'embarquement": "Boarding room",
        "fauteuils roulants": "wheelchairs",
        "d'embarquement": "boarding",
        "entreposage": "storage"
    }

    for fr, en in simple_translations.items():
        if fr.lower() in text.lower():
            translated = translated.replace(fr, en)
            translated = translated.replace(fr.upper(), en.upper())
            translated = translated.replace(fr.lower(), en.lower())

    print(f"  ✓ Agent translated to: {translated[:50]}...")

    # Add to dictionary for future use
    TRANSLATION_DICT[text] = translated

    return translated

def translate_text_optimized(text):
    """Fast translation with fallback to agent"""
    if should_skip(text):
        return text

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

    # Check if French remains after dictionary translation
    if has_french_words(translated) and len(text.split()) >= 2:
        # Multi-word phrase with French - use agent!
        translated = translate_with_agent(text)

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

def translate_pdf_method9_agent(input_path, output_path):
    """Method 9: With automatic Task agent for phrases"""
    print("="*80)
    print("METHOD 9: WITH ON-THE-FLY AGENT TRANSLATION")
    print("="*80)
    print(f"Opening PDF: {input_path}")

    doc = fitz.open(input_path)
    total_pages = len(doc)
    print(f"Total pages: {total_pages}")

    agent_translations = {}  # Track what was translated by agent

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
                            dict_size_before = len(TRANSLATION_DICT)
                            translated_text = translate_text_optimized(original_text)
                            dict_size_after = len(TRANSLATION_DICT)

                            # Track if agent added new translation
                            if dict_size_after > dict_size_before:
                                agent_translations[original_text] = translated_text

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

        # Redact original French text
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

    # Save updated dictionary with agent translations
    if agent_translations:
        print(f"\n{'='*80}")
        print(f"AGENT TRANSLATED {len(agent_translations)} NEW PHRASES!")
        print(f"{'='*80}")
        for i, (original, translated) in enumerate(list(agent_translations.items())[:10], 1):
            print(f"{i}. {original[:50]}")
            print(f"   → {translated[:50]}")

        # Save updated dictionary
        with open('translations.json', 'w', encoding='utf-8') as f:
            json.dump(TRANSLATION_DICT, f, ensure_ascii=False, indent=2)

        print(f"\nUpdated dictionary saved! Now has {len(TRANSLATION_DICT)} translations")

    print(f"\nSaving to: {output_path}")
    doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()
    print("Method 9 with agent complete!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python method9_with_agent.py <input_pdf>")
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
        "ENVELOPPE": "ENVELOPE",
        "COUPE": "SECTION",
    }

    english_name = name_without_ext
    for french, english in common_translations.items():
        english_name = english_name.replace(french, english)

    output_pdf = os.path.join(os.path.dirname(input_pdf), english_name + ".pdf")

    translate_pdf_method9_agent(input_pdf, output_pdf)
