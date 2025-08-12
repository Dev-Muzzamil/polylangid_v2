# Multilingual Dataset Generator

This repository contains a comprehensive multilingual dataset generator that creates mixed-language sentences with language annotations.

## Generated Dataset

### Dataset Characteristics
- **Total sentences**: 10,000
- **Total words/tokens**: 54,950
- **Languages**: 20 languages (English, Chinese, Hindi, Spanish, French, Arabic, Bengali, Portuguese, Russian, Urdu, Indonesian, German, Japanese, Turkish, Korean, Italian, Thai, Vietnamese, Polish, Dutch)
- **Words per sentence**: 3-8 words
- **Word difficulty**: Complex and difficult words across three difficulty levels (easy, medium, hard)

### Language Distribution
Each of the 20 languages is represented roughly equally (~5% each):
- Arabic (ar): 4.9%
- Bengali (bn): 5.0%
- German (de): 5.0%
- English (en): 5.0%
- Spanish (es): 5.2%
- French (fr): 5.0%
- Hindi (hi): 5.1%
- Indonesian (id): 5.0%
- Italian (it): 5.2%
- Japanese (ja): 5.0%
- Korean (ko): 5.1%
- Dutch (nl): 5.1%
- Polish (pl): 4.8%
- Portuguese (pt): 4.9%
- Russian (ru): 4.9%
- Thai (th): 5.1%
- Turkish (tr): 5.0%
- Urdu (ur): 5.0%
- Vietnamese (vi): 5.0%
- Chinese (zh): 4.8%

### Sentence Length Distribution
- 3 words: 17.0% (1,703 sentences)
- 4 words: 16.8% (1,678 sentences)
- 5 words: 16.2% (1,624 sentences)
- 6 words: 16.4% (1,643 sentences)
- 7 words: 16.7% (1,665 sentences)
- 8 words: 16.9% (1,687 sentences)

## Dataset Format

Each sentence is formatted as:

```json
{
  "text": "philosophy 哲学 سائنس philosophy विज्ञान",
  "spans": [
    {
      "text": "philosophy",
      "lang": "en"
    },
    {
      "text": "哲学",
      "lang": "zh"
    },
    {
      "text": "سائنس",
      "lang": "ur"
    },
    {
      "text": "philosophy",
      "lang": "en"
    },
    {
      "text": "विज्ञान",
      "lang": "hi"
    }
  ]
}
```

## Word Difficulty Levels

The vocabulary is organized into three difficulty levels for each language:

### Easy (20 words per language)
Basic complex words like "philosophy", "magnificent", "understanding"

### Medium (50 words per language)  
Sophisticated vocabulary like "perspicacious", "quintessential", "transcendental"

### Hard (30 words per language)
Very complex terms like "phantasmagorical", "epistemological", "psychoneuroimmunology"

## Usage

### Generate New Dataset

```bash
python scripts/generate_multilingual_dataset.py -n 10000 --format json -o multilingual_dataset.json
```

### Parameters

- `-n, --num-sentences`: Number of sentences to generate (default: 10000)
- `--min-words`: Minimum words per sentence (default: 3)
- `--max-words`: Maximum words per sentence (default: 8)
- `--format`: Output format - json or jsonl (default: jsonl)
- `--difficulty-weights`: Sampling weights like 'easy:0.1,medium:0.6,hard:0.3'
- `--seed`: Random seed for reproducibility (default: 42)

### Example Output

The generated dataset contains complex multilingual sentences like:

1. `"colectivo fascinating мудрость harmonioso ความไว้วางใจ आध्यात्मिक Nationalismus 时代精神"`
2. `"sublime تقليد uluslararası teknologi сознание"`
3. `"structurel tecnologico 스타일 pusillanimous सभ्यता มนุษยธรรม humanisme salud"`

## Files

- `multilingual_dataset_10k.json`: Main dataset with 10,000 sentences
- `data/wordlists/words_by_difficulty.json`: Vocabulary organized by language and difficulty
- `scripts/generate_multilingual_dataset.py`: Dataset generation script

## Applications

This dataset is ideal for:
- Multilingual language identification training
- Code-switching research
- Cross-lingual NLP model evaluation
- Language detection in mixed-language texts
- Multilingual text processing benchmarks