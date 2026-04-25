from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


SRC_TEST_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_TEST_DIR.parent
DB_PATH = PROJECT_ROOT / "database" / "sql" / "restaurant.db"
OUTPUT_PATH = SRC_TEST_DIR / "llm_goldset.json"


PREFERRED_TAGS = [
    "혼밥",
    "데이트",
    "가족외식",
    "가성비좋은",
    "매콤한",
    "해장",
    "술모임",
    "카공",
    "혼자카페",
    "야식",
    "간식",
    "무료주차",
    "예약가능",
    "분위기좋은",
    "서민적인",
    "깔끔한",
    "점심식사",
    "저녁식사",
    "배달",
    "테이크아웃",
    "식사모임",
    "단체모임",
    "회식",
    "기념일",
    "낮술",
    "캐주얼한",
    "한가한",
    "넓은",
]


def fetch_all_restaurants() -> list[dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    restaurants = cur.execute(
        """
        SELECT restaurant_code, name, address, open_time, close_time, tel_no
        FROM restaurant
        ORDER BY restaurant_code
        """
    ).fetchall()

    results: list[dict[str, Any]] = []
    for row in restaurants:
        code = row["restaurant_code"]
        categories = [
            item[0]
            for item in cur.execute(
                """
                SELECT c.name
                FROM rel_restaurant_category rel
                JOIN category c ON c.category_code = rel.category_code
                WHERE rel.restaurant_code = ?
                ORDER BY c.name
                """,
                (code,),
            ).fetchall()
        ]
        tags = [
            item[0]
            for item in cur.execute(
                """
                SELECT t.name
                FROM rel_restaurant_tag rel
                JOIN tag t ON t.tag_code = rel.tag_code
                WHERE rel.restaurant_code = ?
                ORDER BY t.name
                """,
                (code,),
            ).fetchall()
        ]
        menus = [
            {"name": item[0], "price": item[1]}
            for item in cur.execute(
                """
                SELECT name, price
                FROM menu
                WHERE restaurant_code = ?
                ORDER BY menu_code
                """,
                (code,),
            ).fetchall()
        ]

        results.append(
            {
                "restaurant_code": code,
                "name": row["name"],
                "address": row["address"],
                "open_time": row["open_time"],
                "close_time": row["close_time"],
                "tel_no": row["tel_no"],
                "categories": categories,
                "tags": tags,
                "menus": menus,
            }
        )

    conn.close()
    return results


def choose_tag(tags: list[str]) -> str | None:
    tag_set = set(tags)
    for tag in PREFERRED_TAGS:
        if tag in tag_set:
            return tag
    return tags[0] if tags else None


def clean_menu_keyword(menu_name: str) -> str:
    text = menu_name.strip()
    if "(" in text:
        text = text.split("(", 1)[0].strip()
    for suffix in [" 소", " 중", " 대", " 1호", " 2호", " 3호"]:
        if text.endswith(suffix):
            text = text[: -len(suffix)].strip()
    return text or menu_name.strip()


def make_tag_question(tag: str, category: str) -> str:
    template_map = {
        "혼밥": "혼밥하기 좋은 {category} 맛집 추천해줘",
        "데이트": "데이트하기 좋은 {category} 맛집 추천해줘",
        "가족외식": "가족외식하기 좋은 {category} 맛집 추천해줘",
        "가성비좋은": "가성비 좋은 {category} 맛집 추천해줘",
        "매콤한": "매콤한 {category} 맛집 추천해줘",
        "해장": "해장하기 좋은 {category} 맛집 추천해줘",
        "술모임": "술모임하기 좋은 {category} 맛집 추천해줘",
        "카공": "카공하기 좋은 {category} 추천해줘",
        "혼자카페": "혼자 가기 좋은 {category} 추천해줘",
        "야식": "야식으로 좋은 {category} 맛집 추천해줘",
        "간식": "간식 먹기 좋은 {category} 추천해줘",
        "무료주차": "무료주차 가능한 {category} 맛집 추천해줘",
        "예약가능": "예약 가능한 {category} 맛집 추천해줘",
        "분위기좋은": "분위기 좋은 {category} 맛집 추천해줘",
        "서민적인": "서민적인 {category} 맛집 추천해줘",
        "깔끔한": "깔끔한 {category} 맛집 추천해줘",
        "점심식사": "점심에 가기 좋은 {category} 맛집 추천해줘",
        "저녁식사": "저녁에 가기 좋은 {category} 맛집 추천해줘",
        "배달": "배달 되는 {category} 맛집 추천해줘",
        "테이크아웃": "테이크아웃 가능한 {category} 추천해줘",
        "식사모임": "식사모임하기 좋은 {category} 맛집 추천해줘",
        "단체모임": "단체모임하기 좋은 {category} 맛집 추천해줘",
        "회식": "회식하기 좋은 {category} 맛집 추천해줘",
        "기념일": "기념일에 가기 좋은 {category} 추천해줘",
        "낮술": "낮술하기 좋은 {category} 추천해줘",
        "캐주얼한": "캐주얼한 분위기의 {category} 맛집 추천해줘",
        "한가한": "한가한 분위기의 {category} 맛집 추천해줘",
        "넓은": "넓은 {category} 맛집 추천해줘",
    }
    return template_map.get(tag, "{tag}에 어울리는 {category} 맛집 추천해줘").format(tag=tag, category=category)


def build_fixed_cases(restaurants: list[dict[str, Any]], restaurant_count: int = 10) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    selected = [item for item in restaurants if item["menus"]][:restaurant_count]
    for index, item in enumerate(selected, start=1):
        menu_keyword = clean_menu_keyword(item["menus"][0]["name"])

        cases.append(
            {
                "case_id": f"fixed_{index:03d}_hours",
                "source": "restaurant.db",
                "query_type": "fixed",
                "question": f"{item['name']} 영업시간 알려줘",
                "expected_route": "fixed",
                "payload_checks": [{"keys": ["restaurant"], "contains_any": [item["name"]]}],
                "expected_targets": {
                    "restaurant_codes": [item["restaurant_code"]],
                    "restaurant_names": [item["name"]],
                },
                "answer_checks": {
                    "must_include_any": [item["name"], "영업", "시간"],
                    "must_include_all": [],
                    "must_not_include": [],
                },
                "min_used_restaurants": 1,
                "metadata": {
                    "restaurant_code": item["restaurant_code"],
                    "restaurant_name": item["name"],
                    "menu_keyword": menu_keyword,
                },
            }
        )

        cases.append(
            {
                "case_id": f"fixed_{index:03d}_menu",
                "source": "restaurant.db",
                "query_type": "fixed",
                "question": f"{item['name']}에 {menu_keyword} 있어?",
                "expected_route": "fixed",
                "payload_checks": [
                    {"keys": ["restaurant"], "contains_any": [item["name"]]},
                    {"keys": ["menu"], "contains_any": [menu_keyword]},
                ],
                "expected_targets": {
                    "restaurant_codes": [item["restaurant_code"]],
                    "restaurant_names": [item["name"]],
                },
                "answer_checks": {
                    "must_include_any": [item["name"], menu_keyword],
                    "must_include_all": [],
                    "must_not_include": [],
                },
                "min_used_restaurants": 1,
                "metadata": {
                    "restaurant_code": item["restaurant_code"],
                    "restaurant_name": item["name"],
                    "menu_keyword": menu_keyword,
                },
            }
        )

    return cases


def build_embedding_cases(restaurants: list[dict[str, Any]], limit: int = 30) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    for item in restaurants:
        if len(cases) >= limit:
            break
        if not item["categories"] or not item["tags"]:
            continue

        category = item["categories"][0]
        tag = choose_tag(item["tags"])
        if not tag:
            continue

        cases.append(
            {
                "case_id": f"embedding_{len(cases) + 1:03d}",
                "source": "restaurant.db",
                "query_type": "embedding",
                "question": make_tag_question(tag, category),
                "expected_route": "embedding",
                "payload_checks": [
                    {"keys": ["category", "food", "menu"], "contains_any": [category]},
                    {"keys": ["tag", "review"], "contains_any": [tag]},
                ],
                "expected_targets": {
                    "restaurant_codes": [item["restaurant_code"]],
                    "restaurant_names": [item["name"]],
                },
                "answer_checks": {
                    "must_include_any": ["추천", item["name"], category],
                    "must_include_all": [],
                    "must_not_include": [],
                },
                "min_used_restaurants": 1,
                "metadata": {
                    "restaurant_code": item["restaurant_code"],
                    "restaurant_name": item["name"],
                    "category": category,
                    "tag": tag,
                },
            }
        )

    return cases


def main() -> None:
    restaurants = fetch_all_restaurants()
    fixed_cases = build_fixed_cases(restaurants, restaurant_count=10)
    embedding_cases = build_embedding_cases(restaurants, limit=30)
    goldset = fixed_cases + embedding_cases

    if len(goldset) != 50:
        raise ValueError(f"Expected 50 cases, got {len(goldset)}")

    OUTPUT_PATH.write_text(json.dumps(goldset, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"goldset_written: {OUTPUT_PATH}")
    print(f"total_cases: {len(goldset)}")
    print(f"fixed_cases: {len(fixed_cases)}")
    print(f"embedding_cases: {len(embedding_cases)}")


if __name__ == "__main__":
    main()
