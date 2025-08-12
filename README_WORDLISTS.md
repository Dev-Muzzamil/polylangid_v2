# Single JSON Wordlist with Difficulty Tiers

The generator reads a single JSON file at:
`data/wordlists/words_by_difficulty.json`

Structure:
```json
{
  "en": {
    "easy":   ["... 20 words ..."],
    "medium": ["... 50 words ..."],
    "hard":   ["... 30 words ..."]
  },
  "ru": { "easy": [...], "medium": [...], "hard": [...] },
  "... other languages ..."
}
```

Generate 10k items:
```bash
python scripts/generate_multilingual_dataset.py \
  --num-sentences 10000 \
  --min-words 3 \
  --max-words 8 \
  --output dataset.jsonl \
  --format jsonl \
  --difficulty-weights "easy:0.2,medium:0.5,hard:0.3"
```

Notes
- The output JSON structure is: {"text": "...", "spans":[{"text":"...","lang":".."}, ...]}.
- Vietnamese and similar may include spaces per token; each is still one span.
- The script warns if any language deviates from 20/50/30 counts (warn-only).