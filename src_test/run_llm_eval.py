from __future__ import annotations

import csv
import json
import os
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

from src.pipeline import run_qa
from src.router import decide_route
from src.slot_extractor import embedding_slot_extract, fixed_search


GOLDSET_PATH = BASE_DIR / "llm_goldset_50.json"


def extract_slots(question: str, route: str) -> dict[str, str]:
    if route == "fixed":
        return fixed_search.invoke(question)
    return embedding_slot_extract.invoke(question)


def normalize_restaurant_names(result: dict[str, Any]) -> list[str]:
    restaurants = result.get("used_restaurant_list", []) or []
    names: list[str] = []
    for item in restaurants:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if name and name not in names:
            names.append(name)
    return names


def compare_slots(expected: dict[str, str], actual: dict[str, str]) -> dict[str, Any]:
    keys = sorted(set(expected) | set(actual))
    per_key: dict[str, bool] = {}
    filled_expected = [k for k, v in expected.items() if str(v).strip()]
    filled_matches = 0

    for key in keys:
        exp = str(expected.get(key, "")).strip()
        got = str(actual.get(key, "")).strip()
        matched = exp == got
        per_key[key] = matched
        if key in filled_expected and matched:
            filled_matches += 1

    filled_total = len(filled_expected)
    return {
        "exact_match": all(per_key.values()) if per_key else True,
        "filled_key_accuracy": (filled_matches / filled_total) if filled_total else 1.0,
        "per_key": per_key,
    }


def compare_restaurants(
    expected_candidates: list[str],
    actual_candidates: list[str],
    expected_behavior: str,
    answer_text: str,
) -> dict[str, Any]:
    expected_set = set(expected_candidates)
    actual_set = set(actual_candidates)
    overlap = sorted(expected_set & actual_set)

    if expected_behavior == "no_match_or_low_confidence":
        no_candidates = len(actual_candidates) == 0
        cautious_answer = any(
            token in answer_text
            for token in ["없", "어렵", "확인되지", "찾지 못", "모르", "부족"]
        )
        passed = no_candidates or cautious_answer
        return {
            "passed": passed,
            "overlap": overlap,
            "actual_candidates": actual_candidates,
        }

    return {
        "passed": len(overlap) > 0,
        "overlap": overlap,
        "actual_candidates": actual_candidates,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return

    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8-sig", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set. Add it to .env before running this evaluator.")

    data = json.loads(GOLDSET_PATH.read_text(encoding="utf-8"))
    items = data["items"]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    detail_rows: list[dict[str, Any]] = []
    csv_rows: list[dict[str, Any]] = []
    route_counter: Counter[str] = Counter()
    route_pass = 0
    slot_pass = 0
    restaurant_pass = 0

    for item in items:
        question = item["question"]
        expected_route = item["expected_route"]
        expected_slots = item["expected_slots"]
        expected_candidates = item.get("expected_restaurant_candidates", [])
        expected_behavior = item.get("expected_behavior", "positive_match")

        actual_route = decide_route(question)
        actual_slots = extract_slots(question, actual_route)
        qa_result = run_qa(question=question, session_id=f"eval_{item['id']}")
        answer = str(qa_result.get("answer", ""))
        actual_candidates = normalize_restaurant_names(qa_result)

        slot_result = compare_slots(expected_slots, actual_slots)
        restaurant_result = compare_restaurants(
            expected_candidates=expected_candidates,
            actual_candidates=actual_candidates,
            expected_behavior=expected_behavior,
            answer_text=answer,
        )

        route_ok = actual_route == expected_route
        slot_ok = bool(slot_result["exact_match"])
        restaurant_ok = bool(restaurant_result["passed"])

        route_counter[actual_route] += 1
        route_pass += int(route_ok)
        slot_pass += int(slot_ok)
        restaurant_pass += int(restaurant_ok)

        row = {
            "id": item["id"],
            "question": question,
            "expected_route": expected_route,
            "actual_route": actual_route,
            "route_ok": route_ok,
            "expected_slots": expected_slots,
            "actual_slots": actual_slots,
            "slot_exact_ok": slot_ok,
            "slot_filled_key_accuracy": round(slot_result["filled_key_accuracy"], 4),
            "expected_candidates": expected_candidates,
            "actual_candidates": actual_candidates,
            "restaurant_ok": restaurant_ok,
            "restaurant_overlap": restaurant_result["overlap"],
            "expected_behavior": expected_behavior,
            "evaluation_focus": item.get("evaluation_focus", ""),
            "answer_preview": answer[:300],
        }
        detail_rows.append(row)

        csv_rows.append(
            {
                "id": item["id"],
                "question": question,
                "expected_route": expected_route,
                "actual_route": actual_route,
                "route_ok": route_ok,
                "slot_exact_ok": slot_ok,
                "slot_filled_key_accuracy": round(slot_result["filled_key_accuracy"], 4),
                "restaurant_ok": restaurant_ok,
                "expected_candidates": " | ".join(expected_candidates),
                "actual_candidates": " | ".join(actual_candidates),
                "restaurant_overlap": " | ".join(restaurant_result["overlap"]),
                "expected_behavior": expected_behavior,
            }
        )

    total = len(items)
    summary = {
        "dataset_name": data.get("dataset_name"),
        "dataset_version": data.get("dataset_version"),
        "ran_at": timestamp,
        "total_cases": total,
        "route_accuracy": round(route_pass / total, 4),
        "slot_exact_accuracy": round(slot_pass / total, 4),
        "restaurant_hit_accuracy": round(restaurant_pass / total, 4),
        "actual_route_distribution": dict(route_counter),
    }

    payload = {
        "summary": summary,
        "details": detail_rows,
    }

    detail_json_path = BASE_DIR / f"llm_eval_result_{timestamp}.json"
    detail_csv_path = BASE_DIR / f"llm_eval_result_{timestamp}.csv"
    latest_json_path = BASE_DIR / "llm_eval_result_latest.json"
    latest_csv_path = BASE_DIR / "llm_eval_result_latest.csv"

    write_json(detail_json_path, payload)
    write_json(latest_json_path, payload)
    write_csv(detail_csv_path, csv_rows)
    write_csv(latest_csv_path, csv_rows)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"wrote: {detail_json_path}")
    print(f"wrote: {detail_csv_path}")
    print(f"wrote: {latest_json_path}")
    print(f"wrote: {latest_csv_path}")


if __name__ == "__main__":
    main()
