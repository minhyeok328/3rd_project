"""Restaurant 후보 재랭킹(Retriever).

DB/커넥터가 넘겨준 restaurant_list 를 질문과의 키워드 매칭 기반으로
top-k 개로 간단히 다시 추린다. 벡터 재정렬이 붙기 전의 기본 리트리버.

─────────────────────────────────────────────────────────────────────────────
이 파일이 하는 일

    1) DB 에서 넘어온 식당 후보(dict 리스트)를 받는다.
    2) 사용자 질문(query) 속 단어들과, 각 식당 문서의 텍스트를 비교한다.
    3) 질문과 많이 겹치는 식당일수록 점수를 높게 주고, 정렬 후 상위 k개만 반환.
    4) 아무 것도 매칭되지 않으면(= 점수가 모두 0) 그냥 앞에서 k개를 잘라 반환한다.

    즉, 이 모듈은 "LLM 에 최종적으로 넘기기 전 1차 필터" 역할을 한다.

흐름상의 위치:
    pipeline.connector_search_node → restaurant_list 획득
    → generator.generate_response 안에서 simple_retrieve_restaurants() 호출
    → 추려진 후보만 system prompt 와 함께 LLM 에 전달
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations
from typing import Any


def simple_retrieve_restaurants(
    query: str,
    docs: list[dict[str, Any]],
    k: int = 3,
) -> list[dict[str, Any]]:
    """
    DB connector가 넘겨준 restaurant_list 안에서
    질문과의 단순 키워드 매칭 기반으로 top-k 후보를 다시 추린다.

    - query 토큰이 문서 전체 텍스트에 등장하면 가점
    - 문서 핵심 키워드(category/tags/menu/review tags)가 query에 부분문자열로 등장하면 큰 가점
    - 점수가 전부 0이면 앞에서 k개 fallback

    Args:
        query: 사용자 질문 원문 문자열
        docs : DB/커넥터가 전달해준 식당 정보 dict 들의 리스트
        k    : 최종적으로 선택하고 싶은 상위 후보 개수 (기본 3)

    Returns:
        list[dict[str, Any]]: 질문과 가장 관련 있는 상위 k개 식당 리스트

    전체 흐름 속 위치:
        generator.generate_response() 가 이 함수를 호출하여 후보를 좁힌 뒤
        그 결과를 LLM 에 전달해 최종 답변을 만든다.
    """
    # -----------------------------------------------------------------
    # 0) 문서가 비어 있으면 할 일이 없으므로 즉시 빈 리스트 반환.
    # -----------------------------------------------------------------
    if not docs:
        return []

    # -----------------------------------------------------------------
    # 1) 질문(query) 정규화
    #    - 소문자로 통일
    #    - 구두점 등 불필요한 기호를 공백으로 치환
    #    - 2글자 이상 단어만 토큰으로 추려서 유의미한 비교 대상으로 확보
    # -----------------------------------------------------------------
    q = (query or "").lower()
    for ch in [".", ",", "?", "!", "~", "'", '"']:
        q = q.replace(ch, " ")
    q_tokens = [t for t in q.split() if len(t) >= 2]

    # 각 문서에 대해 (점수, 문서) 튜플을 모아둘 버퍼.
    scored: list[tuple[int, dict[str, Any]]] = []

    # -----------------------------------------------------------------
    # 2) 모든 식당 문서를 순회하며 점수를 계산한다.
    # -----------------------------------------------------------------
    for r in docs:
        # 혹시라도 dict 가 아닌 이상한 값이 섞여 있으면 건너뜀 (안전장치).
        if not isinstance(r, dict):
            continue

        # ---------------------------------------------------
        # 2-1) 문서의 "핵심 키워드" 목록 구성
        #       category, tags, menu 이름, 리뷰의 tags 까지 끌어모아
        #       모두 소문자로 통일해둔다.
        # ---------------------------------------------------
        doc_keywords: list[str] = []
        doc_keywords += [str(c).lower() for c in r.get("category", []) if c]
        doc_keywords += [str(t).lower() for t in r.get("tags", []) if t]
        doc_keywords += [
            str(m.get("name", "")).lower()
            for m in r.get("menus", [])
            if isinstance(m, dict)
        ]

        # 리뷰들 각각의 tags 도 키워드로 편입.
        for rv in r.get("reviews", []):
            if isinstance(rv, dict):
                doc_keywords += [str(t).lower() for t in rv.get("tags", []) if t]

        # 길이 1 이하는 의미 없는 잡음이라 제거 (예: 단일 한 글자 등).
        doc_keywords = [kw for kw in doc_keywords if len(kw) >= 2]

        # ---------------------------------------------------
        # 2-2) 문서 전체 텍스트(merged) 조립
        #       이름/지역/주소/카테고리/태그/메뉴 설명/리뷰 본문을 한 덩어리로.
        #       이 merged 안에 query 토큰이 등장하면 "문서 안에서 발견된 것"
        #       으로 판단하여 가점한다.
        # ---------------------------------------------------
        text_fields = [
            str(r.get("name", "")),
            str(r.get("region", "")),
            str(r.get("address", "")),
            " ".join(map(str, r.get("category", []))),
            " ".join(map(str, r.get("tags", []))),
            " ".join(
                [
                    f"{m.get('name', '')} {m.get('description', '')}"
                    for m in r.get("menus", [])
                    if isinstance(m, dict)
                ]
            ),
            " ".join(
                [
                    str(rv.get("content", ""))
                    for rv in r.get("reviews", [])
                    if isinstance(rv, dict)
                ]
            ),
        ]
        merged = " ".join(text_fields).lower()

        # ---------------------------------------------------
        # 2-3) 점수 계산
        #       (a) 질문 토큰이 문서 본문 merged 에 포함되면 +2
        #       (b) 문서 키워드가 질문(q) 문자열 속 부분문자열로 등장하면 +3
        #           → "문서가 말하고 있는 개념을 질문에서 요구하고 있다"는 신호
        # ---------------------------------------------------
        score = 0

        for token in q_tokens:
            if token in merged:
                score += 2

        for kw in set(doc_keywords):
            if kw in q:
                score += 3

        # (점수, 해당 문서) 저장.
        scored.append((score, r))

    # -----------------------------------------------------------------
    # 3) 점수 내림차순 정렬 후 상위 k개 선택.
    #    단, 점수가 0 인 문서는 의미 없는 매칭이므로 제외.
    # -----------------------------------------------------------------
    scored.sort(key=lambda x: x[0], reverse=True)
    top_docs = [item[1] for item in scored[:k] if item[0] > 0]

    # -----------------------------------------------------------------
    # 4) fallback:
    #    아무 문서도 점수를 얻지 못했다면(= 매칭 실패)
    #    원본 docs 앞에서 k개를 잘라 그대로 반환해준다.
    #    → 완전히 빈 리스트가 내려가 LLM 이 답을 못 만드는 상황 방지.
    # -----------------------------------------------------------------
    return top_docs if top_docs else docs[:k]
