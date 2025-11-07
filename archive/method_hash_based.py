"""
Hash-Based Translation Memory System
- Uses content hashing to build a master translation dictionary
- ALL text (words, phrases, sentences) is hashed and stored once, reused everywhere
- Works across all PDFs, resilient to structure changes
- Dictionary grows organically with each translation
"""
import fitz
import json
import hashlib
import os
import sys

# Master translation memory (hash-based)
TRANSLATION_MEMORY_FILE = 'translation_memory.json'

print("Loading translation memory...")

# Load or create translation memory (hash ALL text)
if os.path.exists(TRANSLATION_MEMORY_FILE):
    with open(TRANSLATION_MEMORY_FILE, 'r', encoding='utf-8') as f:
        TRANSLATION_MEMORY = json.load(f)
    print(f"Translation memory loaded: {len(TRANSLATION_MEMORY)} translations")
else:
    TRANSLATION_MEMORY = {}
    print("Translation memory: Starting fresh")

def normalize_text(text):
    """Normalize text for consistent hashing"""
    # Strip whitespace, normalize spaces
    normalized = ' '.join(text.split())
    return normalized

def hash_text(text):
    """Create hash of text for dictionary lookup"""
    normalized = normalize_text(text)
    # Use SHA256 for reliable hashing
    hash_obj = hashlib.sha256(normalized.encode('utf-8'))
    return hash_obj.hexdigest()

def should_skip(text):
    if not text or not text.strip():
        return True
    if not any(c.isalpha() for c in text):
        return True

    # Skip units
    units = {'MM', 'CM', 'M', 'KG', 'LB', 'FT', 'IN', 'SQ', 'MIN', 'MAX', 'NO', 'QTY', 'TYP', 'REF'}
    if text.upper() in units:
        return True

    # Skip technical codes ending with "..." or "." (like BAP..., BBO..., M�, F�, etc.)
    if text.endswith('...') or text.endswith('....') or text.endswith('......'):
        return True

    # Skip very short codes (1-3 chars with punctuation like "A...", "M�", "V", "XXX")
    clean = text.strip('.�')
    if len(clean) <= 3 and not ' ' in text:  # Single "words" 3 chars or less
        return True

    # Skip technical codes/acronyms (2-4 chars with special chars like �)
    if len(text) <= 4 and '�' in text:
        return True

    # Skip short technical codes (2-3 lowercase letters)
    if len(text) <= 3 and text.islower() and text.isalpha():
        return True

    return False

def has_french(text):
    """Quick check if text likely has French"""
    french_indicators = [
        # Common French words (articles, prepositions, conjunctions)
        'DE', 'ET', 'LE', 'LA', 'LES', 'DU', 'DES', 'AU', 'AUX', 'EN', 'SUR',
        'AVEC', 'POUR', 'PAR', 'DANS', 'TOUS', 'TOUTES', 'TOUT', 'SONT', 'EST',
        # Architectural terms
        'PARTIE', 'NOUVELLE', 'NOUVEAU', 'NOUVEL', 'EXISTANTE', 'EXISTANT',
        'CLOISON', 'PLAFOND', 'TOITURE', 'MUR', 'PORTE', 'CADRE',
        'ZONE', 'STRUCTURE', 'APPARENTE', 'APPARENT',
        'POUTRELLES', 'SOLINAGE', 'LINTEAU',
        'IDENTIFICATION', 'MOBILIER', 'ÉQUIPEMENTS', 'EQUIPEMENTS',
        'LUMINAIRE', 'APPAREILS', 'DIFFUSEUR', 'GICLEUR',
        'RETOUR', 'LIMITE', 'PEINTURE',
        'CAISSON', 'IGNIFUGE', 'ENTREPLAFOND',
        'NUMÉRO', 'NUMERO', 'RÉVISIONS', 'REVISIONS',
        'SUPERFÍCIE', 'SUPERFICIE', 'REQUISE',
        'AIR', 'OXYGÈNE', 'OXYGENE', 'VIDE', 'MÉDICAL', 'MEDICAL',
        'INTERRUPTEUR', 'INTERCOM', 'APPEL', 'GARDE',
        'PRISE', 'ÉLECTRIQUE', 'ELECTRIQUE', 'DATA', 'TÉLÉPHONE', 'TELEPHONE',
        'ÉLÉVATIONS', 'ELEVATIONS', 'INTÉRIEURES', 'INTERIEURES',
        'BASSE', 'HAUTEUR', 'NIVEAU', 'PLANCHER',
        'HAUT', 'BAS',
        'AXE', 'STRUCTURAL', 'STRUCTURALE',
        'NOUVEAUX', 'NOUVELLES', 'EXISTANTS', 'EXISTANTES',
        'DÉMOLIR', 'DEMOLIR', 'CONSERVER', 'ENLEVER', 'RÉINSTALLER', 'REINSTALLER',
        'BLOCS', 'BÉTON', 'BETON',
        'SOL', 'REMBLAYÉ', 'REMBLAYE',
        'ASSEMBLAGE', 'ASSEMBLAGES', 'ENVELOPPE',
        'COUPE', 'ARRIÈRE', 'ARRIERE', 'PLAN',
        'TOILES', 'SOLAIRES', 'DOUBLE', 'PLAQUE', 'FERMETURE',
        'FONDS', 'VISSAGE', 'IDENTIFIÉS', 'IDENTIFIES', 'DESSINS', 'LISTES',
        'ACCESSOIRES', 'FOURNIS', 'INSTALLÉS', 'INSTALLES', 'PROPRIÉTAIRE', 'PROPRIETAIRE',
        'ABRÉVIATION', 'ABREVIATION', 'ENTREPRENEUR', 'FOURNIR', 'INSTALLER',
        'VALIDER', 'POSITIONNEMENT', 'FINAL', 'CHANTIER', 'AVANT', 'INSTALLATION',
        'AUTRE', 'PART', 'RESPONSABILITÉ', 'RESPONSABILITE',
        'AUTRES', 'TOUS', 'ÉLÉMENTS', 'ELEMENTS', 'INTÉGRER', 'INTEGRER',
        'OUVRAGE', 'PRÉVUS', 'PREVUS', 'DOCUMENTS', 'DERNIERS',
        'POSITIONNÉS', 'POSITIONNES'
    ]
    words = text.upper().split()
    for word in words:
        # Remove parentheses and punctuation for matching
        clean_word = word.strip('(),.;:!?')
        if clean_word in french_indicators:
            return True
        # Check for accented characters (proper or corrupted)
        if any(c in word for c in 'ÀÂÆÇÉÈÊËÏÎÔÙÛÜàâæçéèêëïîôùûüÿœ�'):
            return True
    return False

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

def translate_pdf_hash_based(input_path, output_path):
    """Hash-based translation with master dictionary"""
    print("="*80)
    print("HASH-BASED TRANSLATION MEMORY SYSTEM")
    print("="*80)
    print(f"Opening PDF: {input_path}")

    pdf_code = os.path.basename(input_path).split(' - ')[0]

    doc = fitz.open(input_path)
    total_pages = len(doc)
    print(f"Total pages: {total_pages}")
    print(f"PDF code: {pdf_code}")
    print(f"Master translation memory: {len(TRANSLATION_MEMORY)} existing translations")

    # Collect text that needs translation
    text_needing_translation = {}  # {hash: original_text}
    all_text_elements = []

    # Statistics
    stats = {
        'total_elements': 0,
        'skipped': 0,
        'cached': 0,
        'new': 0
    }

    # PHASE 1: Extract and categorize all text
    print("\n" + "="*80)
    print("PHASE 1: EXTRACTING TEXT")
    print("="*80)

    for page_num in range(total_pages):
        print(f"\nPage {page_num + 1}/{total_pages}...")
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
            stats['total_elements'] += 1

            if should_skip(text) or repl.get("is_superscript"):
                # Skip this text (numbers, units, technical codes, superscripts)
                repl["translated"] = text
                repl["page"] = page_num
                all_text_elements.append(repl)
                stats['skipped'] += 1

            else:
                # Assume ALL other text is French and needs translation
                # (except numbers/codes already filtered by should_skip)
                text_hash = hash_text(text)

                if text_hash in TRANSLATION_MEMORY:
                    # Cache hit! Reuse existing translation
                    repl["translated"] = TRANSLATION_MEMORY[text_hash]
                    repl["page"] = page_num
                    all_text_elements.append(repl)
                    stats['cached'] += 1
                    print(f"  [CACHED] {text[:50]}...")
                else:
                    # Cache miss - needs translation
                    text_needing_translation[text_hash] = text
                    repl["translated"] = f"__HASH_{text_hash}__"
                    repl["page"] = page_num
                    all_text_elements.append(repl)
                    stats['new'] += 1
                    print(f"  [NEW] {text[:50]}...")

    print("\n" + "="*80)
    print("PHASE 1 COMPLETE - STATISTICS")
    print("="*80)
    print(f"Total text elements: {stats['total_elements']}")
    print(f"  Skipped (no French): {stats['skipped']}")
    print(f"  Cached (hash hit): {stats['cached']}")
    print(f"  New (need translation): {stats['new']}")

    cache_hit_rate = 0
    total_french = stats['cached'] + stats['new']
    if total_french > 0:
        cache_hit_rate = (stats['cached'] / total_french) * 100
    print(f"\nCache hit rate: {cache_hit_rate:.1f}%")

    # PHASE 2: Translate new text
    if text_needing_translation:
        print("\n" + "="*80)
        print("PHASE 2: TRANSLATION NEEDED")
        print("="*80)
        print(f"{len(text_needing_translation)} unique text items need translation")

        # Save text for manual/agent translation
        pending_file = f"{pdf_code}_pending_translations.json"
        with open(pending_file, 'w', encoding='utf-8') as f:
            json.dump(text_needing_translation, f, ensure_ascii=False, indent=2)

        print(f"\nSaved to: {pending_file}")
        print("\n**ACTION REQUIRED:**")
        print(f"1. Translate all text in {pending_file}")
        print(f"   Format: {{\"hash\": \"translated_text\", ...}}")
        print(f"2. Merge into {TRANSLATION_MEMORY_FILE}")
        print("3. Re-run this script to complete translation")
        print("\nExiting...")
        return

    # PHASE 3: Apply translations
    print("\n" + "="*80)
    print("PHASE 3: APPLYING TRANSLATIONS")
    print("="*80)

    for page_num in range(total_pages):
        print(f"\nPage {page_num + 1}/{total_pages}...")
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

    print(f"\n" + "="*80)
    print(f"Saving to: {output_path}")
    doc.save(output_path, garbage=4, deflate=True, clean=True)
    doc.close()

    print("="*80)
    print("TRANSLATION COMPLETE!")
    print("="*80)
    print(f"Master translation memory now has: {len(TRANSLATION_MEMORY)} translations")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python method_hash_based.py <input_pdf> <output_pdf>")
        print("\nExample:")
        print('  python method_hash_based.py "A-001 - NOTES ET LÉGENDES.pdf" "A-001 - OUTPUT.pdf"')
        sys.exit(1)

    translate_pdf_hash_based(sys.argv[1], sys.argv[2])
