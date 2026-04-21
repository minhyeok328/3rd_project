# src/generate.py
from __future__ import annotations

import json
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from .config import SETTINGS

_SESSION_MESSAGES: dict[str, list[BaseMessage]] = {}


def load_prompt_template() -> str:
    if not SETTINGS.prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {SETTINGS.prompt_path}")
    return SETTINGS.prompt_path.read_text(encoding="utf-8")


def clear_session(session_id: str) -> None:
    _SESSION_MESSAGES.pop(session_id, None)


def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=SETTINGS.llm_model,
        temperature=0,
        api_key=SETTINGS.openai_api_key,
    )


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
    """
    if not docs:
        return []

    q = (query or "").lower()
    for ch in [".", ",", "?", "!", "~", "'", '"']:
        q = q.replace(ch, " ")
    q_tokens = [t for t in q.split() if len(t) >= 2]

    scored: list[tuple[int, dict[str, Any]]] = []

    for r in docs:
        if not isinstance(r, dict):
            continue

        doc_keywords: list[str] = []
        doc_keywords += [str(c).lower() for c in r.get("category", []) if c]
        doc_keywords += [str(t).lower() for t in r.get("tags", []) if t]
        doc_keywords += [
            str(m.get("name", "")).lower()
            for m in r.get("menus", [])
            if isinstance(m, dict)
        ]

        for rv in r.get("reviews", []):
            if isinstance(rv, dict):
                doc_keywords += [str(t).lower() for t in rv.get("tags", []) if t]

        doc_keywords = [kw for kw in doc_keywords if len(kw) >= 2]

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

        score = 0

        # 1) query 토큰이 문서 전체 텍스트에 등장하면 가점
        for token in q_tokens:
            if token in merged:
                score += 2

        # 2) 문서 핵심 키워드가 query 원문에 부분문자열로 등장하면 큰 가점
        for kw in set(doc_keywords):
            if kw in q:
                score += 3

        scored.append((score, r))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_docs = [item[1] for item in scored[:k] if item[0] > 0]

    return top_docs if top_docs else docs[:k]


def generate_response(
    question: str,
    restaurant_list: list[dict[str, Any]],
    route: str,
    session_id: str = "default",
    route_payload: dict[str, Any] | None = None,
    connector_meta: dict[str, Any] | None = None,
) -> str:
    prompt_rules = load_prompt_template()
    history = _SESSION_MESSAGES.setdefault(session_id, [])

    route_payload = route_payload or {}
    connector_meta = connector_meta or {}

    retrieved_restaurants = simple_retrieve_restaurants(
        query=question,
        docs=restaurant_list,
        k=SETTINGS.top_k,
    )

    system_prompt = f"""
{prompt_rules}

[Search Route]
{route}

[Search Payload]
{json.dumps(route_payload, ensure_ascii=False, indent=2)}

[Connector Meta]
{json.dumps(connector_meta, ensure_ascii=False, indent=2)}
""".strip()

    rag_input = {
        "question": question,
        "restaurant_list": retrieved_restaurants,
    }

    messages: list[BaseMessage] = [
        SystemMessage(content=system_prompt),
        *history,
        HumanMessage(content=json.dumps(rag_input, ensure_ascii=False, indent=2)),
    ]

    llm = get_llm()
    result = llm.invoke(messages)
    response = result.content if hasattr(result, "content") else str(result)

    history.append(HumanMessage(content=question))
    history.append(AIMessage(content=response))

    return response