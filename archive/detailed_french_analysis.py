"""
Deep analysis: Extract actual French text from translated PDFs and compare to dictionary
"""

import fitz
import json
import os

# Load dictionary
with open('method9_data/translations.json', 'r', encoding='utf-8') as f:
    TRANSLATION_DICT = json.load(f)

def extract_all_text_with_positions(pdf_path):
    """Extract every text span with its position"""
    doc = fitz.open(pdf_path)
    all_spans = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if block.get("type") == 0:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        if text:
                            all_spans.append({
                                "page": page_num + 1,
                                "text": text,
                                "bbox": span["bbox"],
                                "size": span["size"]
                            })

    doc.close()
    return all_spans

def has_french_indicators(text):
    """Check if text has French words"""
    french_words = [
        'VOIR', 'POUR', 'DANS', 'AVEC', 'DE', 'DES', 'LES', 'ET', 'SONT',
        'PORTE', 'PORTES', 'CADRE', 'CADRES', 'DÉTAILS', 'PLAN', 'NOTES',
        'AU', 'DU', 'LA', 'LE', 'SUR', 'PAR', 'TOUS', 'EST', 'À'
    ]

    text_upper = text.upper()
    words = text_upper.split()

    for word in words:
        clean = word.strip('.,;:()[]{}!?-/')
        if clean in french_words:
            return True
        # Check for accented chars
        if any(c in word for c in 'ÀÂÆÇÉÈÊËÏÎÔÙÛÜàâæçéèêëïîôùûüÿœ�'):
            return True

    return False

def is_in_dictionary(text):
    """Check if text (or close variant) is in dictionary"""
    if text in TRANSLATION_DICT:
        return True

    # Case-insensitive
    text_lower = text.lower()
    for key in TRANSLATION_DICT.keys():
        if key.lower() == text_lower:
            return True

    return False

def categorize_french_text(text):
    """Categorize the type of French text"""
    words = text.split()
    word_count = len(words)

    # Single words
    if word_count == 1:
        return "single_word"

    # Short phrases (2-3 words)
    elif word_count <= 3:
        return "short_phrase"

    # Medium phrases (4-6 words)
    elif word_count <= 6:
        return "medium_phrase"

    # Long sentences
    else:
        return "long_sentence"

def analyze_pdf_deeply(pdf_path):
    """Detailed analysis of remaining French text"""
    print(f"\n{'='*80}")
    print(f"DEEP ANALYSIS: {os.path.basename(pdf_path)}")
    print('='*80)

    # Extract all text
    all_spans = extract_all_text_with_positions(pdf_path)
    print(f"Total text spans extracted: {len(all_spans)}")

    # Find French text
    french_spans = []
    for span in all_spans:
        if has_french_indicators(span["text"]):
            in_dict = is_in_dictionary(span["text"])
            category = categorize_french_text(span["text"])

            french_spans.append({
                **span,
                "in_dictionary": in_dict,
                "category": category
            })

    print(f"French text spans found: {len(french_spans)}")

    # Group by category
    categories = {
        "single_word": [],
        "short_phrase": [],
        "medium_phrase": [],
        "long_sentence": []
    }

    in_dict_count = 0
    not_in_dict_count = 0

    for span in french_spans:
        categories[span["category"]].append(span)
        if span["in_dictionary"]:
            in_dict_count += 1
        else:
            not_in_dict_count += 1

    # Summary
    print(f"\nCATEGORY BREAKDOWN:")
    for cat, items in categories.items():
        print(f"  {cat:20s}: {len(items):3d} items")

    print(f"\nDICTIONARY STATUS:")
    print(f"  In dictionary:     {in_dict_count:3d}")
    print(f"  NOT in dictionary: {not_in_dict_count:3d}")

    # Show examples of what's NOT in dictionary
    print(f"\n--- NOT IN DICTIONARY (First 15 examples) ---")
    not_in_dict = [s for s in french_spans if not s["in_dictionary"]]

    for i, span in enumerate(not_in_dict[:15], 1):
        page = span["page"]
        text = span["text"]
        cat = span["category"]
        if len(text) > 70:
            text = text[:67] + "..."
        print(f"{i:2d}. [P{page}] [{cat:15s}] {text}")

    # Show examples of what IS in dictionary but still appears
    print(f"\n--- IN DICTIONARY BUT STILL PRESENT (First 10 examples) ---")
    in_dict_examples = [s for s in french_spans if s["in_dictionary"]][:10]

    for i, span in enumerate(in_dict_examples, 1):
        page = span["page"]
        text = span["text"]
        cat = span["category"]
        translation = TRANSLATION_DICT.get(text, "???")
        if len(text) > 40:
            text = text[:37] + "..."
        if len(translation) > 40:
            translation = translation[:37] + "..."
        print(f"{i:2d}. [P{page}] {text:40s} -> {translation}")

    # Analyze patterns
    print(f"\n--- PATTERN ANALYSIS (Not in dictionary) ---")

    # Group by word count
    by_word_count = {}
    for span in not_in_dict:
        wc = len(span["text"].split())
        if wc not in by_word_count:
            by_word_count[wc] = []
        by_word_count[wc].append(span["text"])

    for wc in sorted(by_word_count.keys())[:10]:
        count = len(by_word_count[wc])
        print(f"  {wc:2d} words: {count:3d} instances")
        # Show 2 examples
        for ex in by_word_count[wc][:2]:
            if len(ex) > 60:
                ex = ex[:57] + "..."
            print(f"           - {ex}")

    return {
        "filename": os.path.basename(pdf_path),
        "total_spans": len(all_spans),
        "french_spans": len(french_spans),
        "categories": {k: len(v) for k, v in categories.items()},
        "in_dict": in_dict_count,
        "not_in_dict": not_in_dict_count,
        "examples_not_in_dict": [s["text"] for s in not_in_dict[:10]]
    }

def main():
    """Analyze all translated PDFs"""
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
            result = analyze_pdf_deeply(pdf_path)
            results.append(result)

    # Final summary
    print(f"\n\n{'='*80}")
    print("OVERALL SUMMARY")
    print('='*80)

    for r in results:
        print(f"\n{r['filename']}:")
        print(f"  Total text spans: {r['total_spans']}")
        print(f"  French spans found: {r['french_spans']}")
        print(f"  In dictionary (but still present): {r['in_dict']}")
        print(f"  NOT in dictionary: {r['not_in_dict']}")
        print(f"  Categories: {r['categories']}")

if __name__ == "__main__":
    main()
