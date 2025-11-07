"""
Extract all text from PDF and identify remaining French words/phrases
"""
import fitz
import json
import re
from collections import Counter

def is_french_word(word):
    """Check if a word is likely French"""
    # Common French words (case-insensitive)
    french_words = {
        'DE', 'ET', 'LE', 'LA', 'LES', 'DU', 'DES', 'AU', 'AUX', 'EN', 'SUR',
        'AVEC', 'POUR', 'PAR', 'DANS', 'TOUS', 'TOUTES', 'TOUT', 'SONT', 'EST',
        'UN', 'UNE', 'CE', 'CES', 'QUI', 'QUE', 'DANS', 'PLUS', 'MOINS',
        'COMME', 'MAIS', 'OU', 'OÙ', 'SI', 'NE', 'PAS', 'TRÈS', 'BIEN',
        'FAIRE', 'ÊTRE', 'AVOIR', 'PEUT', 'SANS', 'SOUS', 'ENTRE', 'AVANT',
        'APRÈS', 'PENDANT', 'SELON', 'CHEZ', 'VERS', 'AUTRES', 'AUTRE',
        'CHAQUE', 'PLUSIEURS', 'QUELQUES', 'MÊME', 'CETTE', 'CET',
        'VOIR', 'PLAN', 'NOTE', 'NOTES', 'LÉGENDE', 'LÉGENDES', 'DÉTAIL',
        'DÉTAILS', 'FEUILLE', 'ÉCHELLE', 'NIVEAU', 'DALLE', 'MUR', 'MURS',
        'PLAFOND', 'SOL', 'PORTE', 'PORTES', 'FENÊTRE', 'FENÊTRES',
        'ESCALIER', 'ESCALIERS', 'ASCENSEUR', 'TOITURE', 'FONDATION',
        'FONDATIONS', 'BÉTON', 'ACIER', 'BOIS', 'MÉTAL', 'ALUMINIUM',
        'ISOLANT', 'ISOLATION', 'FINITION', 'FINITIONS', 'PEINTURE',
        'REVÊTEMENT', 'CARRELAGE', 'PLANCHER', 'BARDAGE', 'COUVERTURE',
        'ÉTANCHÉITÉ', 'DRAINAGE', 'VENTILATION', 'CHAUFFAGE', 'PLOMBERIE',
        'ÉLECTRICITÉ', 'ÉPAISSEUR', 'LARGEUR', 'LONGUEUR', 'HAUTEUR',
        'DIAMÈTRE', 'RAYON', 'SURFACE', 'VOLUME', 'POIDS', 'CHARGE',
        'RÉSISTANCE', 'PRESSION', 'TEMPÉRATURE', 'HUMIDITÉ',
        'CONFORMÉMENT', 'SPÉCIFICATIONS', 'NORMES', 'RÈGLEMENTS',
        'EXIGENCES', 'RECOMMANDATIONS', 'PRESCRIPTIONS', 'INSTRUCTIONS',
        'BORDEREAU', 'ANALYSE', 'CADRES', 'OUVERTURES', 'FINIS',
        'WATERPROOFING', 'INTERFACES'
    }

    word_upper = word.upper()

    # Check against French word list
    if word_upper in french_words:
        return True

    # Check for French accented characters
    french_chars = 'ÀÂÆÇÉÈÊËÏÎÔÙÛÜàâæçéèêëïîôùûüÿœŒ'
    if any(c in word for c in french_chars):
        return True

    # Check for common French suffixes
    french_suffixes = ['TION', 'SION', 'MENT', 'ANCE', 'ENCE', 'EUR', 'TEUR', 'TRICE']
    for suffix in french_suffixes:
        if word_upper.endswith(suffix) and len(word) > 5:
            # More likely French if it has these endings
            return True

    return False

def extract_and_analyze_pdf(pdf_path):
    """Extract all text and identify French words"""
    print("="*80)
    print(f"ANALYZING PDF: {pdf_path}")
    print("="*80)

    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    print(f"\nTotal pages: {total_pages}\n")

    all_text = []
    french_phrases = []
    page_analysis = []

    # Extract text from all pages
    for page_num in range(total_pages):
        print(f"Extracting page {page_num + 1}/{total_pages}...")
        page = doc[page_num]

        # Get text with position info
        text_instances = page.get_text("dict")
        blocks = text_instances.get("blocks", [])

        page_text = []
        page_french = []

        for block in blocks:
            if block.get("type") == 0:  # Text block
                for line in block.get("lines", []):
                    line_text = ""
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        if text:
                            line_text += text + " "
                            page_text.append(text)

                    # Check if line contains French
                    line_text = line_text.strip()
                    if line_text:
                        words = re.findall(r'\b[A-Za-zÀ-ÿ]+\b', line_text)
                        french_words_in_line = [w for w in words if is_french_word(w)]

                        if french_words_in_line:
                            page_french.append({
                                "text": line_text,
                                "french_words": french_words_in_line
                            })

        all_text.extend(page_text)
        if page_french:
            french_phrases.extend(page_french)
            page_analysis.append({
                "page": page_num + 1,
                "french_items": page_french
            })

    doc.close()

    # Analyze all text
    print("\n" + "="*80)
    print("ANALYSIS RESULTS")
    print("="*80)

    # Count words
    all_words = []
    for text in all_text:
        words = re.findall(r'\b[A-Za-zÀ-ÿ]+\b', text)
        all_words.extend(words)

    total_word_count = len(all_words)

    # Identify French words
    french_words_found = []
    english_words_found = []

    for word in all_words:
        if len(word) <= 2:  # Skip very short words
            continue
        if is_french_word(word):
            french_words_found.append(word)
        else:
            english_words_found.append(word)

    french_count = len(french_words_found)
    english_count = len(english_words_found)

    print(f"\nWORD COUNT SUMMARY:")
    print(f"  Total words extracted: {total_word_count}")
    print(f"  French words: {french_count}")
    print(f"  English words: {english_count}")
    print(f"  Other (numbers, codes, etc.): {total_word_count - french_count - english_count}")

    if french_count > 0:
        percentage = (french_count / (french_count + english_count)) * 100
        print(f"  French percentage: {percentage:.1f}%")

    # Show most common French words
    print(f"\nMOST COMMON FRENCH WORDS:")
    french_counter = Counter([w.upper() for w in french_words_found])
    for word, count in french_counter.most_common(30):
        print(f"  {word}: {count} times")

    # Show French phrases by page
    print(f"\n" + "="*80)
    print("FRENCH TEXT BY PAGE")
    print("="*80)

    for page_info in page_analysis:
        print(f"\nPAGE {page_info['page']}:")
        print("-" * 80)
        for item in page_info['french_items']:
            french_words_str = ", ".join(set(item['french_words']))
            print(f"  TEXT: {item['text']}")
            print(f"  FRENCH: [{french_words_str}]")
            print()

    # Save detailed results to JSON
    output_file = "french_analysis_results.json"
    results = {
        "pdf_file": pdf_path,
        "total_pages": total_pages,
        "word_count": {
            "total": total_word_count,
            "french": french_count,
            "english": english_count,
            "other": total_word_count - french_count - english_count
        },
        "french_words_frequency": dict(french_counter.most_common(50)),
        "pages_with_french": page_analysis,
        "all_french_phrases": french_phrases
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n" + "="*80)
    print(f"Detailed results saved to: {output_file}")
    print("="*80)

    return results

if __name__ == "__main__":
    pdf_path = r"translated_pdfs\A-001 - NOTES ET LEGENDS.pdf"
    extract_and_analyze_pdf(pdf_path)
