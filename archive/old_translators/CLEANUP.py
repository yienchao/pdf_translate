"""
Delete unnecessary files - keep only essential files for the translation system
"""
import os
import glob

# Files to DELETE (test files, temporary files, old methods)
files_to_delete = [
    # Test and debug files
    "test_*.py",
    "test_*.pdf",
    "debug_*.py",
    "extract_*.py",
    "analyze_*.py",

    # Old method files (keep only method9_optimized.py)
    "method1*.py",
    "method2*.py",
    "method3*.py",
    "method4*.py",
    "method5*.py",
    "method6*.py",
    "method7*.py",
    "method8*.py",
    "method10*.py",

    # Temporary translation files
    "a001_translations.json",
    "final_6_words.json",
    "words_needing_translation.json",
    "batch_words_to_translate.json",
    "translation_test_results.json",
    "remaining_french_in_output.json",
    "untranslated_french_words.json",
    "failed_insertions.json",
    "removed_single_chars.json",
    "multi_word_phrases.json",
    "final_419_translations.json",
    "a081_new_translations.json",

    # One-time setup scripts
    "add_missing_materials.py",
    "add_last_sentence.py",
    "extract_and_add_sentence.py",
    "fix_dictionary_single_chars.py",
    "add_all_accent_variants.py",
    "add_all_corrupt_variants_v2.py",
    "clean_dictionary_single_words.py",
    "merge_59_words.py",
    "merge_a001_words.py",
    "merge_final_6.py",
    "merge_batch_words.py",
    "fix_final_phrases.py",

    # Temporary output
    "exact_sentence.txt",
    "output.txt"
]

print("Deleting unnecessary files...\n")

deleted_count = 0
for pattern in files_to_delete:
    matching_files = glob.glob(pattern)
    for file in matching_files:
        try:
            os.remove(file)
            print(f"Deleted: {file}")
            deleted_count += 1
        except Exception as e:
            print(f"Could not delete {file}: {e}")

print(f"\nDeleted {deleted_count} files")
print("\n" + "="*80)
print("ESSENTIAL FILES REMAINING:")
print("="*80)
print("\nCore translation system:")
print("  - method9_optimized.py (main translation engine)")
print("  - translations.json (3,070-word dictionary)")
print("  - translate_batch_pdfs.py (for batch processing)")
print("  - translate_all_three.py (for A-001, A-081, A-530)")
print("  - translate_a081_a530.py")
print("\nUtility scripts:")
print("  - process_untranslated_batch.py (extract untranslated words)")
print("  - merge_batch_words.py (merge new translations)")
print("\nTranslated PDFs:")
print("  - A-001 - NOTES AND LEGENDS.pdf")
print("  - A-081 - SCHEDULE OF FINISHES.pdf")
print("  - A-530 - ENVELOPE DETAILS (SECTION).pdf")
