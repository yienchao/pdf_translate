# AI-Powered PDF Translation

## Overview

This project now includes **AI-powered translation** using Claude API, which can translate ANY French text to English automatically!

## Methods Available

### Method 1-3: Dictionary-Based (Original)
- ✓ Fast
- ✓ No API costs
- ✗ Limited to predefined terms

### Method 4: AI-Powered Hybrid (NEW!)
- ✓ Translates ANY French text
- ✓ Contextual understanding
- ✓ Falls back to dictionary for common terms (faster + cheaper)
- ✓ Works with new documents automatically
- ⚠ Requires Anthropic API key

## Setup

### 1. Get an API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Generate an API key
4. Copy the key (starts with `sk-ant-...`)

### 2. Set the API Key

**Option A: Environment Variable (Recommended)**
```bash
# Windows Command Prompt
set ANTHROPIC_API_KEY=sk-ant-your-key-here

# Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Linux/Mac
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Option B: In Code**
```python
translate_pdf_method4(input_pdf, output_pdf, api_key="sk-ant-your-key-here")
```

## Usage

### Method 4: AI-Powered Translation

```python
python method4_ai_powered.py
```

This will:
1. ✓ Try dictionary first (fast, free)
2. ✓ Fall back to AI for unknown terms (smart, comprehensive)
3. ✓ Create: `AR-001 - METHOD4 - AI-POWERED.pdf`

### Testing AI Translator

```python
# Test the AI translator
python ai_translator.py

# Test the hybrid approach
python hybrid_translator.py
```

## How It Works

### Hybrid Translation Flow

```
French Text: "LÉGENDES ET NOTES GÉNÉRALES"
    ↓
[1] Check Dictionary
    ├─ Found? → "LEGENDS AND GENERAL NOTES" ✓
    └─ Not found? → Continue to AI
        ↓
[2] Claude AI Translation
    └─ "LEGENDS AND GENERAL NOTES" ✓
```

### Benefits

1. **Fast for Common Terms**
   - Dictionary lookup is instant
   - No API calls for known terms

2. **Smart for Unknown Terms**
   - AI understands context
   - Handles technical terminology
   - Works with any French text

3. **Cost Effective**
   - Caches translations
   - Uses fast Haiku model
   - Only calls AI when needed

## Cost Estimate

Using Claude 3 Haiku (cheapest model):
- **Input:** $0.25 per million tokens
- **Output:** $1.25 per million tokens

For a typical architectural PDF (like AR-001):
- ~1,000 words = ~1,300 tokens
- Cost: ~$0.002 per page (less than a penny!)

## Files Created

```
pdfTranslate/
├── method1_redact_replace.py      # Dictionary only
├── method4_ai_powered.py          # AI-powered! ⭐
├── ai_translator.py               # Claude API wrapper
├── hybrid_translator.py           # Dictionary + AI hybrid
├── translation_dictionary.py      # Common terms dictionary
└── README_AI_TRANSLATION.md       # This file
```

## Troubleshooting

### "No API key found"
- Set the `ANTHROPIC_API_KEY` environment variable
- Or pass `api_key` parameter directly

### "AI translation error"
- Check your API key is valid
- Ensure you have API credits
- Check internet connection

### Without API Key
The script will still work using dictionary only (like Method 1), but won't translate unknown terms.

## Comparison

| Feature | Dictionary Only | AI-Powered |
|---------|----------------|------------|
| Speed | ⚡ Instant | 🚀 Fast |
| Coverage | Limited terms | **Any text** ✓ |
| Accuracy | Good for known | **Excellent** ✓ |
| Cost | Free | ~$0.002/page |
| Setup | None | API key needed |

## Next Steps

1. **Get API key** from https://console.anthropic.com/
2. **Set environment variable** `ANTHROPIC_API_KEY`
3. **Run Method 4** `python method4_ai_powered.py`
4. **Enjoy automatic translation!** 🎉

For any questions, check the code comments or modify the scripts as needed!
