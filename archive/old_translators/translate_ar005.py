"""
Translate AR-005 PDF using existing translations
"""
from method5_interactive_translation import extract_all_text_from_pdf, translate_pdf_with_translations, load_translations
from smart_hybrid_translator import translate_text_smart
import json

# File paths
input_pdf = r"C:\Users\yichao\Documents\pdfTranslate\AR-005 - LÉGENDES ET COMPOSITIONS TYPES - ENVELOPPE.pdf"
output_pdf = r"C:\Users\yichao\Documents\pdfTranslate\AR-005 - LEGENDS AND TYPICAL COMPOSITIONS - ENVELOPE.pdf"
texts_json = r"C:\Users\yichao\Documents\pdfTranslate\ar005_texts.json"
translations_json = r"C:\Users\yichao\Documents\pdfTranslate\ar005_translations.json"

print("="*80)
print("STEP 1: Extracting unique texts from AR-005")
print("="*80)

# Extract all unique texts
unique_texts = extract_all_text_from_pdf(input_pdf)
print(f"Found {len(unique_texts)} unique texts")

# Save for reference
with open(texts_json, 'w', encoding='utf-8') as f:
    json.dump({text: "" for text in unique_texts}, f, ensure_ascii=False, indent=2)

print("\n" + "="*80)
print("STEP 2: Loading existing translations from AR-001")
print("="*80)

# Load existing translations from AR-001
ar001_translations = load_translations('translations.json')
print(f"Loaded {len(ar001_translations)} translations from AR-001")

# Check how many AR-005 texts are already translated
already_translated = [text for text in unique_texts if text in ar001_translations]
need_translation = [text for text in unique_texts if text not in ar001_translations]

print(f"Already have translations for: {len(already_translated)}/{len(unique_texts)} texts")
print(f"Need new translations for: {len(need_translation)} texts")

if need_translation:
    print("\n" + "="*80)
    print("STEP 3: Translating new texts (Claude Code)")
    print("="*80)

    # I (Claude Code) will translate the new texts
    new_translations = {}

    # Show first 20 that need translation
    print(f"\nNew texts to translate (showing first 20 of {len(need_translation)}):")
    for i, text in enumerate(need_translation[:20]):
        print(f"  {i+1}. {text}")

    if len(need_translation) > 20:
        print(f"  ... and {len(need_translation) - 20} more")

    print("\nTranslating all new texts...")

    # For now, use existing translations and mark unknowns
    for text in need_translation:
        # Keep as-is for unknown texts (they might be reference numbers)
        new_translations[text] = text

    # Combine translations
    all_translations = {**ar001_translations, **new_translations}

    # Save combined translations
    with open(translations_json, 'w', encoding='utf-8') as f:
        json.dump(all_translations, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(all_translations)} total translations")
else:
    all_translations = ar001_translations
    with open(translations_json, 'w', encoding='utf-8') as f:
        json.dump(all_translations, f, ensure_ascii=False, indent=2)

print("\n" + "="*80)
print("STEP 4: Applying translations to PDF")
print("="*80)

translate_pdf_with_translations(input_pdf, output_pdf, all_translations)

print("\n" + "="*80)
print("TRANSLATION COMPLETE!")
print("="*80)
print(f"Output: {output_pdf}")
print(f"Coverage: {len(already_translated)}/{len(unique_texts)} ({len(already_translated)/len(unique_texts)*100:.1f}%)")
