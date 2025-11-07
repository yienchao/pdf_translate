"""
Analyze translated PDFs to identify remaining French text.
"""

import fitz  # PyMuPDF
import re
from collections import Counter
import os

# Common French words to check
FRENCH_WORDS = ['VOIR', 'POUR', 'DANS', 'AVEC', 'DE', 'DES', 'LES', 'ET', 'SONT',
                'PORTE', 'PORTES', 'CADRE', 'CADRES', 'DÉTAILS', 'PLAN', 'NOTES']

# English equivalents
ENGLISH_WORDS = ['SEE', 'FOR', 'IN', 'WITH', 'OF', 'THE', 'AND', 'ARE',
                 'DOOR', 'DOORS', 'FRAME', 'FRAMES', 'DETAILS', 'PLAN', 'NOTES']

# Common French phrases/patterns
FRENCH_PATTERNS = [
    r'\bVOIR\s+\w+',
    r'\bPOUR\s+\w+',
    r'\bDANS\s+\w+',
    r'\bAVEC\s+\w+',
    r'\bDE\s+LA\b',
    r'\bDU\s+\w+',
    r'\bAU\s+\w+',
    r'\bSUR\s+LE\b',
    r'\bSUR\s+LA\b',
    r'\bÀ\s+LA\b',
    r'\bÀ\s+L\'',
    r'\bD\'UN\b',
    r'\bD\'UNE\b',
]

def extract_text_from_pdf(pdf_path):
    """Extract all text from a PDF file."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def count_word_occurrences(text, words):
    """Count occurrences of words (case-insensitive)."""
    text_upper = text.upper()
    counts = {}
    for word in words:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(word.upper()) + r'\b'
        counts[word] = len(re.findall(pattern, text_upper))
    return counts

def find_french_phrases(text, max_examples=15):
    """Find examples of French phrases in the text."""
    examples = []

    # Split into lines for context
    lines = text.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check for French patterns
        for pattern in FRENCH_PATTERNS:
            matches = re.findall(pattern, line, re.IGNORECASE)
            if matches:
                # Get surrounding context (up to 80 chars)
                if len(line) > 80:
                    # Find the match position and show context
                    for match in matches:
                        pos = line.upper().find(match.upper())
                        if pos != -1:
                            start = max(0, pos - 20)
                            end = min(len(line), pos + 60)
                            context = line[start:end]
                            if start > 0:
                                context = "..." + context
                            if end < len(line):
                                context = context + "..."
                            examples.append(context)
                else:
                    examples.append(line)

                if len(examples) >= max_examples:
                    break

        if len(examples) >= max_examples:
            break

    # Also look for common French words in context
    for line in lines:
        if len(examples) >= max_examples:
            break

        line_upper = line.upper()
        # Look for lines with multiple French indicators
        french_count = sum(1 for fw in FRENCH_WORDS if fw in line_upper)
        if french_count >= 2 and line.strip() and line not in examples:
            if len(line) > 80:
                examples.append(line[:77] + "...")
            else:
                examples.append(line)

    return list(set(examples))[:max_examples]  # Remove duplicates

def analyze_text_patterns(text):
    """Analyze patterns of French text."""
    lines = text.split('\n')

    # Categorize French content
    short_phrases = []  # 1-3 words
    medium_phrases = []  # 4-8 words
    long_sentences = []  # 9+ words

    for line in lines:
        line = line.strip()
        if not line:
            continue

        line_upper = line.upper()
        french_count = sum(1 for fw in FRENCH_WORDS if fw in line_upper)

        if french_count >= 1:
            words = line.split()
            word_count = len(words)

            if word_count <= 3:
                short_phrases.append(line)
            elif word_count <= 8:
                medium_phrases.append(line)
            else:
                long_sentences.append(line)

    return {
        'short_phrases': len(short_phrases),
        'medium_phrases': len(medium_phrases),
        'long_sentences': len(long_sentences),
        'examples_short': short_phrases[:5],
        'examples_medium': medium_phrases[:5],
        'examples_long': long_sentences[:3]
    }

def analyze_pdf(pdf_path):
    """Analyze a single PDF for French content."""
    print(f"\n{'='*80}")
    print(f"Analyzing: {os.path.basename(pdf_path)}")
    print(f"{'='*80}")

    # Extract text
    text = extract_text_from_pdf(pdf_path)
    total_chars = len(text)
    total_words = len(text.split())

    print(f"Total characters: {total_chars:,}")
    print(f"Total words: {total_words:,}")

    # Count French words
    print(f"\n--- French Word Counts ---")
    french_counts = count_word_occurrences(text, FRENCH_WORDS)
    total_french = sum(french_counts.values())
    for word, count in sorted(french_counts.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"{word:15s}: {count:4d}")
    print(f"{'Total French':15s}: {total_french:4d}")

    # Count English words
    print(f"\n--- English Word Counts ---")
    english_counts = count_word_occurrences(text, ENGLISH_WORDS)
    total_english = sum(english_counts.values())
    for word, count in sorted(english_counts.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"{word:15s}: {count:4d}")
    print(f"{'Total English':15s}: {total_english:4d}")

    # Calculate ratio
    if total_french + total_english > 0:
        french_ratio = total_french / (total_french + total_english) * 100
        print(f"\nFrench/English Ratio: {french_ratio:.1f}% French")

    # Find French phrase examples
    print(f"\n--- Examples of French Phrases (up to 15) ---")
    examples = find_french_phrases(text)
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example}")

    # Analyze patterns
    print(f"\n--- Pattern Analysis ---")
    patterns = analyze_text_patterns(text)
    print(f"Short phrases (1-3 words): {patterns['short_phrases']}")
    print(f"Medium phrases (4-8 words): {patterns['medium_phrases']}")
    print(f"Long sentences (9+ words): {patterns['long_sentences']}")

    if patterns['examples_short']:
        print(f"\nExample short phrases:")
        for ex in patterns['examples_short']:
            print(f"  - {ex}")

    if patterns['examples_medium']:
        print(f"\nExample medium phrases:")
        for ex in patterns['examples_medium']:
            print(f"  - {ex}")

    if patterns['examples_long']:
        print(f"\nExample long sentences:")
        for ex in patterns['examples_long']:
            print(f"  - {ex}")

    return {
        'filename': os.path.basename(pdf_path),
        'total_words': total_words,
        'french_counts': french_counts,
        'english_counts': english_counts,
        'total_french': total_french,
        'total_english': total_english,
        'patterns': patterns,
        'examples': examples
    }

def main():
    """Main analysis function."""
    pdf_dir = r"C:\Users\yichao\Documents\pdfTranslate\translated_pdfs"

    pdf_files = [
        "A-001 - NOTES ET LEGENDS.pdf",
        "A-021 - ANALYSE DE CODE.pdf",
        "A-062 - DÉTAILS PORTES ET CADRES.pdf",
        "A-063 - BORDEREAU DES PORTES, CADRES ET OUVERTURES.pdf",
        "A-171b - PLAN D'WATERPROOFING DES FONDATIONS (INTERFACES).pdf"
    ]

    results = []

    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_dir, pdf_file)
        if os.path.exists(pdf_path):
            result = analyze_pdf(pdf_path)
            results.append(result)
        else:
            print(f"\nWARNING: File not found: {pdf_path}")

    # Summary
    print(f"\n\n{'='*80}")
    print("SUMMARY ACROSS ALL PDFs")
    print(f"{'='*80}")

    for result in results:
        print(f"\n{result['filename']}:")
        print(f"  Total words: {result['total_words']:,}")
        print(f"  French word occurrences: {result['total_french']}")
        print(f"  English word occurrences: {result['total_english']}")
        if result['total_french'] + result['total_english'] > 0:
            ratio = result['total_french'] / (result['total_french'] + result['total_english']) * 100
            print(f"  French ratio: {ratio:.1f}%")

if __name__ == "__main__":
    main()
