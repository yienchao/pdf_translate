"""
Check A-530 for remaining French
"""
import fitz
import re

def has_french(text):
    french_words = [
        'DE', 'ET', 'LE', 'LA', 'LES', 'DU', 'DES', 'AU', 'AUX', 'SUR',
        'AVEC', 'POUR', 'PAR', 'DANS', 'QUI', 'QUE', 'UN', 'UNE', 'SONT', 'EST',
        'TOUS', 'TOUTES', 'TOUT', 'VOIR', 'OU', 'ASSEMBLAGE', 'ENVELOPPE'
    ]

    if text.strip().upper().startswith('SIC,'):
        return False

    words = text.upper().split()
    french_count = 0
    for word in words:
        word_clean = re.sub(r'[^\w]', '', word)
        if word_clean in french_words:
            french_count += 1
        if any(c in word for c in 'ÀÂÆÇÉÈÊËÏÎÔÙÛÜàâæçéèêëïîôùûüÿœ') and len(word) > 4:
            french_count += 1

    return french_count >= 2

def should_skip(text):
    if not text or not text.strip():
        return True
    if not any(c.isalpha() for c in text):
        return True
    if len(text) <= 4 and '�' in text:
        return True
    if len(text) <= 3 and text.islower() and text.isalpha():
        return True
    if text.upper() == 'SIC':
        return True
    return False

doc = fitz.open("A-530 - ENVELOPE DETAILS (SECTION).pdf")
remaining = []

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
                        remaining.append(text)

doc.close()

print(f"A-530: Found {len(remaining)} French text elements\n")
print("First 30:")
for i, text in enumerate(remaining[:30], 1):
    print(f"{i}. {text}")
