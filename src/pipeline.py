# src/pipeline.py
from __future__ import annotations

from typing import Any, Literal, TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from .config import SETTINGS
from .embedding_tool import embedding_slot_extract
from .generate import generate_response
from .llm_tool2 import fixed_search


class GraphState(TypedDict, total=False):
    question: str
    session_id: str

    # ============================================================
    # [커넥터 반환 데이터가 들어오는 자리]
    # main.py 또는 외부 호출부에서 아래 형태로 넘겨준다고 가정
    #
    # {
    #     "restaurant_list": [...],
    #     "search_mode": "...",
    #     "candidate_count": ...
    # }
    # ============================================================
    connector_response: dict[str, Any]

    route: Literal["embedding", "fixed"]
    route_payload: dict[str, str]

    restaurant_list: list[dict[str, Any]]
    answer: str


_graph = None


def decide_route(question: str) -> str:
    router_prompt = """
너는 식당 검색 라우터다.
사용자 질문을 보고 반드시 아래 둘 중 하나만 반환해.

- embedding
- fixed

판단 기준:
1) 분위기, 상황, 취향, 특징, 평가, 조합 조건 중심이면 embedding
2) 특정 식당명, 특정 메뉴명, 특정 유저/리뷰어, 명시적 엔티티 검색이면 fixed
3) 지역명이 들어가더라도 핵심이 조건 기반 탐색이면 embedding
4) 애매하면 embedding

반드시 embedding 또는 fixed 중 하나의 단어만 출력해.

사용자 질문:
{question}
""".strip()

    llm = ChatOpenAI(
        model=SETTINGS.router_model,
        temperature=0,
        api_key=SETTINGS.openai_api_key,
    )

    raw = llm.invoke(router_prompt.replace("{question}", question)).content.strip().lower()
    if "fixed" in raw:
        return "fixed"
    return "embedding"


def _normalize_connector_response(result: Any) -> dict[str, Any]:
    if result is None:
        return {"restaurant_list": []}

    if isinstance(result, dict):
        restaurant_list = result.get("restaurant_list", [])
        if restaurant_list is None:
            restaurant_list = []

        if not isinstance(restaurant_list, list):
            raise ValueError("connector_response['restaurant_list']는 list 형태여야 합니다.")

        return {
            **result,
            "restaurant_list": restaurant_list,
        }

    if isinstance(result, list):
        return {"restaurant_list": result}

    raise ValueError("connector_response는 dict 또는 list 형태여야 합니다.")


def route_node(state: GraphState) -> GraphState:
    return {"route": decide_route(state["question"])}


def embedding_slot_node(state: GraphState) -> GraphState:
    payload = embedding_slot_extract.invoke(state["question"])
    return {"route_payload": payload}


def fixed_slot_node(state: GraphState) -> GraphState:
    payload = fixed_search.invoke(state["question"])
    return {"route_payload": payload}


def connector_prepare_node(state: GraphState) -> GraphState:
    # ============================================================
    # [커넥터 반환 데이터 받아오는 곳]
    # 외부(main.py 등)에서 전달받은 connector_response를 여기서 정규화함
    # ============================================================
    connector_response = _normalize_connector_response(state.get("connector_response"))

    # ============================================================
    # [커넥터 데이터에서 restaurant_list 추출하는 곳]
    # 이후 generate_response에 들어갈 핵심 데이터
    # ============================================================
    restaurant_list = connector_response.get("restaurant_list", [])

    return {
        "connector_response": connector_response,
        "restaurant_list": restaurant_list,
    }


def generate_node(state: GraphState) -> GraphState:
    question = state["question"]
    session_id = state.get("session_id", "default")
    route = state.get("route", "embedding")
    route_payload = state.get("route_payload", {})
    restaurant_list = state.get("restaurant_list", [])
    connector_response = state.get("connector_response", {})

    connector_meta = {
        k: v
        for k, v in connector_response.items()
        if k != "restaurant_list"
    }
    connector_meta["restaurant_count"] = len(restaurant_list)

    answer = generate_response(
        question=question,
        restaurant_list=restaurant_list,
        route=route,
        session_id=session_id,
        route_payload=route_payload,
        connector_meta=connector_meta,
    )
    return {"answer": answer}


def route_condition(state: GraphState) -> str:
    return state["route"]


def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("route_node", route_node)
    graph.add_node("embedding_slot_node", embedding_slot_node)
    graph.add_node("fixed_slot_node", fixed_slot_node)
    graph.add_node("connector_prepare_node", connector_prepare_node)
    graph.add_node("generate_node", generate_node)

    graph.add_edge(START, "route_node")

    graph.add_conditional_edges(
        "route_node",
        route_condition,
        {
            "embedding": "embedding_slot_node",
            "fixed": "fixed_slot_node",
        },
    )

    graph.add_edge("embedding_slot_node", "connector_prepare_node")
    graph.add_edge("fixed_slot_node", "connector_prepare_node")

    graph.add_edge("connector_prepare_node", "generate_node")
    graph.add_edge("generate_node", END)

    return graph.compile()


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


def run_qa(
    question: str,
    connector_response: dict[str, Any] | list[dict[str, Any]],
    session_id: str = "default",
) -> dict[str, Any]:
    graph = get_graph()

    # ============================================================
    # [외부에서 커넥터 반환 데이터를 주입하는 곳]
    # main.py가 connector_response를 넘겨주면 여기서 그래프에 넣음
    # ============================================================
    result = graph.invoke(
        {
            "question": question,
            "session_id": session_id,
            "connector_response": connector_response,
        }
    )

    return {
        "question": question,
        "route": result.get("route"),
        "route_payload": result.get("route_payload", {}),
        "connector_response": result.get("connector_response", {}),
        "restaurant_list": result.get("restaurant_list", []),
        "answer": result.get("answer", ""),
    }