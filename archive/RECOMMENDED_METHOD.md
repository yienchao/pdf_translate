# RECOMMENDED: Method 10 with Task Agents

## Why Method 10 is Best

✅ **Handles PDF evolution** - Only translates new/changed text when PDF is updated
✅ **Memory grows automatically** - Each PDF improves all future translations
✅ **Cross-PDF reuse** - Translations work across ALL PDFs, not just one
✅ **Most cost-effective long-term** - Efficiency improves over time
✅ **No API key needed** - Uses Task agents directly

## Quick Start

### 1. First Translation
```bash
python method10_with_agents.py "A-001 - INPUT.pdf" "A-001 - OUTPUT.pdf"
```
Creates: `A-001_pending_translations.json`

### 2. Translate with Agent
Tell Claude Code:
> "Use Task agent with haiku to translate A-001_pending_translations.json to A-001_translated.json"

### 3. Merge into Memory
```bash
python merge_translations.py A-001_pending_translations.json
```

### 4. Build PDF
```bash
python method10_with_agents.py "A-001 - INPUT.pdf" "A-001 - OUTPUT.pdf"
```

Done! PDF is translated.

## For Multiple PDFs

Process in parallel:
1. Run method10_with_agents.py on all PDFs (creates pending files)
2. Launch multiple Task agents in parallel (one per pending file)
3. Run merge_translations.py for each
4. Re-run method10_with_agents.py on all PDFs

## When PDF Changes

Just run step 1 again! Method 10 automatically:
- Detects unchanged text (reuses from memory)
- Only creates pending file for NEW/CHANGED text
- You only translate the differences

## Files

- `method10_with_agents.py` - Main script (NO API keys)
- `merge_translations.py` - Merge helper
- `translation_memory.json` - Growing translation dictionary
- `{PDF}_pending_translations.json` - Temp: items needing translation
- `{PDF}_translated.json` - Temp: agent output

## Cost (700 pages estimate)

- First 100 pages: ~$10
- Next 600 pages: ~$25 (with growing reuse)
- **Total: ~$35 with automatic efficiency gains**

Compare: Method 9 without growth would be ~$15-20 each time you process 700 pages

## See Also

- [method10_fixed.md](.claude/method10_fixed.md) - Full documentation
- [custom_instructions.md](.claude/custom_instructions.md) - Behavior rules
