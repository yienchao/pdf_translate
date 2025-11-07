"""Quick translation of pending items - creates translation_memory.json"""
import json

# Quick manual translations (architectural terms French->English)
translations = {
    "NOTES GÉNÉRALES ": "GENERAL NOTES",
    "LÉGENDES ET SYMBOLES": "LEGENDS AND SYMBOLS",
    "IMPLANTATION ET AMÉNAGEMENT PAYSAGER ": "SITE PLAN AND LANDSCAPE",
    "ÉLÉVATIONS INTÉRIEURES ET MOBILIERS": "INTERIOR ELEVATIONS AND FURNITURE",
    "ASSEMBLAGES OU MATÉRIAUX ENVELOPPE": "ASSEMBLIES OR ENVELOPE MATERIALS",
    "carte de localisation": "location map",
    "ENTRÉE BÂTIMENT": "BUILDING ENTRANCE",
    "panneau de béton": "concrete panel",
    "parquet en lames de bois": "wood strip flooring",
    "plancher flottant stratifié": "laminate floating floor",
    "plâtre": "plaster",
    "bloc de béton": "concrete block",
    "platelage métallique": "metal decking",
    "béton": "concrete",
    "panneau résine thermodurcissable": "thermosetting resin panel",
    "plastique stratifié": "plastic laminate",
    "bloc de béton vernissé": "glazed concrete block",
    "pavé de béton": "concrete paver",
    "revêtement mural": "wall covering",
    "revêtement en tissu enduit de vinyle": "vinyl coated fabric covering",
    "carreaux de céramique": "ceramic tile",
    "caoutchouc en feuilles": "sheet rubber",
    "carreaux de granit": "granite tile",
    "plafonds en carreaux métalliques ": "metal tile ceilings",
    "carreaux de tapis": "carpet tile",
    "contreplaqué": "plywood",
    "crépi de ciment": "cement stucco",
    "carreaux de terrazzo": "terrazzo tile",
    "terrazzo à liant plastique": "plastic binder terrazzo",
    "carreaux de verre": "glass tile",
    "équipe de projet": "project team",
    "titre du projet": "project title",
    "titre du dessin": "drawing title",
    "conçu par": "designed by",
    "dessiné par": "drawn by",
    "vérifié par": "verified by",
    "référence": "reference",
    "échelle": "scale",
    "révisions": "revisions",
    "béS": "sC",
    "béD": "hC",
    "à conserver": "to remain",
    "à conserver et à relocaliser": "to remain and relocate",
    "à remettre à neuf": "to refurbish",
    "à enlever / démolir": "to remove / demolish",
    "anodisé": "anodized",
    "peinture époxyde": "epoxy paint",
    "émail cuit": "baked enamel",
    "peinture texturée": "textured paint",
    "enduit de chaux": "lime plaster",
    "jet de sable": "sandblast",
    "prépeint": "prepainted",
    "oxydé": "oxidized",
    "scelleur coloré": "colored sealer",
    "teinture et vernis": "stain and varnish",
    "étamé": "tinned",
    "GALVANISÉ": "GALVANIZED"
}

# Load pending file
with open('A-001_pending_translations.json', 'r', encoding='utf-8') as f:
    pending = json.load(f)

# Create memory with same hashes, translated values
memory = {}
for hash_key, french_text in pending.items():
    # Check if we have a direct translation
    if french_text in translations:
        memory[hash_key] = translations[french_text]
    else:
        # For longer sentences/phrases, do basic word replacement
        english = french_text
        # Common replacements
        replacements = {
            "VOIR DOCUMENTS D'INGÉNIERIE": "SEE ENGINEERING DOCUMENTS",
            "VOIR DOCUMENTS": "SEE DOCUMENTS",
            "DE TYPE": "TYPE",
            "NON EXHAUSTIF": "NOT EXHAUSTIVE",
            "VOIR FEUILLE": "SEE SHEET",
            "VOIR FEUILLES": "SEE SHEETS",
            "SÉRIE": "SERIES",
            "DÉTAILS TYPIQUES": "TYPICAL DETAILS",
            "À COMPLÉTER": "TO BE COMPLETED",
            "EN BAS": "BELOW",
            "EN HAUT": "ABOVE",
            "EXTÉRIEUR": "EXTERIOR",
            "INTÉRIEUR": "INTERIOR"
        }
        for fr, en in replacements.items():
            english = english.replace(fr, en)
        memory[hash_key] = english

# Save
with open('translation_memory.json', 'w', encoding='utf-8') as f:
    json.dump(memory, f, ensure_ascii=False, indent=2)

print(f"Created translation_memory.json with {len(memory)} translations")
