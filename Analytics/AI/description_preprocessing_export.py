"""
Exports raw vs cleaned descriptions to a JSON file for offline review.
Run:  python -m Analytics.AI.description_preprocessing_export
Output: Analytics/AI/preprocessing_review.json
"""

import json
from pathlib import Path

from .description_preprocessing import clean_description_for_embedding

EXAMPLES_PATH = Path(__file__).parent / "description_examples.json"
OUTPUT_PATH   = Path(__file__).parent / "preprocessing_review.json"


def main():
    with open(EXAMPLES_PATH, encoding='utf-8') as f:
        examples = json.load(f)

    records = []
    for item in examples:
        title       = item.get('title', '').strip()
        description = item.get('description', '').strip()
        if not description:
            continue
        cleaned = clean_description_for_embedding(description, title)
        records.append({
            "title":   title,
            "raw":     description,
            "cleaned": cleaned,
        })

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"Exported {len(records)} records to {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
