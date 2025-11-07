"""
Method 10 Helper: Merge agent translations into translation_memory.json
"""
import json
import sys
import os

def merge_translations(pending_file):
    """Merge translated pending items into translation memory"""

    # Load the translated file (created by agent)
    translated_file = pending_file.replace('_pending_translations.json', '_translated.json')

    if not os.path.exists(translated_file):
        print(f"ERROR: {translated_file} not found!")
        print(f"Please run Task agent to create this file first.")
        sys.exit(1)

    with open(translated_file, 'r', encoding='utf-8') as f:
        translated = json.load(f)

    print(f"Loaded {len(translated)} translations from {translated_file}")

    # Load existing translation memory
    memory_file = 'translation_memory.json'
    if os.path.exists(memory_file):
        with open(memory_file, 'r', encoding='utf-8') as f:
            memory = json.load(f)
        print(f"Loaded existing memory: {len(memory)} entries")
    else:
        memory = {}
        print("Starting fresh translation memory")

    # Merge new translations
    added = 0
    for hash_key, english_text in translated.items():
        if hash_key not in memory:
            memory[hash_key] = english_text
            added += 1
        else:
            # Update if different
            if memory[hash_key] != english_text:
                print(f"Updating: {memory[hash_key][:50]} -> {english_text[:50]}")
                memory[hash_key] = english_text

    # Save updated memory
    with open(memory_file, 'w', encoding='utf-8') as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*80}")
    print(f"SUCCESS!")
    print(f"{'='*80}")
    print(f"Added {added} new translations")
    print(f"Total in memory: {len(memory)} entries")
    print(f"Saved to: {memory_file}")
    print(f"\nNow re-run method_hash_based.py to build the translated PDF!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python merge_translations.py <pending_file>")
        print("\nExample:")
        print('  python merge_translations.py A-001_pending_translations.json')
        sys.exit(1)

    merge_translations(sys.argv[1])
