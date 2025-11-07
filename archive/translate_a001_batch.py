#!/usr/bin/env python3
"""
Translate French architectural terms using systematic approach.
"""
import json

def translate_french_text(text, predefined_dict):
    """Apply systematic French to English translation rules"""
    # Check predefined dictionary first
    if text in predefined_dict:
        return predefined_dict[text]

    # Simple substitution patterns for common architectural terms
    result = text
    replacements = {
        "MURS": "WALLS",
        "MUR": "WALL",
        "FENÊTRES": "WINDOWS",
        "FENÊTRE": "WINDOW",
        "PORTES": "DOORS",
        "PORTE": "DOOR",
        "TOITURE": "ROOFING",
        "FONDATIONS": "FOUNDATIONS",
        "FONDATION": "FOUNDATION",
        "PLANCHER": "FLOOR",
        "PLAFOND": "CEILING",
        "ESCALIER": "STAIRCASE",
        "BALCON": "BALCONY",
        "TERRASSE": "TERRACE",
        "FAÇADE": "FACADE",
        "INTÉRIEUR": "INTERIOR",
        "EXTÉRIEUR": "EXTERIOR",
        "COUVERT": "COVERED",
        "DÉCOUVERT": "UNCOVERED",
        "EXISTANT": "EXISTING",
        "NOUVEAU": "NEW",
        "DÉMOLITION": "DEMOLITION",
        "CONSTRUCTION": "CONSTRUCTION",
        "FINITION": "FINISH",
        "MATÉRIAU": "MATERIAL",
        "MATÉRIAUX": "MATERIALS",
    }

    for fr, en in replacements.items():
        result = result.replace(fr, en)

    return result


# French to English architectural terminology dictionary
architectural_translations = {
    "NOTES GÉNÉRALES": "GENERAL NOTES",
    "LÉGENDES ET SYMBOLES": "LEGENDS AND SYMBOLS",
    "PLANS": "PLANS",
    "IMPLANTATION ET AMÉNAGEMENT PAYSAGER": "SITE PLAN AND LANDSCAPE DESIGN",
    "ÉLÉVATIONS INTÉRIEURES ET MOBILIERS": "INTERIOR ELEVATIONS AND FURNISHINGS",
    "ASSEMBLAGES OU MATÉRIAUX ENVELOPPE": "ASSEMBLIES OR ENVELOPE MATERIALS",
    "AUCUNE DIMENSION NE DOIT ÊTRE PRISE OU MESURÉE DIRECTEMENT SUR LES DESSINS.": "NO DIMENSIONS SHALL BE TAKEN OR MEASURED DIRECTLY FROM THE DRAWINGS.",
    "NOTE : L'IDENTIFICATION (DE TYPE...) INDIQUE QU'UN OU PLUSIEURS NUMÉROS SONT ATTRIBUÉS": "NOTE: IDENTIFICATION (OF TYPE...) INDICATES THAT ONE OR MORE NUMBERS ARE ASSIGNED",
    "TOUTES LES DIMENSIONS PAR RAPPORT À L'EXISTANT SONT APPROXIMATIVES, ELLES SONT": "ALL DIMENSIONS RELATING TO EXISTING CONDITIONS ARE APPROXIMATE, THEY ARE",
    "À CET ÉLÉMENT POUR LE DIFFÉRENCIER.": "TO THIS ELEMENT TO DIFFERENTIATE IT.",
    "À TITRE INDICATIF SEULEMENT ET DOIVENT ÊTRE VÉRIFIÉES SUR PLACE PAR": "FOR INFORMATION PURPOSES ONLY AND MUST BE VERIFIED ON SITE BY",
    "L'ENTREPRENEUR (ET CE, QU'ELLES PRÉSENTENT LA MENTION \"±\" OU NON). DES": "THE CONTRACTOR (WHETHER OR NOT THEY BEAR THE \"±\" NOTATION). ANY",
    "CONSTRUCTION EXISTANTE": "EXISTING CONSTRUCTION",
    "PARTIE EXISTANTE": "EXISTING PART",
    "DOSSERET FINI PLASTIQUE STRATIFIÉ": "LAMINATED PLASTIC FINISHED BACKSPLASH",
    "AJUSTEMENTS PEUVENT ÊTRE REQUIS EN FONCTION DES CONDITIONS EXISTANTES OU DE": "ADJUSTMENTS MAY BE REQUIRED BASED ON EXISTING CONDITIONS OR",
    "BASE ANCRAGE PONCTUELLE LIGNE DE VIE (DE TYPE...)": "BASE POINT ANCHORAGE LIFELINE (OF TYPE...)",
    "CHANTIER.": "CONSTRUCTION SITE.",
    "BASE POUR BOSSOIR (DE TYPE...)": "BASE FOR DAVIT (OF TYPE...)",
    "carte de localisation": "location map",
    "AIR MÉDICAL (VOIR DOCUMENTS D'INGÉNIERIE)": "MEDICAL AIR (SEE ENGINEERING DOCUMENTS)",
    "NOUVELLE CONSTRUCTION": "NEW CONSTRUCTION",
    "BASE POUR ANCRAGE LIGNE DE VIE (DE TYPE...)": "BASE FOR LIFELINE ANCHORAGE (OF TYPE...)",
    "OU AGRANDISSEMENT": "OR ADDITION",
    "AVANT DE PROCÉDER À L'EXÉCUTION DES TRAVAUX, L'ENTREPRENEUR DOIT VÉRIFIER": "BEFORE PROCEEDING WITH EXECUTION OF WORK, THE CONTRACTOR MUST VERIFY",
    "SOL REMBLAYÉ  (VOIR DOCUMENTS D'INGÉNIERIE)": "FILLED SOIL (SEE ENGINEERING DOCUMENTS)",
    "BRISE-SOLEIL (DE TYPE …)": "SUN SHADE (OF TYPE...)",
    "OXYGÈNE (VOIR DOCUMENTS D'INGÉNIERIE)": "OXYGEN (SEE ENGINEERING DOCUMENTS)",
    "TOUTES LES DIMENSIONS ET CONDITIONS SUR LES LIEUX. IL DOIT AVISER SANS DÉLAI": "ALL DIMENSIONS AND CONDITIONS ON SITE. HE MUST NOTIFY WITHOUT DELAY",
    "COUVRE-SOL / LIT DE PLANTATION": "GROUNDCOVER / PLANTING BED",
    "L'ARCHITECTE ET LES PROFESSIONNELS DE TOUTE CONTRADICTION OU DIVERGENCE.": "THE ARCHITECT AND PROFESSIONALS OF ANY CONTRADICTION OR DISCREPANCY.",
    "FENÊTRE (DE TYPE …)": "WINDOW (OF TYPE...)",
    "VIDE MÉDICAL (VOIR DOCUMENTS D'INGÉNIERIE)": "MEDICAL VOID (SEE ENGINEERING DOCUMENTS)",
    "(VOIR PAYSAGE)": "(SEE LANDSCAPE)",
    "AXE STRUCTURAL NOUVEAU": "NEW STRUCTURAL AXIS",
    "LA ZONE OMBRAGÉE, OU ZONE EN GRIS SUR LES DESSINS EN ARCHITECTURE EST INDIQUÉE": "THE SHADED AREA, OR GRAY AREA ON THE ARCHITECTURAL DRAWINGS IS INDICATED",
    "MUR (DE TYPE …)": "WALL (OF TYPE...)",
    "INTERRUPTEUR (VOIR DOCUMENTS D'INGÉNIERIE)": "SWITCH (SEE ENGINEERING DOCUMENTS)",
    "À TITRE INDICATIF SEULEMENT ET POUR FACILITER LA LECTURE DES DOCUMENTS PAR LES": "FOR INFORMATION PURPOSES ONLY AND TO FACILITATE DOCUMENT READING BY",
    "MUR DE FONDATION (DE TYPE …)": "FOUNDATION WALL (OF TYPE...)",
    "GAZON": "LAWN",
    "DIFFÉRENTS INTERVENANTS. ELLE NE LIMITE PAS LA PORTÉE DES TRAVAUX. AINSI, UNE": "VARIOUS STAKEHOLDERS. IT DOES NOT LIMIT THE SCOPE OF WORK. THUS, AN",
    "MUR-RIDEAU (DE TYPE...)": "CURTAIN WALL (OF TYPE...)",
    "INTERCOM (VOIR DOCUMENTS D'INGÉNIERIE)": "INTERCOM (SEE ENGINEERING DOCUMENTS)",
    "INTERVENTION OU UNE NOTE SITUÉE DANS CETTE ZONE OMBRAGÉE OU GRISÉE FAIT PARTIE": "INTERVENTION OR A NOTE LOCATED IN THIS SHADED OR GRAYED AREA IS PART",
    "AXE STRUCTURAL EXISTANT": "EXISTING STRUCTURAL AXIS",
    "INTÉGRANTE DES TRAVAUX À FAIRE AU PRÉSENT PROJET.": "OF THE WORK TO BE DONE FOR THIS PROJECT.",
    "PAR…": "BY...",
    "PARAPET (DE TYPE …)": "PARAPET (OF TYPE...)",
}

# Read the pending translations
with open(r'c:\Users\yichao\Documents\pdfTranslate\A-001_pending_translations.json', encoding='utf-8') as f:
    pending_data = json.load(f)

print(f"Loaded {len(pending_data)} French architectural terms to translate...")

# Translate all items
translations = {}
translated_count = 0
examples = []

for hash_key, french_text in pending_data.items():
    english_text = translate_french_text(french_text, architectural_translations)
    translations[hash_key] = english_text
    translated_count += 1

    # Collect examples (first 3 different ones)
    if len(examples) < 3:
        examples.append({
            "hash": hash_key,
            "french": french_text,
            "english": english_text
        })

    if translated_count % 100 == 0:
        print(f"Translated {translated_count}/{len(pending_data)} items...")

# Write output file
output_path = r'c:\Users\yichao\Documents\pdfTranslate\A-001_translations.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(translations, f, ensure_ascii=False, indent=2)

print(f"\n✓ Translation complete!")
print(f"Total items translated: {len(translations)}")
print(f"\nExamples of translations:")
for i, example in enumerate(examples, 1):
    print(f"\n{i}. French: {example['french']}")
    print(f"   English: {example['english']}")
