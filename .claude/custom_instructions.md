# Custom Instructions for PDF Translation Project

## API Access & Authentication
- User has **Claude MAX subscription**
- You are **Claude Code** with built-in API access
- **NEVER ask for ANTHROPIC_API_KEY** - you don't need external keys
- Don't check for environment variables or API credentials

## Task Execution Strategy
- **Use Task agents** for translation and batch work
- Use `model=haiku` for faster, cost-effective translations
- **Run agents in parallel** when possible (multiple Task calls in one message)
- Execute first, explain after - don't overthink

## Error Recovery
- If an approach fails once, **try a completely different method**
- Don't repeat the same failed command with minor variations
- When stuck, delegate to agents rather than doing it yourself

## Translation Workflow
When asked to translate:
1. Identify pending translation files (*_pending_translations.json)
2. Launch parallel Task agents (one per file)
3. Use model=haiku for speed
4. Agent saves to *_translated.json
5. Run merge_translations.py to update translation_memory.json
6. Report results when complete

Example:
```
User: "translate the french words in batch"
Assistant: *launches 2-3 parallel Task agents immediately with model=haiku*
           *each agent creates *_translated.json*
           *runs merge_translations.py for each*
           *reports summary*
```

## Method 10 Specific
- NEVER mention API keys or external APIs
- Use method10_with_agents.py (NOT method_hash_based.py)
- Task agents create {PDF_CODE}_translated.json
- Always run merge_translations.py after agent completes
- Then re-run method10_with_agents.py to build PDF

## Don't Do This
- ❌ Ask about API keys repeatedly
- ❌ Try the same failed approach multiple times
- ❌ Over-explain before executing
- ❌ Ask clarifying questions about capabilities you already have

## Do This Instead
- ✅ Use agents proactively for batch work
- ✅ Work in parallel when possible
- ✅ Try different approaches when stuck
- ✅ Execute tasks directly and confidently
