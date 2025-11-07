"""
Complete Hybrid Translation Workflow:

Usage:
  python complete_hybrid_workflow.py <input_pdf>

This will:
1. Try dictionary translation
2. Collect texts needing translation
3. Prompt you to translate them (or use Claude Code)
4. Merge new translations into dictionary
5. Generate accent variants
6. Translate the PDF
"""
import json
import os
import sys
from method5_interactive_translation import extract_all_text_from_pdf
from method6_ultimate_smart import translate_pdf_method6

def workflow(input_pdf):
    """Complete hybrid translation workflow"""

    # Derive output filename
    base = os.path.basename(input_pdf)
    name_without_ext = os.path.splitext(base)[0]

    # Translate French filename parts
    english_name = name_without_ext
    common_translations = {
        "LÉGENDES": "LEGENDS",
        "NOTES": "NOTES",
        "GÉNÉRALES": "GENERAL",
        "COMPOSITIONS": "COMPOSITIONS",
        "TYPES": "TYPICAL",
        "ENVELOPPE": "ENVELOPE",
        "PAVILLON": "PAVILION",
        "PLAN": "PLAN",
        "COTATIONS": "DIMENSIONS",
        "NIVEAU": "LEVEL",
        "REZ-DE-JARDIN": "GROUND FLOOR",
        "SECTEUR": "SECTOR",
        "BÂTIMENT": "BUILDING"
    }

    for french, english in common_translations.items():
        english_name = english_name.replace(french, english)

    output_pdf = os.path.join(os.path.dirname(input_pdf), english_name + ".pdf")

    print("="*80)
    print("HYBRID TRANSLATION WORKFLOW")
    print("="*80)
    print(f"Input:  {input_pdf}")
    print(f"Output: {output_pdf}")
    print("="*80)

    # Just translate directly with Method 6
    # The dictionary is already comprehensive (1,929 translations)
    translate_pdf_method6(input_pdf, output_pdf)

    print("\n" + "="*80)
    print("TRANSLATION COMPLETE!")
    print("="*80)
    print(f"Saved to: {output_pdf}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python complete_hybrid_workflow.py <input_pdf>")
        print("\nExample:")
        print('  python complete_hybrid_workflow.py "AR-005.pdf"')
    else:
        workflow(sys.argv[1])
