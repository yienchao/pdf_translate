# Method 12: PDF Translation with Redaction

## Overview
Method 12 is an improved PDF translation system that properly removes French text and replaces it with English translations. It fixes the major issue in Method 9 where French text remained visible even after "translation."

## Key Improvements Over Method 9

### 1. **Proper Text Removal (Redaction)**
- **Method 9**: Drew white rectangles over text (text still exists in PDF layers)
- **Method 12**: Uses `add_redact_annot()` + `apply_redactions()` to actually remove text
- **Result**: Method 12 achieves ~95% English vs Method 9's ~20%

### 2. **Dual Dictionary System**
- **Base Dictionary** (`base_french_dict.json`): 92 common French words/terms
- **Growing Dictionary** (`method12_data/translations.json`): 4,300+ learned translations
- Combined approach ensures comprehensive coverage

### 3. **Better Text Merging**
- Tighter merge thresholds (x_gap ≤ 5px) to avoid incorrect merging
- Proper bbox handling (converts tuples to lists)
- Results in more accurate phrase extraction

### 4. **Automatic Folder Processing**
- Input: `original/` folder (French PDFs)
- Output: `translated_pdfs/` folder (English PDFs)
- No manual path specification needed

## Usage

### Basic Usage
```bash
python method12_translate.py
```

This will:
1. Process all PDFs in `original/` folder
2. Check dictionary for translations
3. If new French text found, save to `method12_data/{PDF}_to_translate.json`
4. Wait for manual translation
5. Re-run to apply translations

### Manual Translation Workflow
When the script finds untranslated text:
1. It saves to: `method12_data/A-XXX_to_translate.json`
2. **Use Claude Code agent to translate** (or translate manually)
3. Save translations as: `method12_data/A-XXX_sentences.json`
4. Re-run script to apply

## File Structure

```
pdfTranslate/
├── method12_translate.py          # Main script
├── base_french_dict.json          # 92 common French words
├── method12_data/                 # Data folder
│   ├── translations.json          # Growing dictionary (4,300+ entries)
│   ├── A-001_sentences.json       # Translated sentences for A-001
│   ├── A-001_to_translate.json    # Texts needing translation
│   └── ...
├── original/                      # Input: French PDFs
│   ├── A-001 - NOTES ET LÉGENDES.pdf
│   └── ...
└── translated_pdfs/               # Output: English PDFs
    ├── A-001 - NOTES ET LEGENDS.pdf
    └── ...
```

## Translation Logic

### 1. Text Extraction
- Extract all text with bounding boxes from PDF
- Merge adjacent spans (same line, close horizontally)
- Each text element stores: text, bbox, size, color, page

### 2. Translation Decision
For each text element:
```python
if should_skip(text):           # Empty, numbers only, units
    keep original
elif text in TRANSLATION_DICT:  # Dictionary lookup (case-insensitive)
    use translation
elif has_french(text):          # Contains French indicators
    mark for manual translation
else:
    keep original (assume English)
```

### 3. French Detection
Text is considered French if it contains:
- French words: DE, ET, LE, LA, LES, POUR, VOIR, AVEC, DANS, etc.
- French technical terms: INGÉNIERIE, BÉTON, PLAFOND, CLOISON, etc.
- Accented characters: À, É, È, Ê, Ç, etc.

### 4. PDF Application
```python
for each page:
    1. Add redaction annotations (tight bbox)
    2. Apply redactions (removes original text)
    3. Insert translated text (same position, size, color)
    4. Save PDF
```

## Configuration

### Adjustable Parameters

#### Merge Threshold
```python
close_horizontal = -1 <= x_gap <= 5  # Default: 5px
```
- **Lower value**: More separate text elements (less merging)
- **Higher value**: Fewer, longer text elements (more merging)

#### Redaction Padding
```python
rect = fitz.Rect(bbox[0] + 0.5, bbox[1] + 0.5, bbox[2] - 0.5, bbox[3] - 0.5)
```
- **Current**: Tight bbox with 0.5px inset (minimal white gaps)
- **Adjust**: Change padding values if white gaps are too large/small

#### French Detection Words
Edit the `has_french()` function to add/remove French indicators.

## Results

### Translation Accuracy (A-001 PDF)
| Metric | Method 9 | Method 12 | Improvement |
|--------|----------|-----------|-------------|
| "VOIR" count | 66 | 4 | 94% reduction |
| "INGÉNIERIE" count | 51 | 0 | 100% removed |
| "SEE" count | 49 | 54 | +10% |
| "ENGINEERING" count | 40 | 46 | +15% |
| **Overall French** | ~30-40% | ~5% | **~95% English** |

### Performance
- ~1-2 seconds per page
- Dictionary size: 4,330 entries
- Memory efficient (processes one page at a time)

## Troubleshooting

### Issue: White gaps too large
**Solution**: Reduce redaction padding in line 283:
```python
rect = fitz.Rect(bbox[0] + 1.0, bbox[1] + 1.0, bbox[2] - 1.0, bbox[3] - 1.0)
```

### Issue: French text still visible
**Cause**: Text might be in multiple layers or merged incorrectly
**Solution**:
1. Check if text is in dictionary: `python -c "from method12_translate import *; print(translate_with_dict('YOUR TEXT'))"`
2. Verify text merging: Adjust `close_horizontal` threshold

### Issue: Translations look wrong
**Cause**: Word-by-word translation creates gibberish
**Solution**: Add the full phrase to dictionary or translate manually

### Issue: Script stops with "ACTION REQUIRED"
**Normal behavior**: Waiting for manual translation
**Solution**: Follow the 3 steps printed by the script

## Best Practices

1. **Always backup original PDFs** before processing
2. **Process PDFs incrementally** - translate one, verify, then continue
3. **Review translated PDFs** - automated translation isn't perfect
4. **Update base_french_dict.json** with common terms you find
5. **Keep method12_data/** folder - it's your growing knowledge base

## Future Improvements

Potential enhancements:
- [ ] Automatic Claude API translation (remove manual step)
- [ ] Multi-language support (not just French→English)
- [ ] OCR support for scanned PDFs
- [ ] Parallel processing for faster batch translation
- [ ] GUI interface for easier use
- [ ] Translation quality scoring
- [ ] Font matching for better visual consistency

## Technical Details

### Dependencies
- **PyMuPDF (fitz)**: PDF manipulation
- **json**: Dictionary storage
- **pathlib**: File operations

### PDF Layer Handling
PDFs can have multiple text layers:
1. **Content Stream**: Rendered text (what you see)
2. **Text Layer**: Extractable text (for copying)
3. **Annotations**: Overlaid text

Method 9 only added layer 3 (annotations), leaving original text visible.
Method 12 removes layer 1 & 2 via redaction, then adds layer 3 cleanly.

### Redaction vs White Rectangles
```python
# Method 9 (doesn't work properly)
page.draw_rect(rect, fill=(1,1,1))  # Just covers visually

# Method 12 (properly removes)
page.add_redact_annot(rect, fill=(1,1,1))
page.apply_redactions()  # Actually removes content
```

## License & Credits
Created as an improvement over Method 9 for the pdfTranslate project.
Uses PyMuPDF for PDF manipulation.
