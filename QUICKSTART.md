# 🚀 Quick Start Guide - PDF Translator with Anthropic API

## Start the App

**Option 1 - Double-click:**
```
start_app.bat
```

**Option 2 - Command line:**
```bash
streamlit run app.py
```

The app will open at **http://localhost:8501**

---

## Using the App

### 1. **Enter Your API Key**
- In the sidebar, paste your Anthropic API key
- Click outside the text box to save it

### 2. **Upload a PDF**
- Click "Browse files"
- Select a French PDF (e.g., A-001, A-062, A-063)

### 3. **Translate**

**If items need translation:**
- Click **"🤖 Auto-Translate with AI"** (uses your API key)
- Wait for Claude Haiku 4.5 to translate
- Then click **"🚀 Translate PDF"** to apply to the PDF

**If all in dictionary:**
- Click **"🚀 Translate PDF"** directly

### 4. **Download**
- Download your translated PDF
- Check the "Files" tab for all previous translations

---

## Features

✅ **Automatic Translation** - Uses Claude Haiku 4.5 via Anthropic API
✅ **Smart Dictionary** - Reuses common translations (2,237 entries)
✅ **Batch Processing** - Handles large PDFs efficiently
✅ **Cost Effective** - Uses Haiku (cheapest model)
✅ **No Data Loss** - Preserves all PDF formatting

---

## API Costs (Haiku 4.5)

Haiku 4.5 pricing:
- **Input**: $0.80 / million tokens
- **Output**: $4.00 / million tokens

Typical PDF (A-001):
- ~100 items to translate
- ~$0.01 - $0.05 per PDF

Very affordable! 💰

---

## Troubleshooting

**"API key not set"**
- Enter your key in the sidebar

**"Translation failed"**
- Check your API key is valid
- Check you have API credits

**App won't start**
- Run: `pip install -r requirements.txt`
- Make sure Streamlit is installed

---

## Next Steps - Deploy to Render

1. Create account on Render.com
2. Connect your GitHub repo
3. Set environment variable: `ANTHROPIC_API_KEY`
4. Deploy as Web Service
5. Access from anywhere!

See `README_STREAMLIT.md` for deployment details.
