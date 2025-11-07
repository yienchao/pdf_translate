"""
After batch translation, process all untranslated French words
This collects from untranslated_french_words.json and prepares for translation
"""
import json

try:
    # Load untranslated words from last run
    with open('untranslated_french_words.json', 'r', encoding='utf-8') as f:
        untranslated = json.load(f)

    print(f"Found {len(untranslated)} untranslated texts")

    if len(untranslated) == 0:
        print("No untranslated words! Dictionary is complete for this PDF.")
        exit(0)

    # Extract unique words (not full sentences)
    import re
    unique_words = set()

    for text in untranslated.keys():
        # Extract words
        words = re.findall(r'\b[a-zA-ZÀ-ÿ]{2,}\b', text)
        for word in words:
            # Skip English words
            if word.isupper() and not any(c in word for c in 'ÀÂÆÇÉÈÊËÏÎÔÙÛÜàâæçéèêëïîôùûüÿœ'):
                continue
            unique_words.add(word)

    # Also include full phrases if short (< 8 words)
    for text in untranslated.keys():
        word_count = len(text.split())
        if word_count <= 8:
            unique_words.add(text)

    print(f"Extracted {len(unique_words)} unique terms/phrases")

    # Create template for translation
    to_translate = {word: "" for word in sorted(unique_words)}

    # Save
    with open('batch_words_to_translate.json', 'w', encoding='utf-8') as f:
        json.dump(to_translate, f, ensure_ascii=False, indent=2)

    print(f"Saved to: batch_words_to_translate.json")
    print(f"\nNext steps:")
    print(f"1. Use Task agent or Claude to translate batch_words_to_translate.json")
    print(f"2. Run: python merge_batch_words.py")
    print(f"3. Re-run the PDFs that had untranslated words")

except FileNotFoundError:
    print("No untranslated_french_words.json found")
    print("This means either:")
    print("  1. No PDFs were translated yet")
    print("  2. All PDFs translated perfectly with current dictionary!")
