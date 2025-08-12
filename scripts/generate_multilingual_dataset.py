#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import random
from pathlib import Path
from typing import Dict, List, Any, Optional

LANG_CODES = [
    "en","zh","hi","es","fr","ar","bn","pt","ru","ur",
    "id","de","ja","tr","ko","it","th","vi","pl","nl"
]

DIFFICULTIES = ["easy", "medium", "hard"]

def parse_weights(spec: str) -> Dict[str, float]:
    # spec: "easy:0.2,medium:0.5,hard:0.3"
    parts = [p.strip() for p in spec.split(",") if p.strip()]
    weights: Dict[str, float] = {}
    for p in parts:
        if ":" not in p:
            raise ValueError(f"Invalid weight part: {p}")
        k, v = p.split(":", 1)
        k = k.strip().lower()
        if k not in DIFFICULTIES:
            raise ValueError(f"Unknown difficulty in weights: {k}")
        weights[k] = float(v)
    # normalize
    s = sum(weights.values())
    if s <= 0:
        raise ValueError("Sum of weights must be > 0")
    for k in list(weights.keys()):
        weights[k] /= s
    # fill missing with 0
    for d in DIFFICULTIES:
        weights.setdefault(d, 0.0)
    return weights

def load_words_json(path: Path) -> Dict[str, Dict[str, List[str]]]:
    # JSON structure:
    # {
    #   "en": { "easy":[...20...], "medium":[...50...], "hard":[...30...] },
    #   "ru": { "easy":[...], "medium":[...], "hard":[...] },
    #   ...
    # }
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Wordlist JSON must map language code to difficulty buckets.")
    out: Dict[str, Dict[str, List[str]]] = {l: {d: [] for d in DIFFICULTIES} for l in LANG_CODES}
    for lang, buckets in data.items():
        if not isinstance(buckets, dict):
            raise ValueError(f"Language '{lang}' must map to an object with easy/medium/hard arrays.")
        out.setdefault(lang, {d: [] for d in DIFFICULTIES})
        for d in DIFFICULTIES:
            arr = buckets.get(d, [])
            if not isinstance(arr, list):
                raise ValueError(f"{lang}/{d} must be a list.")
            # de-duplicate preserving order
            seen = set()
            uniq = []
            for w in arr:
                w = str(w)
                if w and (w not in seen):
                    uniq.append(w)
                    seen.add(w)
            out[lang][d] = uniq
    return out

def choose_difficulty(weights: Dict[str, float], available: Dict[str, List[str]]) -> str:
    diffs = [d for d in DIFFICULTIES if available.get(d)]
    if not diffs:
        return "medium"
    probs = [max(0.0, weights.get(d, 0.0)) for d in diffs]
    s = sum(probs)
    probs = [1.0 / len(diffs)] * len(diffs) if s <= 0 else [p / s for p in probs]
    r = random.random()
    cum = 0.0
    for d, p in zip(diffs, probs):
        cum += p
        if r <= cum:
            return d
    return diffs[-1]

def generate_item(
    langs: List[str],
    buckets: Dict[str, Dict[str, List[str]]],
    min_words: int,
    max_words: int,
    diff_weights: Dict[str, float]
) -> Dict[str, Any]:
    available_langs = [l for l in langs if any(buckets.get(l, {}).get(d) for d in DIFFICULTIES)]
    if not available_langs:
        raise ValueError("No available languages with words.")
    k = random.randint(min_words, max_words)
    k = min(k, len(available_langs))  # ensure unique langs per sentence
    chosen_langs = random.sample(available_langs, k)

    spans = []
    words = []
    for lang in chosen_langs:
        lang_buckets = buckets.get(lang, {})
        d = choose_difficulty(diff_weights, lang_buckets)
        candidates = lang_buckets.get(d, [])
        if not candidates:
            candidates = next((lang_buckets[x] for x in DIFFICULTIES if lang_buckets.get(x)), [])
        word = random.choice(candidates)
        spans.append({"text": word, "lang": lang})
        words.append(word)

    return {"text": " ".join(words), "spans": spans}

def generate_dataset(
    n: int,
    buckets: Dict[str, Dict[str, List[str]]],
    min_words: int = 3,
    max_words: int = 8,
    langs: Optional[List[str]] = None,
    seed: Optional[int] = None,
    diff_weights: Optional[Dict[str, float]] = None,
) -> List[Dict[str, Any]]:
    if seed is not None:
        random.seed(seed)
    langs = langs or LANG_CODES
    diff_weights = diff_weights or {"easy": 0.2, "medium": 0.5, "hard": 0.3}
    return [generate_item(langs, buckets, min_words, max_words, diff_weights) for _ in range(n)]

def write_jsonl(path: Path, items: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for obj in items:
            f.write(json.dumps(obj, ensure_ascii=False))
            f.write("\n")

def write_json_array(path: Path, items: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Generate a multilingual mixed-token dataset with spans and difficulty tiers.")
    parser.add_argument("-n", "--num-sentences", type=int, default=10000, help="Number of sentences to generate (default: 10000)")
    parser.add_argument("--min-words", type=int, default=3, help="Minimum tokens per sentence (default: 3)")
    parser.add_argument("--max-words", type=int, default=8, help="Maximum tokens per sentence (default: 8)")
    parser.add_argument("-o", "--output", type=Path, default=Path("dataset.jsonl"), help="Output file path (default: dataset.jsonl)")
    parser.add_argument("--format", choices=["jsonl", "json"], default="jsonl", help="Output format (default: jsonl)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility (default: 42)")

    # Single JSON wordlist
    parser.add_argument("--wordlist-json", type=Path, default=Path("data/wordlists/words_by_difficulty.json"),
                        help="Path to JSON with {lang:{easy:[20], medium:[50], hard:[30]}}")

    # Difficulty sampling weights
    parser.add_argument("--difficulty-weights", type=str, default="easy:0.2,medium:0.5,hard:0.3",
                        help="Sampling weights like 'easy:0.2,medium:0.5,hard:0.3'")

    args = parser.parse_args()

    buckets = load_words_json(args.wordlist_json)

    # Validation (warn-only)
    for l in LANG_CODES:
        total = sum(len(buckets.get(l, {}).get(d, [])) for d in DIFFICULTIES)
        if total == 0:
            print(f"Warning: No words found for language '{l}'.", flush=True)
        for d, target in {"easy": 20, "medium": 50, "hard": 30}.items():
            cnt = len(buckets.get(l, {}).get(d, []))
            if cnt != target:
                print(f"Warning: {l}/{d} has {cnt} words (expected {target}).", flush=True)

    diff_weights = parse_weights(args.difficulty_weights)

    items = generate_dataset(
        n=args.num_sentences,
        buckets=buckets,
        min_words=args.min_words,
        max_words=args.max_words,
        langs=LANG_CODES,
        seed=args.seed,
        diff_weights=diff_weights
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.format == "jsonl":
        write_jsonl(args.output, items)
    else:
        write_json_array(args.output, items)

    print(f"Done. Wrote {len(items)} items to {args.output} ({args.format}).")

if __name__ == "__main__":
    main()