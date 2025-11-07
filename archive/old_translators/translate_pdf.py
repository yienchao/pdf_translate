import fitz  # PyMuPDF
import re
from pathlib import Path

# Comprehensive French-to-English architectural dictionary
TRANSLATION_DICT = {
    # Document headers and general terms
    "LÉGENDES ET NOTES GÉNÉRALES": "LEGENDS AND GENERAL NOTES",
    "LÉGENDES": "LEGENDS",
    "LÉGENDE": "LEGEND",
    "NOTES GÉNÉRALES": "GENERAL NOTES",

    # Reference terms
    "ENCADRÉ DE RÉFÉRENCE AU DÉTAIL": "DETAIL REFERENCE BOX",
    "NUMÉRO DU DÉTAIL": "DETAIL NUMBER",
    "NUMÉRO DE LA FEUILLE DU DÉTAIL": "DETAIL SHEET NUMBER",
    "ZONE DU DÉTAIL AGRANDI": "ENLARGED DETAIL AREA",
    "RÉFÉRENCE DE L'ÉLÉVATION": "ELEVATION REFERENCE",
    "NUMÉRO DE ÉLÉVATION SUR LA FEUILLE": "ELEVATION NUMBER ON SHEET",
    "NUMÉRO DE LA FEUILLE DE L'ÉLÉVATION": "ELEVATION SHEET NUMBER",
    "SENS DE L'ÉLÉVATION": "ELEVATION DIRECTION",
    "SENS DES ÉLÉVATIONS": "ELEVATIONS DIRECTION",
    "RÉFÉRENCES MULTIPLES AUX ÉLÉVATIONS": "MULTIPLE ELEVATION REFERENCES",
    "NUMÉRO DES ÉLÉVATIONS SUR LA FEUILLES": "ELEVATIONS NUMBER ON SHEETS",
    "RENVOI DE CONTINUITÉ AU DESSIN": "DRAWING CONTINUITY REFERENCE",
    "NUMÉRO DE LA FEUILLE DU DESSIN": "DRAWING SHEET NUMBER",

    # Structural terms
    "AXE STRUCTURAL": "STRUCTURAL AXIS",
    "NIVEAU EN COUPE OU ÉLÉVATION": "LEVEL IN SECTION OR ELEVATION",
    "NIVEAU (DESSUS) DE L'ÉLÉMENT": "LEVEL (TOP) OF ELEMENT",
    "COUPE DE RÉFÉRENCE AU DÉTAIL OU À LA COUPE DE MUR TYPE": "DETAIL OR TYPICAL WALL SECTION REFERENCE",
    "NUMÉRO DU DÉTAIL OU DESSIN": "DETAIL OR DRAWING NUMBER",
    "NUMÉRO DE LA FEUILLE DU DÉTAIL OU DESSIN": "DETAIL OR DRAWING SHEET NUMBER",
    "SENS ET ZONE DU DÉTAIL OU DE LA COUPE DE MUR TYPE": "DETAIL OR TYPICAL WALL SECTION DIRECTION AND AREA",
    "NOTE SIM. AU BESOIN": "NOTE SIM. AS NEEDED",
    "COUPE DE RÉFÉRENCE POUR COUPE GÉNÉRALE": "REFERENCE SECTION FOR GENERAL SECTION",
    "LETTRE DE LA COUPE GÉNÉRALE": "GENERAL SECTION LETTER",
    "NUMÉRO DE LA FEUILLE DE LA COUPE GÉNÉRALE": "GENERAL SECTION SHEET NUMBER",
    "SENS ET ZONE DE LA COUPE GÉNÉRALE": "GENERAL SECTION DIRECTION AND AREA",
    "TRAJET DE L'ÉLÉMENT COUPÉ DU PLAN OU DE L'ÉLÉVATION": "PATH OF ELEMENT CUT FROM PLAN OR ELEVATION",

    # General symbols
    "SYMBOLES GÉNÉRAUX": "GENERAL SYMBOLS",
    "IDENTIFICATION DU DESSIN": "DRAWING IDENTIFICATION",
    "NUMÉRO DU DESSIN": "DRAWING NUMBER",
    "NUMÉRO DE LA FEUILLE DU DESSIN": "DRAWING SHEET NUMBER",
    "ÉTIQUETTE DE RÉFÉRENCE DE PLANS AGRANDIS SIMILAIRES SUR LA SÉRIE": "SIMILAR ENLARGED PLANS REFERENCE TAG ON SERIES",
    "VOIR": "SEE",
    "ÉCHELLE": "SCALE",

    # Ceiling, wall, and floor legends
    "LÉGENDE DES PLAFONDS, MURS ET PLANCHERS": "CEILING, WALL AND FLOOR LEGEND",
    "PLAFOND RÉFLÉCHI": "REFLECTED CEILING",
    "FINI DU PLAFOND": "CEILING FINISH",
    "SYSTÈME DU PLAFOND": "CEILING SYSTEM",
    "VOIR COMPOSITIONS TYPES SUR": "SEE TYPICAL ASSEMBLIES ON",
    "ÉLÉVATION DU PLAFOND PAR RAPPORT AU PLANCHER DE L'ÉTAGE": "CEILING ELEVATION RELATIVE TO FLOOR LEVEL",
    "PLANCHER": "FLOOR",
    "FINI DE LA PLINTHE": "BASEBOARD FINISH",
    "FINI DU PLANCHER": "FLOOR FINISH",
    "MUR": "WALL",
    "FINI DU MUR": "WALL FINISH",
    "DÉLIMITATION DE LA COULEUR D'ACCENT MURALE": "WALL ACCENT COLOR BOUNDARY",

    # Ceiling types
    "CARREAUX ACOUSTIQUES LAVABLES": "WASHABLE ACOUSTIC TILES",
    "COULEUR BLANC": "WHITE COLOR",
    "COULEUR NOIR": "BLACK COLOR",
    "COULEUR VERT": "GREEN COLOR",
    "USAGE GÉNÉRAL": "GENERAL USE",
    "MODÈLE": "MODEL",
    "SYSTÈME DE SUSPENSION": "SUSPENSION SYSTEM",
    "CARREAUX ACOUSTIQUES STÉRILES": "STERILE ACOUSTIC TILES",
    "ZONE SANTÉ": "HEALTH ZONE",
    "SYSTÈME DE PLAFOND MÉTALLIQUE À RESSORTS DE TORSION": "TORSION SPRING METAL CEILING SYSTEM",
    "PANNEAUX DE LAMES": "BLADE PANELS",
    "PANNEAUX DE REMPLISSAGE ACOUSTIQUE": "ACOUSTIC INFILL PANELS",
    "PANNEAU RADIANT": "RADIANT PANEL",
    "VOIR DOCUMENTS D'INGÉNIERIE": "SEE ENGINEERING DOCUMENTS",
    "AVEC ZONE TECHNIQUE DE": "WITH TECHNICAL ZONE OF",
    "DE LARGEUR": "WIDTH",
    "PLAFOND EN STRUCTURE APPARENTE": "EXPOSED STRUCTURE CEILING",
    "DALLE DE BÉTON SUR PONTAGE MÉTALLIQUE SUR MURS PORTEURS DE MAÇONNERIE": "CONCRETE SLAB ON METAL DECK ON LOAD-BEARING MASONRY WALLS",
    "SE RÉFÉRER AU DÉTAIL": "REFER TO DETAIL",
    "DALLE DE BÉTON SUR PONTAGE MÉTALLIQUE AVEC REVÊTEMENT IGNIFUGE PROJETÉ SUR COLONNES D'ACIER": "CONCRETE SLAB ON METAL DECK WITH SPRAYED FIREPROOFING ON STEEL COLUMNS",
    "DALLE DE BÉTON SUR PONTAGE MÉTALLIQUE SUR COLONNES D'ACIER": "CONCRETE SLAB ON METAL DECK ON STEEL COLUMNS",
    "PLAFOND AVEC PANNEAUX D'ÉBÉNISTERIE": "CEILING WITH MILLWORK PANELS",
    "SYSTÈME DE PLAFOND INSONORISANT": "SOUND-INSULATING CEILING SYSTEM",
    "PLAFOND ACOUSTIQUE": "ACOUSTIC CEILING",
    "OUVERTURE D'ACCÈS AUX VCF": "VCF ACCESS OPENING",
    "MOULURES EN TÉ FACILEMENT DÉMONTABLES AU DESSUS DE LA PLATEFORME ÉLÉVATRICE À CISEAUX": "EASILY REMOVABLE T-MOLDINGS ABOVE SCISSOR LIFT PLATFORM",

    # Abbreviations
    "ABRÉVIATIONS": "ABBREVIATIONS",
    "ACIER STRUCTURAL AUX FENÊTRES": "STRUCTURAL STEEL AT WINDOWS",
    "VOIR LÉGENDES ÉLÉVATIONS": "SEE ELEVATION LEGENDS",
    "ALIGNER": "ALIGN",
    "ALUMINIUM": "ALUMINUM",
    "APPEL D'OFFRES": "CALL FOR TENDERS",
    "BOLLARD": "BOLLARD",
    "BOYAU D'ARROSAGE": "GARDEN HOSE",
    "BOUTON POUSSOIR": "PUSH BUTTON",
    "BOUTON DE RETENUE": "HOLD BUTTON",
    "VOIR LÉGENDE ÉLÉVATION": "SEE ELEVATION LEGEND",
    "CENTRE LIGNE": "CENTER LINE",
    "CENTRE À CENTRE": "CENTER TO CENTER",
    "CENTRE DU MENEAU": "MULLION CENTER",
    "COLONNE PLUVIALE": "RAINWATER DOWNSPOUT",
    "CAMÉRA DE SÉCURITÉ": "SECURITY CAMERA",
    "VOIR DOCUMENTS D'INGÉNIERIE POUR BASE DE SUPPORT POUR CAMÉRA DÉPOSÉE SUR LA TOITURE": "SEE ENGINEERING DOCUMENTS FOR SUPPORT BASE FOR ROOF-MOUNTED CAMERA",
    "CAMÉRA DE SÉCURITÉ MURALE": "WALL-MOUNTED SECURITY CAMERA",
    "CONTREVENTEMENT STRUCTURAL": "STRUCTURAL BRACING",
    "PANNEAU DE SIGNALISATION MURAL": "WALL-MOUNTED SIGNAGE PANEL",
    "PANNEAU DE SIGNALISATION SUSPENDU": "SUSPENDED SIGNAGE PANEL",
    "DRAIN AU PLANCHER": "FLOOR DRAIN",
    "DEGRÉ DE RÉSISTANCE AU FEU": "FIRE RESISTANCE RATING",
    "DRAIN DE TOIT": "ROOF DRAIN",
    "DRAIN DE TOIT D'URGENCE": "EMERGENCY ROOF DRAIN",
    "DÉFLECTEUR POUR GICLEUR": "SPRINKLER DEFLECTOR",
    "VOIR DÉTAIL": "SEE DETAIL",
    "ÉGAL": "EQUAL",
    "ÉLECTROMÉCANIQUE": "ELECTROMECHANICAL",
    "ÉLECTRICITÉ": "ELECTRICITY",
    "ÉPAIS": "THICK",
    "ÉMIS POUR CONSTRUCTION": "ISSUED FOR CONSTRUCTION",
    "EXTÉRIEUR": "EXTERIOR",
    "FACE FINIE À FACE FINIE": "FINISH FACE TO FINISH FACE",
    "FEUILLE DE CUIVRE": "COPPER SHEET",
    "FACE FINIE À AXE": "FINISH FACE TO AXIS",
    "FOURNI ET INSTALLÉ PAR LE PROPRIÉTAIRE": "SUPPLIED AND INSTALLED BY OWNER",
    "FOURNI PAR LE PROPRIÉTAIRE, INSTALLÉ PAR L'ENTREPRENEUR": "SUPPLIED BY OWNER, INSTALLED BY CONTRACTOR",
    "GARDE-CORPS": "GUARDRAIL",
    "GICLEUR DE FENÊTRE": "WINDOW SPRINKLER",
    "GARDE-CORPS EXTÉRIEUR": "EXTERIOR GUARDRAIL",
    "HORS-CONTRAT": "OUT OF CONTRACT",
    "HAUTEUR DE CLOISON": "PARTITION HEIGHT",
    "HORIZONTAL": "HORIZONTAL",
    "INTÉRIEUR": "INTERIOR",
    "INVERSÉ": "INVERTED",
    "PANNEAU DIRECTIONNEL SUSPENDU": "SUSPENDED DIRECTIONAL PANEL",
    "JOINT ARCHITECTURAL": "ARCHITECTURAL JOINT",
    "JOINT DE CONTRÔLE": "CONTROL JOINT",
    "JOINT DE CONTRÔLE COMPARTIMENTÉ": "COMPARTMENTED CONTROL JOINT",
    "JOINT DE DILATATION": "EXPANSION JOINT",
    "GARNITURE D'ÉTANCHÉITÉ ATYPIQUE DANS LE MUR-RIDEAU": "ATYPICAL SEALING GASKET IN CURTAIN WALL",
    "JOINT DE SILICONE": "SILICONE JOINT",
    "JOINT SISMIQUE": "SEISMIC JOINT",
    "LINTEAU LIBRE": "FREE LINTEL",
    "LINTEAU STRUCTURAL": "STRUCTURAL LINTEL",
    "LUMINAIRE": "LIGHT FIXTURE",
    "MONUMENT DE PLANCHER": "FLOOR MONUMENT",
    "MAIN-COURANTE": "HANDRAIL",
    "MÉCANIQUE": "MECHANICAL",
    "MÉTAUX OUVRÉS": "ORNAMENTAL METALS",
    "MUR-RIDEAU": "CURTAIN WALL",
    "MENEAU TRAITÉ ACOUSTIQUEMENT": "ACOUSTICALLY TREATED MULLION",
    "NOUVEAU": "NEW",
    "OUVERTURE": "OPENING",
    "OUVERTURE BRUTE": "ROUGH OPENING",
    "OUVERTURE LIBRE": "CLEAR OPENING",
    "PASSAGE DU CÂBLE": "CABLE PASSAGE",
    "PLAQUE DE CAMÉRA DE SÉCURITÉ": "SECURITY CAMERA PLATE",
    "PASSE-FILS": "WIRE PASS-THROUGH",
    "POINT BAS": "LOW POINT",
    "POINT HAUT": "HIGH POINT",
    "PANNEAU D'ACCÈS": "ACCESS PANEL",
    "PLAQUE DE PLOMB": "LEAD PLATE",
    "PARE-FUMÉE": "SMOKE BARRIER",
    "REVÊTEMENT ACOUSTIQUE": "ACOUSTIC COATING",
    "ROBINET D'ARROSAGE EXTÉRIEUR": "EXTERIOR HOSE BIB",
    "PANNEAU MURAL DE REPÉRAGE": "WALL-MOUNTED WAYFINDING PANEL",
    "REVÊTEMENT": "CLADDING",
    "SORTIE DE BUANDERIE": "LAUNDRY VENT",
    "PROFIL DE LA SECTION EFFECTIVE DE LA PERSIENNE": "LOUVER EFFECTIVE SECTION PROFILE",
    "SEULEMENT": "ONLY",
    "SORTIE DE HOTTE DE CUISINE": "KITCHEN HOOD EXHAUST",
    "VOIR DOCUMENTS D'INGÉNIERIE": "SEE ENGINEERING DOCUMENTS",
    "SAUF INDICATION CONTRAIRE": "UNLESS OTHERWISE NOTED",
    "SIMILAIRE": "SIMILAR",
    "STATION DE TRANSPORT PNEUMATIQUE": "PNEUMATIC TRANSPORT STATION",
    "STRUCTURE OU STRUCTURAL": "STRUCTURE OR STRUCTURAL",
    "TYPIQUE": "TYPICAL",
    "VERTICAL": "VERTICAL",
    "VIDE TECHNIQUE": "TECHNICAL VOID",
    "LÉGENDE DES JOINTS SISMIQUES": "SEISMIC JOINTS LEGEND",

    # Table headers and misc
    "Plan clé": "Key Plan",
    "Client": "Client",
    "Concepteur-constructeur": "Design-Builder",
    "USAGERS": "USERS",
    "UTILISATEURS": "USERS",
    "STATION.": "STATION.",
    "DATE": "DATE",
    "ÉMISSION": "ISSUE",
    "PEINTURE": "PAINTING",
    "CONSTRUCTION": "CONSTRUCTION",
    "BASSINS ET GRILLES GRATTE-PIEDS": "BASINS AND GRATING SCRAPERS",
    "LOT": "LOT",
    "REVÊTEMENTS MÉTALLIQUES DE FINITION": "FINISH METAL CLADDING",
    "ÉBÉNISTERIE - MENUISERIE": "MILLWORK - JOINERY",
    "ADDENDA": "ADDENDUM",
    "PORTES ET BÂTIS - PORTES COULISSANTES": "DOORS AND FRAMES - SLIDING DOORS",
    "MOBILIERS BLINDÉS": "ARMORED FURNITURE",

    # Common words
    " ET ": " AND ",
    " OU ": " OR ",
    " SUR ": " ON ",
    " DE ": " OF ",
    " DU ": " OF ",
    " LA ": " THE ",
    " LE ": " THE ",
    " LES ": " THE ",
    " AU ": " TO ",
    " AUX ": " TO ",
    " POUR ": " FOR ",
    " AVEC ": " WITH ",
    " DANS ": " IN ",
    " PAR ": " BY ",
}

def translate_text(text):
    """Translate French text to English using the dictionary."""
    translated = text

    # Sort by length (longest first) to avoid partial matches
    sorted_terms = sorted(TRANSLATION_DICT.items(), key=lambda x: len(x[0]), reverse=True)

    for french, english in sorted_terms:
        # Case-insensitive replacement while preserving original case pattern
        pattern = re.compile(re.escape(french), re.IGNORECASE)
        translated = pattern.sub(english, translated)

    return translated

def translate_pdf(input_path, output_path):
    """Translate French PDF to English and save as a new file."""
    print(f"Opening PDF: {input_path}")
    doc = fitz.open(input_path)

    total_pages = len(doc)
    print(f"Total pages: {total_pages}")

    for page_num in range(total_pages):
        print(f"\nProcessing page {page_num + 1}/{total_pages}...")
        page = doc[page_num]

        # Get all text instances with their positions
        text_instances = page.get_text("dict")

        # Extract text blocks
        blocks = text_instances.get("blocks", [])

        replacements = []

        for block in blocks:
            if block.get("type") == 0:  # Text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        original_text = span.get("text", "")
                        if original_text.strip():
                            translated_text = translate_text(original_text)

                            if translated_text != original_text:
                                # Store replacement info
                                replacements.append({
                                    "original": original_text,
                                    "translated": translated_text,
                                    "bbox": span.get("bbox"),
                                    "font": span.get("font"),
                                    "size": span.get("size"),
                                    "color": span.get("color", 0)
                                })

        # Apply replacements
        print(f"Found {len(replacements)} text replacements on page {page_num + 1}")

        for repl in replacements:
            bbox = repl["bbox"]

            # Create a white rectangle to cover the original text
            rect = fitz.Rect(bbox)
            page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

            # Insert translated text
            # Adjust font size if English text is shorter to fit better
            font_size = repl["size"]

            # Try to insert text at the same position
            try:
                # Convert color from integer to RGB tuple
                color_int = repl["color"]
                color = (
                    ((color_int >> 16) & 0xFF) / 255.0,
                    ((color_int >> 8) & 0xFF) / 255.0,
                    (color_int & 0xFF) / 255.0
                )

                page.insert_text(
                    (bbox[0], bbox[3] - 1),  # Bottom-left position
                    repl["translated"],
                    fontsize=font_size,
                    color=color,
                    fontname="helv"  # Use Helvetica as fallback
                )
            except Exception as e:
                print(f"Warning: Could not insert text '{repl['translated']}': {e}")

    # Save the translated PDF
    print(f"\nSaving translated PDF to: {output_path}")
    doc.save(output_path)
    doc.close()
    print("Translation complete!")

if __name__ == "__main__":
    # Input and output paths
    input_pdf = r"C:\Users\yichao\Documents\pdfTranslate\AR-001 - LÉGENDES ET NOTES GÉNÉRALES.pdf"
    output_pdf = r"C:\Users\yichao\Documents\pdfTranslate\AR-001 - LEGENDS AND GENERAL NOTES.pdf"

    translate_pdf(input_pdf, output_pdf)
