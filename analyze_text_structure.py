"""Analyze A-001 text structure to understand fragmentation"""
import sys
sys.path.insert(0, '.')

from translate_clean import extract_text_from_pdf

pdf_path = "original/A-001 - NOTES ET LÉGENDES.pdf"
text_elements = extract_text_from_pdf(pdf_path)

print(f"Total elements: {len(text_elements)}\n")

# Group by text length
single_word = []
short_phrase = []
long_text = []

for elem in text_elements:
    text = elem["text"]
    word_count = len(text.split())

    if word_count == 1:
        single_word.append(text)
    elif word_count <= 5:
        short_phrase.append(text)
    else:
        long_text.append(text)

print(f"Single words: {len(single_word)}")
print(f"Short phrases (2-5 words): {len(short_phrase)}")
print(f"Long text (6+ words): {len(long_text)}")

print("\n=== Sample LONG text (multi-line paragraphs): ===")
for i, text in enumerate(long_text[:10]):
    print(f"\n{i+1}. ({len(text.split())} words)")
    print(f"   {text[:200]}...")

print("\n=== Sample SINGLE words (fragmented): ===")
for i, text in enumerate(single_word[:30]):
    print(f"{text}", end=", ")
