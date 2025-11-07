"""Test different PyMuPDF extraction methods for proper accent capture"""
import fitz

pdf_path = "original/A-001 - NOTES ET LÉGENDES.pdf"
doc = fitz.open(pdf_path)
page = doc[0]

print("="*80)
print("TESTING DIFFERENT EXTRACTION METHODS")
print("="*80)

# Test string that should contain accents
test_area = "Look for: 'plancher flottant stratifié' and 'GÉNÉRALES'"

print("\n1. METHOD: get_text('text') - Simple text extraction")
print("-"*80)
text_simple = page.get_text("text")
lines = text_simple.split('\n')
for i, line in enumerate(lines[:30]):
    if 'plancher' in line.lower() or 'g�n�ral' in line.lower() or 'général' in line.lower():
        print(f"  Line {i}: {line}")

print("\n2. METHOD: get_text('dict') - Current method (structured)")
print("-"*80)
blocks = page.get_text("dict")["blocks"]
count = 0
for block in blocks:
    if block.get("type") == 0 and count < 10:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span.get("text", "")
                if 'plancher' in text.lower() or 'général' in text.lower() or 'g�n�ral' in text.lower():
                    print(f"  Span: {text}")
                    count += 1

print("\n3. METHOD: get_text('html') - HTML with encoding")
print("-"*80)
html_text = page.get_text("html")
# Extract just text parts with accents
if 'plancher' in html_text.lower():
    start = html_text.lower().find('plancher')
    snippet = html_text[max(0, start-20):start+80]
    print(f"  HTML snippet: {snippet}")

print("\n4. METHOD: get_text('rawdict') - Raw character codes")
print("-"*80)
raw_blocks = page.get_text("rawdict")["blocks"]
count = 0
for block in raw_blocks:
    if block.get("type") == 0 and count < 10:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span.get("text", "")
                chars = span.get("chars", [])
                if 'plancher' in text.lower() or 'g�n�ral' in text.lower():
                    print(f"  Text: {text}")
                    if chars:
                        char_info = [(c.get('c', '?'), c.get('origin', (0,0))) for c in chars[:10]]
                        print(f"    Chars: {char_info}")
                    count += 1

print("\n5. COMPARISON: First 5 text blocks with all methods")
print("-"*80)

# Get first 5 meaningful text blocks
simple_lines = [l for l in page.get_text("text").split('\n') if l.strip()][:5]
dict_blocks = page.get_text("dict")["blocks"]
dict_texts = []
for block in dict_blocks[:10]:
    if block.get("type") == 0:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span.get("text", "").strip()
                if text:
                    dict_texts.append(text)
                    if len(dict_texts) >= 5:
                        break
            if len(dict_texts) >= 5:
                break
        if len(dict_texts) >= 5:
            break

for i in range(min(5, len(simple_lines), len(dict_texts))):
    print(f"\n  Block {i}:")
    print(f"    Simple: {simple_lines[i]}")
    print(f"    Dict:   {dict_texts[i]}")

    # Compare characters
    if simple_lines[i] != dict_texts[i]:
        print(f"    >>> DIFFERENT! Checking for accent differences...")
        for j, (c1, c2) in enumerate(zip(simple_lines[i], dict_texts[i])):
            if c1 != c2:
                print(f"        Pos {j}: '{c1}' (simple) vs '{c2}' (dict) - codes: {ord(c1)} vs {ord(c2)}")

doc.close()
