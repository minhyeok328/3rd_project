from __future__ import annotations

import argparse
import html
import json
import os
import sys
import traceback
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


DEFAULT_GOLDSET_PATH = Path(__file__).with_name("llm_goldset.json")
DEFAULT_JSON_REPORT_PATH = Path(__file__).with_name("llm_eval_report.json")
DEFAULT_HTML_REPORT_PATH = Path(__file__).with_name("llm_eval_report.html")


def normalize_text(value: Any) -> str:
    return str(value or "").strip().lower()


def truncate_text(value: Any, limit: int = 70) -> str:
    text = str(value or "").replace("\n", " ").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def load_goldset(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as fp:
        data = json.load(fp)

    if not isinstance(data, list):
        raise ValueError("Goldset root must be a list.")

    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"Goldset item at index {index} must be an object.")
        if not item.get("case_id"):
            raise ValueError(f"Goldset item at index {index} is missing case_id.")
        if not item.get("question"):
            raise ValueError(f"Goldset item '{item.get('case_id', index)}' is missing question.")
        item.setdefault("query_type", item.get("expected_route", "unknown"))
        item.setdefault("source", "restaurant.db")

    return data


def build_preflight_status() -> dict[str, Any]:
    issues: list[str] = []
    checks: dict[str, Any] = {
        "openai_api_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "goldset_exists": DEFAULT_GOLDSET_PATH.exists(),
    }
    if not checks["openai_api_key_set"]:
        issues.append("OPENAI_API_KEY is not set.")
    return {"ok": len(issues) == 0, "checks": checks, "issues": issues}


def payload_check_result(case: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    checks = case.get("payload_checks", [])
    details: list[dict[str, Any]] = []

    for check in checks:
        keys = check.get("keys") or ([check["key"]] if "key" in check else [])
        expected_values = [normalize_text(v) for v in check.get("contains_any", []) if normalize_text(v)]
        matched_key = ""
        matched_value = ""
        passed = False

        for key in keys:
            actual_value = normalize_text(payload.get(key, ""))
            if any(expected in actual_value for expected in expected_values):
                matched_key = key
                matched_value = payload.get(key, "")
                passed = True
                break

        if not passed and keys:
            matched_key = keys[0]
            matched_value = payload.get(keys[0], "")

        details.append(
            {
                "keys": keys,
                "matched_key": matched_key,
                "actual": matched_value,
                "expected_contains_any": check.get("contains_any", []),
                "passed": passed,
            }
        )

    total = len(details)
    passed_count = sum(1 for item in details if item["passed"])
    score = passed_count / total if total else 1.0
    return {"score": score, "passed": passed_count == total, "details": details}


def answer_check_result(case: dict[str, Any], answer: str) -> dict[str, Any]:
    checks = case.get("answer_checks", {})
    normalized_answer = normalize_text(answer)
    must_include_any = [normalize_text(v) for v in checks.get("must_include_any", []) if normalize_text(v)]
    must_include_all = [normalize_text(v) for v in checks.get("must_include_all", []) if normalize_text(v)]
    must_not_include = [normalize_text(v) for v in checks.get("must_not_include", []) if normalize_text(v)]

    any_passed = True if not must_include_any else any(token in normalized_answer for token in must_include_any)
    all_passed = all(token in normalized_answer for token in must_include_all)
    none_passed = all(token not in normalized_answer for token in must_not_include)

    check_count = int(bool(must_include_any)) + int(bool(must_include_all)) + int(bool(must_not_include))
    passed_count = int(any_passed and bool(must_include_any)) + int(all_passed and bool(must_include_all)) + int(none_passed and bool(must_not_include))
    score = passed_count / check_count if check_count else 1.0
    return {
        "score": score,
        "passed": any_passed and all_passed and none_passed,
        "details": {
            "must_include_any_passed": any_passed,
            "must_include_all_passed": all_passed,
            "must_not_include_passed": none_passed,
        },
    }


def route_check_result(case: dict[str, Any], route: str) -> dict[str, Any]:
    expected_route = normalize_text(case.get("expected_route", ""))
    actual_route = normalize_text(route)
    passed = expected_route == actual_route if expected_route else True
    return {"score": 1.0 if passed else 0.0, "passed": passed, "expected": case.get("expected_route", ""), "actual": route}


def target_check_result(case: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    targets = case.get("expected_targets", {})
    expected_codes = set(targets.get("restaurant_codes", []))
    expected_names = {normalize_text(name) for name in targets.get("restaurant_names", []) if normalize_text(name)}

    candidate_lists = [result.get("used_restaurant_list", []) or [], result.get("restaurant_list", []) or []]
    seen_codes: set[str] = set()
    seen_names: set[str] = set()

    for collection in candidate_lists:
        for item in collection:
            if not isinstance(item, dict):
                continue
            code = item.get("restaurant_code")
            name = item.get("name")
            if code:
                seen_codes.add(code)
            if name:
                seen_names.add(normalize_text(name))

    code_hit = bool(expected_codes.intersection(seen_codes)) if expected_codes else True
    name_hit = bool(expected_names.intersection(seen_names)) if expected_names else True
    passed = code_hit and name_hit
    return {"score": 1.0 if passed else 0.0, "passed": passed, "expected_codes": sorted(expected_codes), "seen_codes": sorted(seen_codes)}


def retrieval_check_result(case: dict[str, Any], used_restaurants: list[dict[str, Any]]) -> dict[str, Any]:
    minimum = int(case.get("min_used_restaurants", 0))
    actual_count = len(used_restaurants or [])
    passed = actual_count >= minimum
    return {"score": 1.0 if passed else 0.0, "passed": passed, "expected_min": minimum, "actual_count": actual_count}


def aggregate_score(route_score: float, payload_score: float, target_score: float, answer_score: float, retrieval_score: float) -> float:
    return round((route_score * 0.30) + (payload_score * 0.25) + (target_score * 0.25) + (answer_score * 0.10) + (retrieval_score * 0.10), 4)


def explain_failure(case_result: dict[str, Any]) -> str:
    checks = case_result.get("checks", {})
    reasons: list[str] = []
    if not checks.get("route", {}).get("passed", False):
        reasons.append(f"route {checks['route'].get('expected', '?')} -> {checks['route'].get('actual', '?')}")
    if not checks.get("payload", {}).get("passed", False):
        payload_keys: list[str] = []
        for detail in checks.get("payload", {}).get("details", []):
            payload_keys.extend(detail.get("keys", []))
        reasons.append(f"payload miss: {', '.join(payload_keys) if payload_keys else 'payload'}")
    if not checks.get("target", {}).get("passed", False):
        reasons.append("target restaurant not retrieved")
    if not checks.get("answer", {}).get("passed", False):
        reasons.append("answer keyword mismatch")
    if not checks.get("retrieval", {}).get("passed", False):
        reasons.append("retrieval count low")
    if case_result.get("error"):
        reasons.append(case_result["error"]["type"])
    return "; ".join(reasons) if reasons else "-"


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    from src.pipeline import run_qa

    session_id = f"llm_eval::{case['case_id']}"
    result = run_qa(question=case["question"], session_id=session_id, stream=False)

    route_result = route_check_result(case, result.get("route", ""))
    payload_result = payload_check_result(case, result.get("route_payload", {}) or {})
    target_result = target_check_result(case, result)
    answer_result = answer_check_result(case, result.get("answer", ""))
    retrieval_result = retrieval_check_result(case, result.get("used_restaurant_list", []) or [])

    overall_score = aggregate_score(route_result["score"], payload_result["score"], target_result["score"], answer_result["score"], retrieval_result["score"])
    passed = all([route_result["passed"], payload_result["passed"], target_result["passed"], answer_result["passed"], retrieval_result["passed"]])

    case_result = {
        "case_id": case["case_id"],
        "query_type": case.get("query_type", "unknown"),
        "source": case.get("source", "restaurant.db"),
        "question": case["question"],
        "passed": passed,
        "overall_score": overall_score,
        "metadata": case.get("metadata", {}),
        "result": {
            "route": result.get("route", ""),
            "route_payload": result.get("route_payload", {}),
            "restaurant_list_count": len(result.get("restaurant_list", []) or []),
            "used_restaurant_count": len(result.get("used_restaurant_list", []) or []),
            "answer": result.get("answer", ""),
        },
        "checks": {
            "route": route_result,
            "payload": payload_result,
            "target": target_result,
            "answer": answer_result,
            "retrieval": retrieval_result,
        },
    }
    case_result["failure_reason"] = explain_failure(case_result)
    return case_result


def safe_case_failure(case: dict[str, Any], exc: Exception) -> dict[str, Any]:
    failed = {
        "case_id": case["case_id"],
        "query_type": case.get("query_type", "unknown"),
        "source": case.get("source", "restaurant.db"),
        "question": case["question"],
        "passed": False,
        "overall_score": 0.0,
        "metadata": case.get("metadata", {}),
        "error": {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()},
        "result": {"route": "", "route_payload": {}, "restaurant_list_count": 0, "used_restaurant_count": 0, "answer": ""},
        "checks": {
            "route": {"passed": False, "expected": case.get("expected_route", ""), "actual": ""},
            "payload": {"passed": False, "details": []},
            "target": {"passed": False, "expected_codes": case.get("expected_targets", {}).get("restaurant_codes", []), "seen_codes": []},
            "answer": {"passed": False},
            "retrieval": {"passed": False},
        },
    }
    failed["failure_reason"] = explain_failure(failed)
    return failed


def build_summary(case_results: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(case_results)
    passed = sum(1 for item in case_results if item.get("passed"))
    average_score = round(sum(item.get("overall_score", 0.0) for item in case_results) / total, 4) if total else 0.0

    component_accuracy = {}
    for component in ["route", "payload", "target", "answer", "retrieval"]:
        component_accuracy[component] = round(sum(1 for item in case_results if item.get("checks", {}).get(component, {}).get("passed")) / total, 4) if total else 0.0

    return {
        "total_cases": total,
        "passed_cases": passed,
        "failed_cases": total - passed,
        "pass_rate": round(passed / total, 4) if total else 0.0,
        "average_score": average_score,
        "component_accuracy": component_accuracy,
    }


def detect_environment_failure(case_results: list[dict[str, Any]]) -> dict[str, Any]:
    if not case_results:
        return {"is_environment_failure": False, "error_type": "", "count": 0}
    error_types = [item.get("error", {}).get("type", "") for item in case_results if item.get("error")]
    if len(error_types) != len(case_results):
        return {"is_environment_failure": False, "error_type": "", "count": len(error_types)}
    first_type = error_types[0] if error_types else ""
    all_same = all(err == first_type for err in error_types)
    is_env_failure = all_same and first_type in {"OpenAIError", "ValueError", "ImportError"}
    return {"is_environment_failure": is_env_failure, "error_type": first_type if all_same else "", "count": len(error_types)}


def build_group_summary(case_results: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in case_results:
        grouped[str(item.get(field, "unknown"))].append(item)

    rows: list[dict[str, Any]] = []
    for key, items in sorted(grouped.items()):
        total = len(items)
        passed = sum(1 for item in items if item.get("passed"))
        avg_score = round(sum(item.get("overall_score", 0.0) for item in items) / total, 4) if total else 0.0
        rows.append({field: key, "total": total, "passed": passed, "failed": total - passed, "pass_rate": round(passed / total, 4) if total else 0.0, "average_score": avg_score})
    return rows


def render_text_table(headers: list[str], rows: list[list[str]]) -> str:
    widths = [len(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(str(cell)))

    def render_row(values: list[str]) -> str:
        return "| " + " | ".join(str(value).ljust(widths[index]) for index, value in enumerate(values)) + " |"

    separator = "|-" + "-|-".join("-" * width for width in widths) + "-|"
    return "\n".join([render_row(headers), separator, *[render_row(row) for row in rows]])


def build_case_rows(cases: list[dict[str, Any]]) -> list[list[str]]:
    rows: list[list[str]] = []
    for item in cases:
        checks = item.get("checks", {})
        result = item.get("result", {})
        rows.append([
            "PASS" if item.get("passed") else "FAIL",
            item.get("case_id", ""),
            item.get("query_type", ""),
            f"{item.get('overall_score', 0.0):.2f}",
            checks.get("route", {}).get("actual", ""),
            "Y" if checks.get("payload", {}).get("passed") else "N",
            "Y" if checks.get("target", {}).get("passed") else "N",
            "Y" if checks.get("answer", {}).get("passed") else "N",
            "Y" if checks.get("retrieval", {}).get("passed") else "N",
            str(result.get("used_restaurant_count", 0)),
            truncate_text(item.get("failure_reason", "-"), 38),
            truncate_text(item.get("question", ""), 38),
        ])
    return rows


def print_console_report(report: dict[str, Any]) -> None:
    summary = report["summary"]
    print("=" * 112)
    print("LLM Evaluation Dashboard")
    print("=" * 112)

    preflight = report.get("preflight", {})
    if not preflight.get("ok", True):
        print("[Preflight Issues]")
        for issue in preflight.get("issues", []):
            print(f"- {issue}")
        print()

    env_failure = report.get("environment_failure", {})
    if env_failure.get("is_environment_failure"):
        print("[Environment Failure Detected]")
        print(f"All {env_failure.get('count', 0)} cases failed before evaluation due to {env_failure.get('error_type', 'unknown error')}.")
        print("This is not a model-quality result. Fix the runtime environment first, then rerun.")
        print()

    overview_rows = [
        ["cases", summary["total_cases"]],
        ["passed", summary["passed_cases"]],
        ["failed", summary["failed_cases"]],
        ["pass_rate", pct(summary["pass_rate"])],
        ["avg_score", f"{summary['average_score']:.2f}"],
        ["route_acc", pct(summary["component_accuracy"]["route"])],
        ["payload_acc", pct(summary["component_accuracy"]["payload"])],
        ["target_acc", pct(summary["component_accuracy"]["target"])],
        ["answer_acc", pct(summary["component_accuracy"]["answer"])],
        ["retrieval_acc", pct(summary["component_accuracy"]["retrieval"])],
    ]
    print(render_text_table(["metric", "value"], overview_rows))
    print()

    type_rows = [[row["query_type"], row["total"], row["passed"], row["failed"], pct(row["pass_rate"]), f"{row['average_score']:.2f}"] for row in report["type_summary"]]
    print("[By Query Type]")
    print(render_text_table(["type", "total", "passed", "failed", "pass_rate", "avg_score"], type_rows))
    print()

    failed_cases = [item for item in report["cases"] if not item.get("passed")]
    print(f"[Failed Cases] {len(failed_cases)}")
    if failed_cases:
        print(render_text_table(["status", "case_id", "type", "score", "route", "payload", "target", "answer", "retr", "used", "reason", "question"], build_case_rows(failed_cases)))
    else:
        print("All cases passed.")
    print()

    print("[Lowest Score Cases]")
    lowest_cases = sorted(report["cases"], key=lambda item: item.get("overall_score", 0.0))[:15]
    print(render_text_table(["status", "case_id", "type", "score", "route", "payload", "target", "answer", "retr", "used", "reason", "question"], build_case_rows(lowest_cases)))
    print("-" * 112)


def html_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{html.escape(str(header))}</th>" for header in headers)
    body_rows = ["<tr>" + "".join(f"<td>{html.escape(str(cell))}</td>" for cell in row) + "</tr>" for row in rows]
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def write_html_report(report: dict[str, Any], output_path: Path) -> None:
    summary = report["summary"]
    preflight = report.get("preflight", {})
    env_failure = report.get("environment_failure", {})
    overview_rows = [
        ["Cases", summary["total_cases"]],
        ["Passed", summary["passed_cases"]],
        ["Failed", summary["failed_cases"]],
        ["Pass Rate", pct(summary["pass_rate"])],
        ["Average Score", f"{summary['average_score']:.2f}"],
        ["Route Accuracy", pct(summary["component_accuracy"]["route"])],
        ["Payload Accuracy", pct(summary["component_accuracy"]["payload"])],
        ["Target Hit Accuracy", pct(summary["component_accuracy"]["target"])],
        ["Answer Accuracy", pct(summary["component_accuracy"]["answer"])],
        ["Retrieval Accuracy", pct(summary["component_accuracy"]["retrieval"])],
    ]
    type_rows = [[row["query_type"], row["total"], row["passed"], row["failed"], pct(row["pass_rate"]), f"{row['average_score']:.2f}"] for row in report["type_summary"]]
    failed_cases = [item for item in report["cases"] if not item.get("passed")]
    failed_table = html_table(["Status", "Case ID", "Type", "Score", "Route", "Payload", "Target", "Answer", "Retrieval", "Used", "Reason", "Question"], build_case_rows(failed_cases)) if failed_cases else "<p class='empty'>All cases passed.</p>"
    lowest_cases = sorted(report["cases"], key=lambda item: item.get("overall_score", 0.0))[:20]

    preflight_html = ""
    if not preflight.get("ok", True):
        preflight_html = "<section class='panel'><h2>Preflight Issues</h2>" + "".join(f"<p class='alert'>{html.escape(issue)}</p>" for issue in preflight.get("issues", [])) + "</section>"

    env_failure_html = ""
    if env_failure.get("is_environment_failure"):
        env_failure_html = (
            "<section class='panel'><h2>Environment Failure Detected</h2>"
            f"<p class='alert'>All {env_failure.get('count', 0)} cases failed before evaluation due to {html.escape(env_failure.get('error_type', 'unknown error'))}.</p>"
            "<p class='alert'>This is not a model-quality result. Fix the runtime environment first, then rerun.</p></section>"
        )

    html_body = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>LLM Evaluation Dashboard</title>
  <style>
    :root {{
      --bg: #f4efe8;
      --panel: #fffdfa;
      --line: #d9d0c2;
      --text: #1f2937;
      --muted: #6b7280;
      --good: #0f766e;
      --bad: #b91c1c;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      padding: 28px;
      background: radial-gradient(circle at top left, #efe6d8, #f8f5ef 50%, #fcfbf8 100%);
      color: var(--text);
      font-family: "Segoe UI", "Noto Sans KR", sans-serif;
    }}
    .wrap {{ max-width: 1600px; margin: 0 auto; }}
    h1 {{ margin: 0 0 10px; font-size: 34px; }}
    h2 {{ margin: 24px 0 12px; }}
    .meta {{ color: var(--muted); margin-bottom: 16px; }}
    .cards {{ display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; margin-bottom: 18px; }}
    .card, .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      box-shadow: 0 10px 24px rgba(0, 0, 0, 0.05);
    }}
    .card {{ padding: 16px; }}
    .panel {{ padding: 18px; margin-bottom: 18px; overflow-x: auto; }}
    .label {{ font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; }}
    .value {{ font-size: 28px; font-weight: 700; }}
    .value.good {{ color: var(--good); }}
    .value.bad {{ color: var(--bad); }}
    .grid-two {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
    table {{ width: 100%; border-collapse: collapse; min-width: 920px; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 10px 12px; text-align: left; vertical-align: top; font-size: 14px; }}
    th {{ background: #f1eadf; position: sticky; top: 0; }}
    .empty {{ color: var(--muted); }}
    .alert {{ color: var(--bad); font-weight: 600; }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>LLM Evaluation Dashboard</h1>
    <div class="meta">Generated: {html.escape(report["finished_at"])} | Goldset: {html.escape(report["goldset_path"])}</div>
    {preflight_html}
    {env_failure_html}
    <section class="cards">
      <div class="card"><div class="label">Cases</div><div class="value">{summary["total_cases"]}</div></div>
      <div class="card"><div class="label">Passed</div><div class="value good">{summary["passed_cases"]}</div></div>
      <div class="card"><div class="label">Failed</div><div class="value {'bad' if summary['failed_cases'] else 'good'}">{summary["failed_cases"]}</div></div>
      <div class="card"><div class="label">Pass Rate</div><div class="value">{pct(summary["pass_rate"])}</div></div>
      <div class="card"><div class="label">Average Score</div><div class="value">{summary["average_score"]:.2f}</div></div>
    </section>
    <div class="grid-two">
      <section class="panel"><h2>Overview</h2>{html_table(["Metric", "Value"], overview_rows)}</section>
      <section class="panel"><h2>By Query Type</h2>{html_table(["Type", "Total", "Passed", "Failed", "Pass Rate", "Avg Score"], type_rows)}</section>
    </div>
    <section class="panel"><h2>Failed Cases</h2>{failed_table}</section>
    <section class="panel"><h2>Lowest Score Cases</h2>{html_table(["Status", "Case ID", "Type", "Score", "Route", "Payload", "Target", "Answer", "Retrieval", "Used", "Reason", "Question"], build_case_rows(lowest_cases))}</section>
  </div>
</body>
</html>
"""
    output_path.write_text(html_body, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate the LLM pipeline with a goldset generated from restaurant.db.")
    parser.add_argument("--goldset", type=Path, default=DEFAULT_GOLDSET_PATH, help="Path to the goldset JSON file.")
    parser.add_argument("--output", type=Path, default=DEFAULT_JSON_REPORT_PATH, help="Path to write the JSON report.")
    parser.add_argument("--html-output", type=Path, default=DEFAULT_HTML_REPORT_PATH, help="Path to write the HTML report.")
    parser.add_argument("--case", action="append", default=[], help="Evaluate only the given case_id. Can be repeated.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    goldset = load_goldset(args.goldset)
    preflight = build_preflight_status()

    if args.case:
        requested = set(args.case)
        goldset = [item for item in goldset if item["case_id"] in requested]
    if not goldset:
        raise ValueError("No goldset cases selected.")

    case_results: list[dict[str, Any]] = []
    started_at = datetime.now().isoformat(timespec="seconds")
    for case in goldset:
        try:
            case_results.append(evaluate_case(case))
        except Exception as exc:
            case_results.append(safe_case_failure(case, exc))

    case_results.sort(key=lambda item: (item.get("passed", False), item.get("overall_score", 0.0), item.get("case_id", "")))
    report = {
        "started_at": started_at,
        "finished_at": datetime.now().isoformat(timespec="seconds"),
        "goldset_path": str(args.goldset.resolve()),
        "preflight": preflight,
        "summary": build_summary(case_results),
        "type_summary": build_group_summary(case_results, "query_type"),
        "environment_failure": detect_environment_failure(case_results),
        "cases": case_results,
    }

    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_html_report(report, args.html_output)
    print_console_report(report)
    print(f"json_report: {args.output.resolve()}")
    print(f"html_report: {args.html_output.resolve()}")
    return 0 if report["summary"]["failed_cases"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
