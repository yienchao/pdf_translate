"""
Find remaining French text in translated PDF
"""
import fitz
import re

def has_french(text):
    """Check if text has French indicators"""
    french_words = [
        'DE', 'ET', 'LE', 'LA', 'LES', 'DU', 'DES', 'AU', 'AUX', 'SUR',
        'AVEC', 'POUR', 'PAR', 'DANS', 'QUI', 'QUE', 'UN', 'UNE', 'SONT', 'EST',
        'TOUS', 'TOUTES', 'TOUT', 'VOIR', 'OU', 'ASSEMBLAGE', 'ENVELOPPE'
    ]

    # Don't flag if sentence starts with SIC (Latin, used in English)
    if text.strip().upper().startswith('SIC,'):
        return False

    # Check for French words
    words = text.upper().split()
    french_count = 0
    for word in words:
        word_clean = re.sub(r'[^\w]', '', word)
        if word_clean in french_words:
            french_count += 1
        # Check for accented characters (corrupted or proper) but not in technical codes
        if any(c in word for c in 'ÀÂÆÇÉÈÊËÏÎÔÙÛÜàâæçéèêëïîôùûüÿœ') and len(word) > 4:
            french_count += 1

    # Only flag if multiple French words (not just one 'ou' or 'en')
    return french_count >= 2

def should_skip(text):
    """Skip numbers, units, symbols, technical codes"""
    if not text or not text.strip():
        return True
    if not any(c.isalpha() for c in text):
        return True

    # Skip technical codes/acronyms (2-4 chars with � or short lowercase)
    if len(text) <= 4 and '�' in text:
        return True
    if len(text) <= 3 and text.islower() and text.isalpha():
        return True

    # Skip Latin terms
    if text.upper() == 'SIC':
        return True

    return False

# Check translated PDF
pdf_path = "A-001 - NOTES AND LEGENDS.pdf"
print(f"Checking: {pdf_path}\n")

doc = fitz.open(pdf_path)
remaining_french = []

for page_num in range(len(doc)):
    page = doc[page_num]
    text_dict = page.get_text("dict")
    blocks = text_dict.get("blocks", [])

    for block in blocks:
        if block.get("type") == 0:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "")
                    if should_skip(text):
                        continue
                    if has_french(text):
                        remaining_french.append(text)

doc.close()

print(f"Found {len(remaining_french)} text elements with French\n")
print("First 50 examples:")
for i, text in enumerate(remaining_french[:50], 1):
    print(f"{i}. {text}")
