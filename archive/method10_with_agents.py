"""
Method 10: Hash-Based Translation - Works with Task Agents
NO API KEYS NEEDED - Uses Claude Code's built-in Task agents
"""
import fitz
import json
import hashlib
import os
import sys

# Master translation memory (hash-based)
TRANSLATION_MEMORY_FILE = 'translation_memory.json'

print("Loading translation memory...")

# Load or create translation memory
if os.path.exists(TRANSLATION_MEMORY_FILE):
    with open(TRANSLATION_MEMORY_FILE, 'r', encoding='utf-8') as f:
        TRANSLATION_MEMORY = json.load(f)
    print(f"Translation memory loaded: {len(TRANSLATION_MEMORY)} translations")
else:
    TRANSLATION_MEMORY = {}
    print("Translation memory: Starting fresh")

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
    if not text or not text.strip():
        return True
    if not any(c.isalpha() for c in text):
        return True

    units = {'MM', 'CM', 'M', 'KG', 'LB', 'FT', 'IN', 'SQ', 'MIN', 'MAX', 'NO', 'QTY', 'TYP', 'REF'}
    if text.upper() in units:
        return True

    if text.endswith('...') or text.endswith('....'):
        return True

    clean = text.strip('.…')
    if len(clean) <= 3 and not ' ' in text:
        return True

    if len(text) <= 4 and '…' in text:
        return True

    if len(text) <= 3 and text.islower() and text.isalpha():
        return True

    return False

def has_french(text):
    """Quick check if text likely has French"""
    french_indicators = [
        'DE', 'ET', 'LE', 'LA', 'LES', 'DU', 'DES', 'AU', 'AUX', 'EN', 'SUR',
        'AVEC', 'POUR', 'PAR', 'DANS', 'TOUS', 'TOUTES', 'TOUT', 'SONT', 'EST',
        'PARTIE', 'NOUVELLE', 'NOUVEAU', 'EXISTANTE', 'EXISTANT',
        'CLOISON', 'PLAFOND', 'TOITURE', 'MUR', 'PORTE', 'CADRE', 'VOIR'
    ]
    words = text.upper().split()
    for word in words:
        if word in french_indicators:
            return True
        if any(c in word for c in 'ÀÂÆÇÉÈÊËÏÎÔÙÛÜÀÂÆÇÉÈÊËÏÎÔÙÛÜŸŒ…'):
            return True
    return False

def translate_pdf_hash_based(input_path, output_path):
    """Main translation function"""
    doc = fitz.open(input_path)
    total_pages = len(doc)

    # Extract PDF code from filename
    pdf_code = os.path.basename(input_path).split(' - ')[0].replace(' ', '-')

    print("="*80)
    print("METHOD 10: HASH-BASED TRANSLATION WITH TASK AGENTS")
    print("="*80)
    print(f"Opening PDF: {input_path}")
    print(f"Total pages: {total_pages}")
    print(f"PDF code: {pdf_code}")
    print(f"Master translation memory: {len(TRANSLATION_MEMORY)} existing translations")

    # Collect text that needs translation
    text_needing_translation = {}
    all_text_elements = []

    print(f"\n{'='*80}")
    print(f"PHASE 1: EXTRACTING TEXT")
    print(f"{'='*80}\n")

    total_elements = 0
    skipped = 0
    cached = 0
    needs_translation = 0

    for page_num in range(total_pages):
        page = doc[page_num]
        print(f"Page {page_num + 1}/{total_pages}...")

        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if block.get("type") != 0:
                continue

            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"].strip()

                    if should_skip(text):
                        skipped += 1
                        continue

                    total_elements += 1

                    repl = {
                        "original": text,
                        "bbox": span["bbox"],
                        "size": span["size"],
                        "color": span["color"],
                        "page": page_num
                    }

                    text_hash = hash_text(text)

                    if text_hash in TRANSLATION_MEMORY:
                        repl["translated"] = TRANSLATION_MEMORY[text_hash]
                        all_text_elements.append(repl)
                        cached += 1
                        print(f"  [CACHED] {text[:60]}...")
                    else:
                        text_needing_translation[text_hash] = text
                        repl["translated"] = None
                        repl["hash"] = text_hash
                        all_text_elements.append(repl)
                        needs_translation += 1
                        print(f"  [NEW] {text[:60]}...")

    print(f"\n{'='*80}")
    print(f"PHASE 1 COMPLETE - STATISTICS")
    print(f"{'='*80}")
    print(f"Total text elements: {total_elements}")
    print(f"  Skipped (no French): {skipped}")
    print(f"  Cached (hash hit): {cached}")
    print(f"  New (need translation): {needs_translation}")
    if total_elements > 0:
        print(f"\nCache hit rate: {cached/total_elements*100:.1f}%")

    # If text needs translation, save pending file and exit
    if text_needing_translation:
        print(f"\n{'='*80}")
        print(f"PHASE 2: TRANSLATION NEEDED")
        print(f"{'='*80}")

        pending_file = f"{pdf_code}_pending_translations.json"
        with open(pending_file, 'w', encoding='utf-8') as f:
            json.dump(text_needing_translation, f, ensure_ascii=False, indent=2)

        print(f"\nSaved {len(text_needing_translation)} items to: {pending_file}")
        print(f"\n**USE TASK AGENT TO TRANSLATE:**")
        print(f"Ask Claude Code: 'Use Task agent with haiku to translate {pending_file}'")
        print(f"Agent should create: {pdf_code}_translated.json")
        print(f"\nThen run: python merge_translations.py {pending_file}")
        print(f"Then re-run this script to build PDF")
        print("\nExiting...")
        doc.close()
        return

    # All translations available - build PDF
    print(f"\n{'='*80}")
    print(f"PHASE 2: ALL TRANSLATIONS AVAILABLE")
    print(f"{'='*80}")
    print(f"100% cache hit! Building PDF...\n")

    print(f"{'='*80}")
    print(f"PHASE 3: APPLYING TRANSLATIONS")
    print(f"{'='*80}\n")

    for page_num in range(total_pages):
        page = doc[page_num]
        print(f"Page {page_num + 1}/{total_pages}...")

        page_elements = [e for e in all_text_elements if e["page"] == page_num]

        # Draw white boxes over original text
        for elem in page_elements:
            bbox = elem["bbox"]
            page.draw_rect(bbox, color=(1, 1, 1), fill=(1, 1, 1))

        # Insert translated text
        inserted = 0
        for elem in page_elements:
            bbox = elem["bbox"]
            translated_text = elem["translated"]
            font_size = elem["size"]
            color = elem["color"]

            if translated_text:
                try:
                    font = fitz.Font("helv")
                    trans_width = font.text_length(translated_text, fontsize=font_size)
                    bbox_width = bbox[2] - bbox[0]

                    if trans_width > bbox_width:
                        font_size = font_size * (bbox_width / trans_width) * 0.95

                    tw = fitz.TextWriter(page.rect)
                    tw.append(
                        (bbox[0], bbox[3] - 2),
                        translated_text,
                        font=font,
                        fontsize=font_size
                    )
                    tw.write_text(page)
                    inserted += 1
                except Exception as e:
                    print(f"    Warning: Could not insert '{translated_text[:30]}': {e}")

        print(f"  Inserted {inserted}/{len(page_elements)} text elements")

    print(f"\n{'='*80}")
    print(f"Saving to: {output_path}")
    print(f"{'='*80}")
    doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()

    print("="*80)
    print("TRANSLATION COMPLETE!")
    print("="*80)
    print(f"Master translation memory now has: {len(TRANSLATION_MEMORY)} translations")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python method10_with_agents.py <input_pdf> <output_pdf>")
        print("\nExample:")
        print('  python method10_with_agents.py "A-001 - NOTES ET LÉGENDES.pdf" "A-001 - OUTPUT.pdf"')
        sys.exit(1)

    translate_pdf_hash_based(sys.argv[1], sys.argv[2])
