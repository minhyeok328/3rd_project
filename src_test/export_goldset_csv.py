from __future__ import annotations

import csv
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
JSON_PATH = BASE_DIR / "llm_goldset_50.json"
CSV_PATH = BASE_DIR / "llm_goldset_50.csv"


def main() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    items = data["items"]

    fieldnames = [
        "id",
        "question",
        "expected_route",
        "expected_category",
        "expected_tag",
        "expected_menu",
        "expected_food",
        "expected_review",
        "expected_restaurant",
        "expected_user",
        "expected_restaurant_candidates",
        "expected_behavior",
        "evaluation_focus",
    ]

    with CSV_PATH.open("w", encoding="utf-8-sig", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()

        for item in items:
            slots = item.get("expected_slots", {})
            writer.writerow(
                {
                    "id": item["id"],
                    "question": item["question"],
                    "expected_route": item["expected_route"],
                    "expected_category": slots.get("category", ""),
                    "expected_tag": slots.get("tag", ""),
                    "expected_menu": slots.get("menu", ""),
                    "expected_food": slots.get("food", ""),
                    "expected_review": slots.get("review", ""),
                    "expected_restaurant": slots.get("restaurant", ""),
                    "expected_user": slots.get("user", ""),
                    "expected_restaurant_candidates": " | ".join(
                        item.get("expected_restaurant_candidates", [])
                    ),
                    "expected_behavior": item.get("expected_behavior", ""),
                    "evaluation_focus": item.get("evaluation_focus", ""),
                }
            )

    print(f"wrote: {CSV_PATH}")


if __name__ == "__main__":
    main()
