"""
Complete A-081 translations by adding missing items
"""
import json
import hashlib

def hash_text(text):
    """Create hash of text for dictionary lookup"""
    normalized = ' '.join(text.split())
    hash_obj = hashlib.sha256(normalized.encode('utf-8'))
    return hash_obj.hexdigest()

# Manual translations for missing French terms
missing_translations = {
    "PLAFONDS": "CEILINGS",
    "FINIS": "FINISHES",
    "acier": "steel",
    "durcisseur et/ou scelleur": "hardener and/or sealer",
    "aluminium": "aluminum",
    "peinture époxyde": "epoxy paint",
    "carte de localisation": "location map",
    "bloc de béton": "concrete block",
    "prépeint": "pre-painted",
    "bois": "wood",
    "peinture": "paint",
    "béton": "concrete",
    "scelleur": "sealer",
    "caoutchouc": "rubber",
    "carreaux insonorisants": "acoustic tiles",
    "gypse": "gypsum",
    "linoléum": "linoleum",
    "vinyle en carreaux": "vinyl tile",
    "vinyle en feuilles": "vinyl sheet",
    "DA0006-A JETÉE TEMPORAIRE": "DA0006-A TEMPORARY PIER",
    "équipe de projet": "project team",
    "cc1.1": "cc1.1",
    "PRÉLIMINAIRE": "PRELIMINARY",
    "N.B. : Le ou les plans ne sont fournis par YUL (ADM)": "N.B.: Plans are provided by YUL (ADM)",
    "YUL (ADM) ne peut garantir leur exactitude de sorte": "YUL (ADM) cannot guarantee their accuracy such",
    "utiliser avec réserve; il lui incombe d'en vérifier": "use with caution; it is his responsibility to verify",
    "relevés supplémentaires appropriés.": "appropriate additional surveys.",
    "CES DOCUMENTS NE DOIVENT PAS ÊTRE": "THESE DOCUMENTS SHOULD NOT BE",
    "UTILISÉS À DES FINS DE CONSTRUCTION": "USED FOR CONSTRUCTION PURPOSES",
    "sceaux": "seals",
    "DÉVELOPPEMENT PRÉLIMINAIRE": "PRELIMINARY DEVELOPMENT",
    "AVANCEMENT 15%": "15% PROGRESS",
    "date": "date",
    "révisions": "revisions",
    "titre du projet": "project title",
    "JETÉE TEMPORAIRE À YUL AÉROPORT": "TEMPORARY PIER AT YUL AIRPORT",
    "INTERNATIONAL MONTRÉAL-TRUDEAU": "INTERNATIONAL MONTREAL-TRUDEAU",
    "titre du dessin": "drawing title",
    "échelle": "scale",
    "conçu par": "designed by",
    "dessiné par": "drawn by",
    "projet no.": "project no.",
    "DA0006": "DA0006",
    "vérifié par": "verified by",
    "référence": "reference",
    "JLP 4371 | MSDL": "JLP 4371 | MSDL",
    "MF / AS / NR": "MF / AS / NR",
    "25000 | Corgan #25021": "25000 | Corgan #25021",
    "feuille": "sheet",
    "Q142YXXXXAXXXX": "Q142YXXXXAXXXX",
    "A0 élargi - 1422 x 841": "A0 expanded - 1422 x 841",
}

def main():
    print("Completing A-081 translations...")

    # Load existing translations
    with open("A-081_translations.json", 'r', encoding='utf-8') as f:
        translations = json.load(f)

    print(f"Existing translations: {len(translations)}")

    # Add missing translations
    added = 0
    for french, english in missing_translations.items():
        h = hash_text(french)
        if h not in translations:
            translations[h] = english
            added += 1
            print(f"  Added: {french} -> {english}")

    # Save updated translations
    with open("A-081_translations.json", 'w', encoding='utf-8') as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)

    print(f"\nTotal translations: {len(translations)}")
    print(f"Added: {added}")
    print("Saved to: A-081_translations.json")

if __name__ == "__main__":
    main()
