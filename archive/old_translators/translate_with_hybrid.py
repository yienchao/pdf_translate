"""
Hybrid Translation Workflow:
1. Extract all unique texts from PDF
2. Try dictionary translation
3. Collect texts that still have French
4. You (Claude Code) translate the remaining French texts
5. Merge new translations into dictionary
6. Generate accent variants for new translations
7. Apply all translations to PDF
"""
from method5_interactive_translation import extract_all_text_from_pdf
from method7_true_hybrid import translate_text_hybrid, load_dictionary, NEW_TRANSLATIONS
import json
import re

def detect_french_words(text):
    """Find French words that remain in text"""
    # Look for uppercase French words with accents or common French words
    french_words = re.findall(r'\b[A-ZÀ-ÿ]{2,}\b', text)

    # Filter out English words and units
    exclude = {'THE', 'AND', 'WITH', 'FOR', 'NOT', 'ALL', 'ARE', 'FROM', 'WALL', 'FLOOR',
               'MM', 'NO', 'MAX', 'MIN', 'IS', 'AR', 'CB', 'BT', 'DIR', 'ENV', 'EPC',
               'OM', 'ME', 'MF', 'RM', 'VAR', 'VRA', 'AA', 'PAV', 'PDD'}

    return [w for w in french_words if w not in exclude and not w.isdigit()]

def find_untranslated_texts(input_pdf):
    """
    Step 1-3: Extract texts, try dictionary, collect what needs translation
    """
    print("="*80)
    print("STEP 1: Extracting unique texts from PDF")
    print("="*80)

    unique_texts = extract_all_text_from_pdf(input_pdf)
    print(f"Found {len(unique_texts)} unique texts")

    print("\n" + "="*80)
    print("STEP 2: Trying dictionary translation")
    print("="*80)

    needs_translation = {}

    for text in unique_texts:
        translated = translate_text_hybrid(text)
        french_words = detect_french_words(translated)

        if french_words:
            needs_translation[text] = {
                "after_dictionary": translated,
                "french_remaining": french_words
            }

    print(f"\nDictionary covered: {len(unique_texts) - len(needs_translation)}/{len(unique_texts)} texts")
    print(f"Need translation: {len(needs_translation)} texts")

    if needs_translation:
        print("\n" + "="*80)
        print("STEP 3: Texts that still need translation:")
        print("="*80)

        for i, (original, info) in enumerate(list(needs_translation.items())[:20], 1):
            print(f"\n{i}. Original: {original}")
            print(f"   After dict: {info['after_dictionary']}")
            print(f"   French words: {', '.join(info['french_remaining'])}")

        if len(needs_translation) > 20:
            print(f"\n... and {len(needs_translation) - 20} more")

        # Save for manual translation
        with open('texts_needing_translation.json', 'w', encoding='utf-8') as f:
            json.dump(needs_translation, f, ensure_ascii=False, indent=2)

        print(f"\n✓ Saved to: texts_needing_translation.json")
        print("\nNext: Translate these texts and save to 'new_translations.json' in format:")
        print('{"FRENCH TEXT": "ENGLISH TEXT"}')

    return needs_translation

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python translate_with_hybrid.py <pdf_path>")
        print("\nExample:")
        print('  python translate_with_hybrid.py "AR-005 - LÉGENDES ET COMPOSITIONS TYPES - ENVELOPPE.pdf"')
    else:
        pdf_path = sys.argv[1]
        find_untranslated_texts(pdf_path)
