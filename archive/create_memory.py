"""Create translation memory from pending translations"""
import json
import sys

# Get pending file from command line or use default
pending_file = sys.argv[1] if len(sys.argv) > 1 else 'A-001_pending_translations.json'

# Load pending
print(f"Loading pending translations from: {pending_file}")
with open(pending_file, 'r', encoding='utf-8') as f:
    pending = json.load(f)

# Load existing dictionary to use as seed
try:
    with open('translations.json', 'r', encoding='utf-8') as f:
        trans_dict = json.load(f)
except:
    trans_dict = {}

# Load existing translation memory if exists
try:
    with open('translation_memory.json', 'r', encoding='utf-8') as f:
        memory = json.load(f)
    print(f"Loaded existing translation memory: {len(memory)} translations")
except:
    memory = {}
    print("Starting fresh translation memory")

# Translate each item
for hash_key, french_text in pending.items():
    # Keep acronyms as-is (standalone)
    if french_text in ['SIC', 'DRF', 'FVX', 'MAO', 'TIC', 'YUL', 'ADM', 'béS', 'béD']:
        memory[hash_key] = french_text
        continue

    # Handle sentences starting with "SIC," (Latin for "thus" - keep as-is)
    if french_text.startswith('SIC,'):
        # Don't use trans_dict - it has wrong translation (U.N.O.)
        # Process manually below
        pass
    # Check if exact match in dictionary
    elif french_text in trans_dict:
        memory[hash_key] = trans_dict[french_text]
        continue

    # Common pattern replacements
    english = french_text

    # Normalize special characters (smart quotes, apostrophes)
    english = english.replace(chr(8217), "'")  # Right single quotation mark → apostrophe
    english = english.replace(chr(8216), "'")  # Left single quotation mark → apostrophe
    english = english.replace(chr(8220), '"')  # Left double quotation mark → straight quote
    english = english.replace(chr(8221), '"')  # Right double quotation mark → straight quote
    english = english.replace(chr(8230), '...')  # Horizontal ellipsis → three dots

    # First, protect SIC (Latin for "thus") - replace with placeholder
    english = english.replace('SIC,', '__SIC__')

    replacements = {
        # Long complex sentences first (match longest first)
        "LES FONDS DE VISSAGE IDENTIFIÉS AUX DESSINS ET AUX LISTES D'ÉQUIPEMENTS ET ACCESSOIRES": "THE BLOCKING IDENTIFIED ON THE DRAWINGS AND EQUIPMENT AND ACCESSORIES LISTS",
        "TYPE D'ASSEMBLAGE D'ENVELOPPE (VOIR SECTION": "ENVELOPE ASSEMBLY TYPE (SEE SECTION",
        "ASSEMBLAGES ENVELOPPE POUR ABRÉVIATIONS)": "ENVELOPE ASSEMBLIES FOR ABBREVIATIONS)",
        "SONT LES FONDS DE VISSAGE REQUIS POUR LES ÉQUIPEMENTS FOURNIS (OU FOURNIS ET": "ARE THE BLOCKING REQUIRED FOR THE EQUIPMENT SUPPLIED (OR SUPPLIED AND",
        "INSTALLÉS) PAR LE PROPRIÉTAIRE. CES FONDS DE VISSAGE SONT IDENTIFIÉS AUX DESSINS AVEC": "INSTALLED) BY THE OWNER. THESE BACKINGS ARE IDENTIFIED ON THE DRAWINGS WITH",
        "L'ABRÉVIATION ''FVX''. L'ENTREPRENEUR DOIT FOURNIR ET INSTALLER CES FONDS DE VISSAGE ET": "THE ABBREVIATION ''FVX''. THE CONTRACTOR MUST PROVIDE AND INSTALL THESE BACKINGS AND",
        "VALIDER LEUR POSITIONNEMENT FINAL AVEC LE PROPRIÉTAIRE AU CHANTIER AVANT LEUR": "VALIDATE THEIR FINAL POSITIONING WITH THE OWNER ON SITE BEFORE THEIR",
        "D'AUTRE PART, IL EST DE LA RESPONSABILITÉ DE L'ENTREPRENEUR DE FOURNIR ET INSTALL": "ON THE OTHER HAND, IT IS THE CONTRACTOR'S RESPONSIBILITY TO PROVIDE AND INSTALL",
        "TOUS LES AUTRES FONDS DE VISSAGE REQUIS POUR TOUS LES ÉQUIPEMENTS, ACCESSOIRES OU": "ALL OTHER BACKING REQUIRED FOR ALL EQUIPMENT, ACCESSORIES OR",
        "TOUS AUTRES ÉLÉMENTS À INTÉGRER À L'OUVRAGE PRÉVUS AUX DOCUMENTS. CES DERNIERS NE": "ALL OTHER ELEMENTS TO BE INTEGRATED INTO THE WORK PROVIDED IN THE DOCUMENTS. THESE LATTER DO NOT",
        "SONT PAS POSITIONNÉS AUX DESSINS ET L'ENTREPRENEUR DOIT COORDONNER AVEC CHACUN DE": "ARE NOT POSITIONED ON THE DRAWINGS AND THE CONTRACTOR MUST COORDINATE WITH EACH OF",
        "SES SOUS-TRAITANTS POUR LEURS DIMENSIONS ET POSITIONS.": "THEIR SUBCONTRACTORS FOR THEIR DIMENSIONS AND POSITIONS.",
        # Shorter phrases and common words
        # Room/Space names
        'VESTIBULE': 'VESTIBULE',
        'CORRIDOR': 'CORRIDOR',
        'RAMPE': 'RAMP',
        'PORTE': 'GATE',
        'SALLE': 'ROOM',
        "SALLE D'EMBARQUEMENT": "BOARDING LOUNGE",
        "SALLE D'ENTREVUE": "INTERVIEW ROOM",
        "SALLE DE REPOS": "REST ROOM",
        "SALLE DE MOBILISATION": "MOBILIZATION ROOM",
        "SALLE DE TOILETTE": "TOILET ROOM",
        "TOILETTES MIXTES": "UNISEX TOILETS",
        "TOILETTE ASSISTÉE": "ACCESSIBLE TOILET",
        "LIEU D'AISANCE CANIN": "DOG RELIEF AREA",
        "SALLE D'ALLAITEMENT": "NURSING ROOM",
        'CORRIDOR DE SERVICE': 'SERVICE CORRIDOR',
        "CORRIDOR D'ACCÈS": "ACCESS CORRIDOR",
        'VOIE SURÉLEVÉE': 'ELEVATED ROADWAY',
        'ZONE DE CHAISE ROULANTE': 'WHEELCHAIR AREA',
        'ZONE FAUTEUILS ROULANTS': 'WHEELCHAIR AREA',
        'GAINE DES ASCENSEURS': 'ELEVATOR SHAFT',
        'STATION DE POMPAGE': 'PUMPING STATION',
        'PRÉACTION': 'PREACTION',
        'ENTREPOSAGE': 'STORAGE',
        'LOCAL ÉLECTRIQUE': 'ELECTRICAL ROOM',
        'LOCAL TÉLÉCOM': 'TELECOM ROOM',
        "LOCAL ENTRÉE D'EAU": "WATER ENTRY ROOM",
        'LOCAL DÉCHETS': 'WASTE ROOM',
        'LOCAL TECHNIQUE': 'TECHNICAL ROOM',
        "LOCAL D'ENTRÉE D'EAU": "WATER ENTRY ROOM",
        'LOCAL VENTILATION': 'VENTILATION ROOM',
        'LOCAL PRÉACTION': 'PREACTION ROOM',
        'PLACARD TECHNIQUE': 'TECHNICAL CLOSET',
        'VIDE TECHNIQUE': 'TECHNICAL VOID',
        'CONCIERGERIE': 'JANITORIAL',
        'COMMERCES': 'RETAIL',
        'MACHINES DISTRIBUTRICES': 'VENDING MACHINES',
        'PROTECTION INCENDIE': 'FIRE PROTECTION',
        'ENTRÉE ÉLECTRIQUE PRINCIPALE': 'MAIN ELECTRICAL ENTRANCE',
        'ESCALIER': 'STAIRWAY',
        'VESTIBULE ARRIÈRE': 'REAR VESTIBULE',
        'BUREAU': 'OFFICE',
        'ENTREPROSAGE COMPAGNIE': 'COMPANY STORAGE',
        # Directions/Locations
        'NIVEAU': 'LEVEL',
        'NIV': 'LVL',
        'DÉPART': 'DEPARTURE',
        'ARRIVÉE': 'ARRIVAL',
        'INTL': 'INTL',
        'DOM': 'DOM',
        'TARMAC': 'TARMAC',
        # Materials and finishes
        'BORDEREAU DES FINIS': 'SCHEDULE OF FINISHES',
        'LÉGENDE': 'LEGEND',
        'PIÈCES': 'ROOMS',
        'PLANCHERS': 'FLOORS',
        'PLINTHES': 'BASEBOARDS',
        'MURS': 'WALLS',
        'PLAFONDS': 'CEILINGS',
        'REMARQUES': 'REMARKS',
        'MATÉRIAUX': 'MATERIALS',
        'FINIS': 'FINISHES',
        'TYPE': 'TYPE',
        'BASE': 'BASE',
        'SURFACE': 'SURFACE',
        # Common phrases
        'TOUS LES CONDUITS': 'ALL CONDUITS',
        'ÉLECTRIQUE ET MÉCANIQUE': 'ELECTRICAL AND MECHANICAL',
        'SONT ENCASTRÉS': 'ARE CONCEALED',
        'LES COTES DES CLOISONS': 'THE PARTITION DIMENSIONS',
        'INTÉRIEURES EN GYPSE': 'INTERIOR GYPSUM',
        'DOIVENT SE LIRE COMME': 'SHOULD BE READ AS',
        'POSITION DES CADRES DE PORTES': 'DOOR FRAME POSITION',
        'INSTALLER': 'INSTALL',
        'LE NUMÉRO IDENTIFIANT CHAQUE PORTE': 'THE NUMBER IDENTIFYING EACH DOOR',
        'CORRESPOND AU NUMÉRO DE PIÈCE À': 'CORRESPONDS TO THE ROOM NUMBER TO',
        'TOUS LES PLAFONDS SUSPENDUS': 'ALL SUSPENDED CEILINGS',
        'SONT DE TYPE': 'ARE TYPE',
        'LES TRAMES DES PLAFONDS': 'THE CEILING GRIDS',
        'EN CARREAUX INSONORISANTS SONT': 'IN ACOUSTIC TILE ARE',
        'LES         ÉCLAIRAGES SONT CENTRÉS DANS LES 2 SENS DANS LE': 'THE LIGHTING FIXTURES ARE CENTERED IN BOTH DIRECTIONS IN THE',
        'LES ÉCLAIRAGES SONT CENTRÉS DANS LES 2 SENS DANS LE': 'THE LIGHTING FIXTURES ARE CENTERED IN BOTH DIRECTIONS IN THE',
        'LA HAUTEUR DES PLAFONDS EST DE': 'THE CEILING HEIGHT IS',
        'LA POSITION DES GRILLES DE VENTILATION': 'THE POSITION OF VENTILATION GRILLES',
        'DES TRAPPES D\'ALLÉE ET DE': 'ACCESS PANELS AND',
        'NOTES GÉNÉRALES': 'GENERAL NOTES',
        'LÉGENDES ET SYMBOLES': 'LEGENDS AND SYMBOLS',
        'IMPLANTATION ET AMÉNAGEMENT PAYSAGER': 'SITE PLAN AND LANDSCAPING',
        'ÉLÉVATIONS INTÉRIEURES ET MOBILIERS': 'INTERIOR ELEVATIONS AND FURNITURE',
        'ASSEMBLAGES OU MATÉRIAUX ENVELOPPE': 'ENVELOPE ASSEMBLIES OR MATERIALS',
        'VOIR DOCUMENTS D\'INGÉNIERIE': 'SEE ENGINEERING DOCUMENTS',
        'VOIR FEUILLE': 'SEE SHEET',
        'VOIR FEUILLES': 'SEE SHEETS',
        'DE TYPE': 'TYPE',
        'NON EXHAUSTIF': 'NOT EXHAUSTIVE',
        'SÉRIE': 'SERIES',
        'À COMPLÉTER': 'TO BE COMPLETED',
        'EN BAS': 'BELOW',
        'EN HAUT': 'ABOVE',
        'EXTÉRIEUR': 'EXTERIOR',
        'INTÉRIEUR': 'INTERIOR',
        'NOTES GÉNÉRALES / PLANS': 'GENERAL NOTES / PLANS',
        'NOTES GÉNÉRALES / PLAFONDS': 'GENERAL NOTES / CEILINGS',
        'NOTES GÉNÉRALES / TOITURES': 'GENERAL NOTES / ROOFS',
        'NOTES GÉNÉRALES / ÉLÉVATIONS': 'GENERAL NOTES / ELEVATIONS',
        'carte de localisation': 'location map',
        'équipe de projet': 'project team',
        'titre du projet': 'project title',
        'titre du dessin': 'drawing title',
        'conçu par': 'designed by',
        'dessiné par': 'drawn by',
        'vérifié par': 'checked by',
        'référence': 'reference',
        'échelle': 'scale',
        'révisions': 'revisions',
        'à conserver': 'to remain',
        'à enlever / démolir': 'to remove / demolish',
        'à remettre à neuf': 'to refurbish',
        'panneau de béton': 'concrete panel',
        'plâtre': 'plaster',
        'béton': 'concrete',
        # Note: SIC is Latin for "thus" - keep as-is, don't translate
    }

    for fr, en in replacements.items():
        if fr in english:
            english = english.replace(fr, en)

    # Restore SIC placeholder
    english = english.replace('__SIC__', 'SIC,')

    memory[hash_key] = english

# Save translation memory
with open('translation_memory.json', 'w', encoding='utf-8') as f:
    json.dump(memory, f, ensure_ascii=False, indent=2)

print(f"Created translation_memory.json with {len(memory)} translations")
print(f"Added {len(pending)} new translations from {pending_file}")
print("\nFirst 5 NEW translations:")
for i, (k, v) in enumerate(list(pending.items())[:5]):
    french = pending[k]
    english = memory.get(k, 'NOT TRANSLATED')
    print(f"  {french[:60]} -> {english[:60]}")
