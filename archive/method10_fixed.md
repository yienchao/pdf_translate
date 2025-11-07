# Method 10: Hash-Based Translation with Task Agents (FIXED)

## Overview
Hash-based translation memory system that works reliably with Claude Code's Task agents. Every piece of text is hashed and stored once, reused everywhere. Dictionary grows automatically across all PDFs.

## Why Method 10 is Best for Evolving PDFs

✅ **Handles PDF changes** - Only translates new/changed text
✅ **Memory grows automatically** - Each PDF improves future translations
✅ **Works across all PDFs** - Reuses translations everywhere
✅ **Efficient** - Dictionary provides instant lookups, agent handles rest
✅ **Cost-effective** - Only translates new content

## Complete Workflow

### Step 1: First Pass - Extract & Identify
```bash
python method_hash_based.py "A-001 - NOTES ET LÉGENDES.pdf" "A-001 - NOTES AND LEGENDS.pdf"
```

**Output:**
- Creates `A-001_pending_translations.json`
- Format: `{"hash123...": "French text to translate", ...}`
- Shows cache hit rate (how many already translated)

### Step 2: Translate with Task Agent

Launch a Task agent to translate the pending file:

```python
# In Claude Code, use Task tool:
Task(
  subagent_type="general-purpose",
  model="haiku",
  description="Translate A-001 pending items",
  prompt="""
  Translate the French architectural terms in A-001_pending_translations.json to English.

  Working directory: c:\\Users\\yichao\\Documents\\pdfTranslate

  Steps:
  1. Read A-001_pending_translations.json
  2. Translate ALL French values to English (architectural/construction terminology)
  3. Keep the same hash keys
  4. Save to A-001_translated.json with format:
     {"hash_key": "English translation", ...}

  Output format must be:
  {
    "hash123...": "English translation 1",
    "hash456...": "English translation 2",
    ...
  }

  Translate everything and save to A-001_translated.json
  """
)
```

**Agent creates:** `A-001_translated.json`

### Step 3: Merge into Memory
```bash
python merge_translations.py A-001_pending_translations.json
```

**This:**
- Reads `A-001_translated.json`
- Merges into `translation_memory.json`
- Memory grows from 994 → 994 + new translations

### Step 4: Build Translated PDF
```bash
python method_hash_based.py "A-001 - NOTES ET LÉGENDES.pdf" "A-001 - NOTES AND LEGENDS.pdf"
```

**Now:**
- Uses updated translation_memory.json
- 100% cache hit rate
- Builds final PDF

## For Multiple PDFs in Parallel

You can translate multiple PDFs at once:

```python
# Launch agents in parallel (single message with multiple Task calls):
Task(model="haiku", prompt="Translate A-001_pending_translations.json...")
Task(model="haiku", prompt="Translate A-081_pending_translations.json...")
Task(model="haiku", prompt="Translate A-302_pending_translations.json...")
```

Then merge all:
```bash
python merge_translations.py A-001_pending_translations.json
python merge_translations.py A-081_pending_translations.json
python merge_translations.py A-302_pending_translations.json
```

## Handling PDF Revisions

When a PDF changes (new revision):

```bash
# Run Method 10 again
python method_hash_based.py "A-001 - NOTES ET LÉGENDES Rev2.pdf" "A-001 - NOTES AND LEGENDS Rev2.pdf"
```

**Method 10 automatically:**
- ✅ Detects unchanged text (cache hit)
- ✅ Detects new/changed text (only these go to pending)
- ✅ You only translate what changed!

**Example:**
- Original PDF: 589 items
- Revised PDF: 595 items (6 new)
- Only 6 items in pending file
- Agent translates just 6 items
- Memory grows by 6

## Files Used

**Core Files:**
- `method_hash_based.py` - Main script
- `translation_memory.json` - Growing hash-based dictionary
- `merge_translations.py` - Merge helper

**Per-PDF Files:**
- `{PDF_CODE}_pending_translations.json` - Items needing translation
- `{PDF_CODE}_translated.json` - Agent output

## Cost Estimate (700 pages)

Assuming similar to A-001:
- First 100 pages: ~60,000 items to translate (~$10)
- Next 100 pages: ~40,000 new items (~$7) - 33% reuse!
- Next 100 pages: ~30,000 new items (~$5) - 50% reuse!
- Last 400 pages: ~80,000 new items (~$13) - 70% reuse!

**Total: ~$35 for 700 pages with growing efficiency**

Compare to Method 9 without growth: $15-20 but NO reuse across PDFs

## Advantages Over Method 9

| Feature | Method 9 | Method 10 (Fixed) |
|---------|----------|-------------------|
| Dictionary lookups | ✅ 3,857 static | ✅ Grows automatically |
| Handles PDF changes | ❌ Must delete cache | ✅ Auto-detects changes |
| Cross-PDF reuse | ❌ Only within same PDF | ✅ Across ALL PDFs |
| Memory growth | ❌ Manual only | ✅ Automatic |
| Cost over time | Same every time | ✅ Decreases over time |

## Initial Setup: Import Method 9 Dictionary

To bootstrap translation_memory.json with Method 9's dictionary:

```bash
python -c "
import json
import hashlib

# Load Method 9 dictionary
with open('translations.json', 'r', encoding='utf-8') as f:
    dict9 = json.load(f)

# Load existing memory
try:
    with open('translation_memory.json', 'r', encoding='utf-8') as f:
        memory = json.load(f)
except:
    memory = {}

# Convert to hashes
for french, english in dict9.items():
    normalized = ' '.join(french.split())
    hash_key = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    memory[hash_key] = english

# Save
with open('translation_memory.json', 'w', encoding='utf-8') as f:
    json.dump(memory, f, ensure_ascii=False, indent=2)

print(f'Imported {len(dict9)} entries from Method 9')
print(f'Total in memory: {len(memory)} entries')
"
```

## Troubleshooting

**Agent didn't create translated file?**
- Check agent completed successfully
- Look for `*_translated.json` file
- Re-run agent with clearer instructions

**Translations look wrong?**
- Review a few entries in `*_translated.json`
- Edit manually if needed before merging
- Re-run merge script

**PDF still has French?**
- Check cache hit rate (should be 100% after merge)
- Verify translation_memory.json has entries
- Re-run Step 4

## Notes

- User has Claude MAX - never ask for API keys
- Always use Task agents with model="haiku"
- Work in parallel when possible
- This is now the preferred method for production use
