"""
Identify faulty translations in the dictionary that need to be fixed.

Finds:
1. Identity mappings (French -> French)
2. Partial translations (Franglais)
3. Corrupted text (encoding issues)
"""

import json
import os

def has_french_indicators(text):
    """Check if text has French words"""
    french_words = [
        'VOIR', 'POUR', 'DANS', 'AVEC', 'DE', 'DES', 'LES', 'ET', 'SONT',
        'PORTE', 'PORTES', 'CADRE', 'CADRES', 'DÉTAILS', 'PLAN', 'NOTES',
        'AU', 'DU', 'LA', 'LE', 'SUR', 'PAR', 'TOUS', 'EST', 'À', 'UN', 'UNE',
        'RIGIDE', 'TYPE', 'MUR', 'MURS', 'NIVEAU', 'NIVEAUX', 'OUEST', 'EST',
        'ISOLANT', 'ACIER', 'BÉTON', 'ALUMINIUM', 'PROFILÉ', 'JETÉE',
        'ÉPAISSEUR', 'CLOISON', 'SOUS', 'DALLE', 'ENCASTRÉ', 'COFFRET',
        'ROBINET', 'MANOMÈTRES', 'FEUILLE', 'PLAFOND', 'PLANCHER',
        'ESCALIERS', 'TOILETTES', 'EXTINCTEUR', 'DRAINAGE', 'FONDATION',
        'ÉCLAIRAGE', 'APPAREIL', 'SOFFITE', 'EXTÉRIEUR', 'INTÉRIEUR',
        'ENTREPRENEUR', 'CHARPENTE', 'STRUCTURE', 'PORTEUSE', 'INCLUE',
        'PROTECTION', 'IGNIFUGE', 'APPLIQUÉE', 'LIMITENT', 'AGRANDIS'
    ]

    text_upper = text.upper()
    words = text_upper.split()

    for word in words:
        clean = word.strip('.,;:()[]{}!?-/')
        if clean in french_words:
            return True
        # Check for accented chars
        if any(c in word for c in 'ÀÂÆÇÉÈÊËÏÎÔÙÛÜàâæçéèêëïîôùûüÿœ�'):
            return True

    return False

def has_encoding_corruption(text):
    """Check for encoding corruption markers"""
    markers = ['�', 'NOTN', 'OFE', 'SIC,', 'pb�', 'bb�', 'pm�', 'eb�', 'lm�']
    return any(m in text for m in markers)

def is_likely_proper_noun(text):
    """Check if text is likely a proper noun (should stay as-is)"""
    proper_nouns = [
        'MONTRÉAL-TRUDEAU',
        'SDK',
        'BOUTHILLETTE PARIZEAU',
        'YUL',
        'NFPA'
    ]

    text_upper = text.upper()
    for noun in proper_nouns:
        if noun in text_upper:
            return True

    return False

def categorize_fault(french, english):
    """Categorize the type of fault"""
    # Identity mapping
    if french == english:
        if is_likely_proper_noun(french):
            return "proper_noun", "OK - proper noun"
        else:
            return "identity", "French -> French (not translated)"

    # Encoding corruption
    if has_encoding_corruption(english):
        return "corrupted", "Encoding corruption detected"

    # Partial translation (Franglais)
    if has_french_indicators(english):
        return "partial", "Still contains French words"

    # Seems OK
    return "ok", "Appears correct"

def analyze_dictionary():
    """Analyze the translation dictionary for faults"""
    dict_path = 'method9_data/translations.json'

    print("Loading dictionary...")
    with open(dict_path, 'r', encoding='utf-8') as f:
        translation_dict = json.load(f)

    print(f"Total entries: {len(translation_dict)}\n")

    # Categorize all entries
    categories = {
        "identity": [],
        "proper_noun": [],
        "partial": [],
        "corrupted": [],
        "ok": []
    }

    for french, english in translation_dict.items():
        category, reason = categorize_fault(french, english)
        categories[category].append({
            "french": french,
            "english": english,
            "reason": reason
        })

    # Print summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    for cat, items in categories.items():
        print(f"{cat:15s}: {len(items):4d} entries")

    # Show examples and save faulty ones
    faulty_translations = {}

    print("\n" + "="*80)
    print("IDENTITY MAPPINGS (needs translation)")
    print("="*80)
    for i, item in enumerate(categories["identity"][:20], 1):
        french = item["french"]
        display = french[:70] + "..." if len(french) > 70 else french
        try:
            print(f"{i:3d}. {display}")
        except:
            print(f"{i:3d}. [encoding issue]")
        faulty_translations[french] = ""  # Needs translation

    print(f"\n... and {len(categories['identity']) - 20} more") if len(categories["identity"]) > 20 else None

    print("\n" + "="*80)
    print("PARTIAL TRANSLATIONS (Franglais - needs fix)")
    print("="*80)
    for i, item in enumerate(categories["partial"][:20], 1):
        french = item["french"][:50] + "..." if len(item["french"]) > 50 else item["french"]
        english = item["english"][:50] + "..." if len(item["english"]) > 50 else item["english"]
        try:
            print(f"{i:3d}. {french}")
            print(f"     -> {english}")
            print()
        except:
            print(f"{i:3d}. [encoding issue]")
        faulty_translations[item["french"]] = item["english"]  # Mark for review

    print(f"\n... and {len(categories['partial']) - 20} more") if len(categories["partial"]) > 20 else None

    print("\n" + "="*80)
    print("CORRUPTED TRANSLATIONS (encoding issues)")
    print("="*80)
    for i, item in enumerate(categories["corrupted"][:15], 1):
        french = item["french"][:50] + "..." if len(item["french"]) > 50 else item["french"]
        english = item["english"][:50] + "..." if len(item["english"]) > 50 else item["english"]
        try:
            print(f"{i:3d}. {french}")
            print(f"     -> {english}")
            print()
        except:
            print(f"{i:3d}. [encoding issue]")
        faulty_translations[item["french"]] = item["english"]  # Mark for review

    print(f"\n... and {len(categories['corrupted']) - 15} more") if len(categories["corrupted"]) > 15 else None

    # Save faulty translations for correction
    output_file = "faulty_translations_to_fix.json"
    print(f"\n{'='*80}")
    print(f"SAVING FAULTY TRANSLATIONS TO: {output_file}")
    print('='*80)
    print(f"Total faulty entries: {len(faulty_translations)}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(faulty_translations, f, ensure_ascii=False, indent=2)

    print(f"\nNext steps:")
    print(f"1. Edit {output_file}")
    print(f"2. Provide proper English translations")
    print(f"3. Run update_dictionary.py to merge corrections")

    # Also save detailed report
    report_file = "faulty_translations_report.json"
    detailed_report = {
        "summary": {cat: len(items) for cat, items in categories.items()},
        "identity_mappings": categories["identity"],
        "partial_translations": categories["partial"],
        "corrupted": categories["corrupted"]
    }

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(detailed_report, f, ensure_ascii=False, indent=2)

    print(f"\nDetailed report saved to: {report_file}")

    return categories

if __name__ == "__main__":
    analyze_dictionary()
