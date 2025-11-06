# Method 9: Hybrid Dictionary + Haiku Agent Translation

## Overview
The optimal PDF translation method combining instant dictionary lookups with context-aware agent translations.

## How It Works

### Step 1: Extract & Classify Text
```bash
python method11_indexed_sentences.py "input.pdf" "output.pdf"
```
- Opens PDF and extracts ALL text elements
- Classifies each text:
  - **Short (1-3 words)**: Dictionary lookup
  - **Long (4+ words)**: Mark as sentence for agent
  - **Skip**: Numbers, units, technical codes

### Step 2: Dictionary Translation (Instant - FREE)
- Short text → Look up in `translations.json` (3,857 entries)
- Example: "CLOISON" → "PARTITION"
- No cost, instant processing
- ~70% of text handled here

### Step 3: Collect Sentences
- All 4+ word phrases saved to `{PDF_CODE}_sentences.json`
- Format: `{"0": "French sentence...", "1": "Another sentence..."}`
- Example counts:
  - A-001: 259 sentences
  - A-081: 76 sentences

### Step 4: Agent Translation (Manual)
Launch Haiku agent to translate sentences file:
```python
Task(
  subagent_type="general-purpose",
  model="haiku",
  prompt="Translate {PDF_CODE}_sentences.json..."
)
```
- Agent translates all sentences with context
- Saves translations back to same JSON file
- Only this step costs tokens

### Step 5: Build Translated PDF
- Script runs again, combines dictionary + agent translations
- Draws white boxes over French text
- Inserts English text at exact same positions
- Preserves fonts, colors, layout perfectly

## Why Method 9 is Best

✅ **Fast**: Dictionary handles ~70% instantly
✅ **Accurate**: Agent handles complex sentences with context
✅ **Cheap**: Only uses tokens for ~30% of text
✅ **Reusable**: Dictionary grows over time
✅ **Quality**: Haiku 3.5 is fast + accurate for translation
✅ **Scalable**: Works for massive documents

## Cost Estimates

### Single Page (like A-001)
- ~970 text elements
- ~260 sentences for agent (27%)
- ~700 dictionary lookups (73% - FREE)
- Cost: ~$0.02 per page

### 700 Pages
**Text Elements:**
- Dictionary translations: ~490,000 (FREE)
- Sentences for agent: ~182,000

**Haiku 3.5 Token Usage:**
- Input: ~1.8M tokens (~$1.80)
- Output: ~2.7M tokens (~$13.50)
- **Total: $15-20 for 700 pages**

**Time:**
- Dictionary: Instant
- Agent translation: 30-60 minutes (batched)
- PDF building: 2-3 hours

## Files Used

- `method11_indexed_sentences.py` - Main script (despite name, it's Method 9)
- `translations.json` - Dictionary (3,857 entries)
- `{PDF_CODE}_sentences.json` - Per-PDF sentence cache
- Input: Original French PDF
- Output: Translated English PDF

## Usage Example

```bash
# Step 1: Run script (creates sentences file)
python method11_indexed_sentences.py "A-001 - NOTES ET LÉGENDES.pdf" "A-001 - NOTES AND LEGENDS.pdf"

# Step 2: Translate sentences with agent (in parallel if multiple PDFs)
# Use Task tool with model="haiku" to translate A-001_sentences.json

# Step 3: Run script again (uses translated sentences)
python method11_indexed_sentences.py "A-001 - NOTES ET LÉGENDES.pdf" "A-001 - NOTES AND LEGENDS.pdf"
```

## Comparison to Other Methods

### vs Method 10 (Hash-Based)
- ✅ Method 9: Works immediately, no pending files
- ✅ Method 9: Better context understanding
- ❌ Method 10: Requires API key setup
- ❌ Method 10: Creates pending translation files

### vs Method 11 (Pure Agent)
- ✅ Method 9: 70% faster (dictionary)
- ✅ Method 9: Much cheaper
- ✅ Method 9: More consistent terminology
- ❌ Method 11: Simpler but expensive
- ❌ Method 11: Can miss text or be inconsistent

## Tips

1. **Batch Processing**: Translate multiple PDFs' sentences in parallel using multiple Task agents
2. **Dictionary Growth**: Add new terms to `translations.json` as you encounter them
3. **Quality Check**: Always verify critical technical terms
4. **Reuse Sentences**: Keep `*_sentences.json` files for future reference

## Recent Translations

- ✅ A-001 - NOTES AND LEGENDS.pdf (589 dictionary + 259 agent)
- ✅ A-081 - FINISHES SCHEDULE.pdf (405 dictionary + 76 agent)

## Notes

- User has Claude MAX subscription
- Never ask for ANTHROPIC_API_KEY
- Use Task agents with model="haiku"
- Work in parallel when possible
- This is the preferred method going forward
