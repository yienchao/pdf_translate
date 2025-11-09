# Streamlit PDF Translator - Local Setup

## Installation

1. **Install dependencies:**
   ```bash
   pip install streamlit PyMuPDF
   ```

   Or install from requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app:**
   ```bash
   streamlit run app.py
   ```

3. **Open browser:**
   - The app will automatically open at `http://localhost:8501`
   - Or manually navigate to that URL

## How to Use

### Upload & Translate Tab
1. Click "Browse files" to upload a French PDF
2. View extraction statistics:
   - **Total Elements**: All text blocks found
   - **In Dictionary**: Already have translations
   - **Needs Translation**: Require new translations
   - **Skipped**: Numbers, codes, etc.

3. If items need translation:
   - Click "Extract items for translation"
   - Download the JSON file
   - Translate it (manually or with AI)
   - Save as `method9_data/A-XXX_indexed.json`
   - Re-upload PDF and click "Translate"

4. If all in dictionary:
   - Click "Translate PDF" directly
   - Download the translated result

### Files Tab
- View all previously translated PDFs
- Download any previous translation

## File Structure

```
pdfTranslate/
├── app.py                          # Streamlit app
├── translate_clean.py              # Translation engine
├── requirements.txt                # Dependencies
├── uploads/                        # Temporary uploaded PDFs
├── translated_pdfs/                # Output translated PDFs
└── method9_data/
    ├── base_french_dict.json      # Base vocabulary
    ├── translations.json           # Growing dictionary
    ├── A-001_to_translate.json    # Items needing translation
    └── A-001_indexed.json         # Translated items
```

## Next Steps

### For Anthropic API Integration:
1. Add `anthropic` to requirements.txt
2. Set API key as environment variable or Streamlit secret
3. Modify app to call Anthropic API for translation

### For Render Deployment:
1. Create `render.yaml` configuration
2. Set up persistent disk for `method9_data/`
3. Add environment variables for API keys
4. Deploy!

## Troubleshooting

**Port already in use:**
```bash
streamlit run app.py --server.port 8502
```

**Missing dependencies:**
```bash
pip install -r requirements.txt
```

**Dictionary not found:**
- Ensure `method9_data/` folder exists
- Check that `base_french_dict.json` and `translations.json` are present
