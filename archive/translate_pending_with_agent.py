"""
Method 10 Helper: Translate pending items using Task agents
This script bridges Method 10 with Claude Code's Task agents
"""
import json
import sys

def prepare_pending_for_agent(pending_file):
    """Load pending file and prepare for agent translation"""
    with open(pending_file, 'r', encoding='utf-8') as f:
        pending = json.load(f)

    print(f"Loaded {len(pending)} items from {pending_file}")

    # Create a readable format for the agent
    # Convert {hash: french} to numbered list for easier processing
    readable = {}
    for i, (hash_key, french_text) in enumerate(pending.items()):
        readable[str(i)] = {
            "hash": hash_key,
            "french": french_text
        }

    # Save readable version
    readable_file = pending_file.replace('.json', '_readable.json')
    with open(readable_file, 'w', encoding='utf-8') as f:
        json.dump(readable, f, ensure_ascii=False, indent=2)

    print(f"Created readable format: {readable_file}")
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print(f"1. Use Task agent to translate: {readable_file}")
    print(f"2. Agent should output: {pending_file.replace('.json', '_translated.json')}")
    print(f"3. Run: python merge_translations.py {pending_file}")
    print("="*80)

    return readable_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python translate_pending_with_agent.py <pending_file>")
        print("\nExample:")
        print('  python translate_pending_with_agent.py A-001_pending_translations.json')
        sys.exit(1)

    prepare_pending_for_agent(sys.argv[1])
