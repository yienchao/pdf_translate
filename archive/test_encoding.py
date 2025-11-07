import sys
sys.stdout.reconfigure(encoding='utf-8')

from translate_clean import normalize_accents, translate_with_dict

# Simul corrupted PDF text
corrupted = "RETOUR (VOIR DOCUMENTS D'ING\ufffdNIERIE)"
print(f'Corrupted text: {corrupted}')
print(f'Has \\ufffd: {chr(0xfffd) in corrupted}')

normalized = normalize_accents(corrupted)
print(f'Normalized: {normalized}')

translation = translate_with_dict(corrupted)
print(f'Translation: {translation}')
