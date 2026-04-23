"""질의응답 파이프라인(LangGraph) + CLI 진입점.

- `run_qa(question, session_id)` : 외부 호출용 API
- `python -m src.pipeline`       : 터미널에서 대화 테스트

─────────────────────────────────────────────────────────────────────────────
이 파일이 하는 일

    이 프로젝트의 "메인 파이프라인" 이다.
    사용자의 질문이 들어오면 아래 순서로 여러 단계를 자동 실행한다:

        [사용자 질문]
              │
              ▼
        route_node          ← "embedding 이냐 fixed 이냐" 결정 (router.decide_route)
              │
        ┌─────┴──────┐
        ▼            ▼
  embedding_slot_node   fixed_slot_node    ← 질문을 slot(JSON) 으로 쪼갬
        │            │
        └─────┬──────┘
              ▼
      connector_search_node   ← 슬롯 기반으로 DB 조회 (db_embedding_search / db_fixed_search)
              │
              ▼
        generate_node         ← LLM 에게 최종 답변 생성 시키기 (generator.generate_response)
              │
              ▼
           [answer]

    이 흐름은 LangGraph 의 StateGraph 로 구성되어 있다.
    StateGraph 란 노드들이 상태(state) 를 주고받으며 연결되는 그래프.

공개 함수:
    - run_qa(question, session_id): 그래프를 한 번 실행해 결과 dict 반환.
    - main():                       터미널 대화형 테스트 루프.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations
from typing import Any, Literal, TypedDict
from langgraph.graph import END, START, StateGraph
from .generator import generate_response
from database.sql.utils import db_fixed_search, db_embedding_search
from .router import decide_route
from .slot_extractor import embedding_slot_extract, fixed_search


class GraphState(TypedDict, total=False):
    """
    LangGraph 노드들 사이에서 공유되는 "상태(state)" 의 스키마.

    각 노드는 이 TypedDict 형태의 dict 를 입력받아
    자신이 책임지는 필드만 채운 partial dict 를 반환한다.
    LangGraph 가 그 반환값을 기존 state 에 병합(merge)해 준다.

    필드 설명:
        question:             사용자 원문 질문 (시작 시점에 채워짐)
        session_id:           멀티턴 대화 히스토리 구분용 ID

        route:                "embedding" 또는 "fixed" 로 분기 결정
        route_payload:        slot_extractor 가 뽑은 슬롯 dict

        restaurant_list:      DB 가 돌려준 원본 식당 후보 리스트
        used_restaurant_list: 실제 LLM 에 전달된 최종 식당 리스트
        answer:               LLM 이 생성한 최종 답변 문자열

    total=False 로 선언했기 때문에 모든 필드를 반드시 채울 필요는 없고,
    각 노드가 "자기가 만들어내는 필드만" 쓰면 된다.
    """

    question: str
    session_id: str

    route: Literal["embedding", "fixed"]
    route_payload: dict[str, str]

    restaurant_list: list[dict[str, Any]]
    used_restaurant_list: list[dict[str, Any]]
    answer: str


# ---------------------------------------------------------------------------
# 컴파일된 LangGraph 를 캐싱해 두는 전역 변수.
#   - build_graph() 의 결과물을 최초 1회만 생성 후 재사용.
#   - 매 요청마다 그래프를 새로 빌드하면 비용 낭비.
# ---------------------------------------------------------------------------
_graph = None


def _normalize_restaurant_list(result: Any) -> list[dict[str, Any]]:
    """
    DB 커넥터가 돌려준 값을 "순수한 list[dict]" 형태로 정규화한다.

    커넥터는 상황에 따라 아래 중 하나를 반환할 수 있어 처리 방식을 통일시키는 역할:
        1) list                  → 그대로 사용
        2) {"restaurant_list": [...]} → 안쪽 리스트만 꺼내 사용
        3) None                  → 빈 리스트로 치환
        4) 그 외                 → 에러

    Args:
        result: 커넥터 반환값 (list | dict | None | 기타)

    Returns:
        list[dict[str, Any]]: 정규화된 식당 리스트

    Raises:
        ValueError: 예상하지 못한 포맷이 들어왔을 때.

    전체 흐름 속 위치:
        connector_search_node 에서 DB 조회 후 호출해,
        이후 단계에서 안전하게 리스트로 취급할 수 있도록 형태를 맞춘다.
    """
    # 1) None 이면 빈 리스트.
    if result is None:
        return []

    # 2) 이미 list 면 그대로 반환.
    if isinstance(result, list):
        return result

    # 3) dict 인 경우 "restaurant_list" 키 확인.
    if isinstance(result, dict):
        restaurant_list = result.get("restaurant_list", [])
        if restaurant_list is None:
            return []
        if not isinstance(restaurant_list, list):
            raise ValueError("connector_response['restaurant_list']는 list 형태여야 합니다.")
        return restaurant_list

    # 4) 위 세 가지 외의 타입은 규격 위반이므로 에러.
    raise ValueError("connector/utils 반환값은 list 또는 {'restaurant_list': list} 형태여야 합니다.")


# ===========================================================================
# 이하 *_node 함수들: LangGraph 의 각 노드에 대응하는 실행 함수.
#   - 입력:  GraphState (현재까지의 전체 state)
#   - 출력:  GraphState 의 일부 필드만 채운 partial dict
#   - 반환값이 자동으로 state 에 병합된다.
# ===========================================================================

def route_node(state: GraphState) -> GraphState:
    """
    [첫 단계] 질문을 보고 embedding / fixed 중 어디로 보낼지 결정하는 노드.

    state["question"] 을 router.decide_route 에 넘겨
    "embedding" 또는 "fixed" 문자열을 받아 state["route"] 에 저장한다.

    전체 흐름 속 위치: START → route_node → (조건 분기)
    """
    return {"route": decide_route(state["question"])}


def embedding_slot_node(state: GraphState) -> GraphState:
    """
    embedding 경로일 때 슬롯 추출을 수행하는 노드.

    embedding_slot_extract @tool 을 호출하여
    {category, tag, menu, food, review} 딕셔너리를 만들고,
    state["route_payload"] 에 저장한다.
    """
    # @tool 데코레이터로 감싼 함수는 .invoke(...) 로 호출한다.
    payload = embedding_slot_extract.invoke(state["question"])
    return {"route_payload": payload}


def fixed_slot_node(state: GraphState) -> GraphState:
    """
    fixed 경로일 때 슬롯 추출을 수행하는 노드.

    fixed_search @tool 을 호출하여 {restaurant, menu, user} 딕셔너리를 만들고
    state["route_payload"] 에 저장한다.
    """
    payload = fixed_search.invoke(state["question"])
    return {"route_payload": payload}


def connector_search_node(state: GraphState) -> GraphState:
    """
    슬롯(route_payload) 을 이용해 DB 에서 실제 식당 후보를 가져오는 노드.

    - route == "embedding" → db_embedding_search
    - route == "fixed"     → db_fixed_search

    이후 결과는 _normalize_restaurant_list 로 list[dict] 형태로 정규화한 뒤
    state["restaurant_list"] 에 담긴다.

    전체 흐름 속 위치:
        슬롯 추출 노드들 이후, generate_node 이전의 "데이터 조회" 단계.
    """
    # 현재 어떤 경로로 왔는지, 슬롯이 어떤 값인지 꺼낸다.
    route = state["route"]
    route_payload = state.get("route_payload", {})

    # 경로에 따라 서로 다른 커넥터 함수 호출.
    if route == "embedding":
        raw_result = db_embedding_search(route_payload)
    elif route == "fixed":
        raw_result = db_fixed_search(route_payload)
    else:
        # 라우터가 반드시 둘 중 하나만 내놓아야 하지만, 방어적으로 에러 처리.
        raise ValueError(f"알 수 없는 route입니다: {route}")

    # 다양한 반환 포맷을 list[dict] 로 정규화.
    restaurant_list = _normalize_restaurant_list(raw_result)

    return {
        "restaurant_list": restaurant_list,
    }


def generate_node(state: GraphState) -> GraphState:
    """
    [마지막 단계] 최종 답변을 생성하는 노드.

    지금까지 state 에 모인 모든 재료(question, route, slot, 식당 리스트 등)를
    generator.generate_response 에 넘겨 LLM 답변을 만든다.

    반환값:
        answer:               최종 답변 문자열
        used_restaurant_list: LLM 에 실제 전달된 재랭킹 식당 목록

    전체 흐름 속 위치: connector_search_node → generate_node → END
    """
    # 지금 state 안에 있는 값들을 꺼내 기본값과 함께 안전하게 추출.
    question = state["question"]
    session_id = state.get("session_id", "default")
    route = state.get("route", "embedding")
    route_payload = state.get("route_payload", {})
    restaurant_list = state.get("restaurant_list", [])

    # 검색 결과 메타정보. 예: 후보 수를 LLM 에게 알려줘 답변에 반영하게 함.
    connector_meta = {
        "restaurant_count": len(restaurant_list)
    }

    # ---------------------------------------------------------------
    # 실제 최종 답변 생성 (내부에서 LLM 호출 일어남)
    # ---------------------------------------------------------------
    gen_result = generate_response(
        question=question,
        restaurant_list=restaurant_list,
        route=route,
        session_id=session_id,
        route_payload=route_payload,
        connector_meta=connector_meta,
    )

    # answer 와 used_restaurant_list 를 state 에 반영.
    return {
        "answer": gen_result.get("answer", ""),
        "used_restaurant_list": gen_result.get("used_restaurant_list", []),
    }

def route_condition(state: GraphState) -> str:
    """
    LangGraph 의 조건부 엣지(add_conditional_edges) 용 판정 함수.

    현재 state["route"] 값을 그대로 반환 → "embedding" | "fixed".
    build_graph 에서 이 반환값을 다음 노드로 매핑한다.
    """
    return state["route"]


def build_graph():
    """
    LangGraph 그래프를 조립 + 컴파일해서 반환한다.

    구성:
        START
          → route_node
              ├─(embedding)→ embedding_slot_node
              └─(fixed)────→ fixed_slot_node
                 → connector_search_node
                     → generate_node
                         → END

    Returns:
        컴파일된 StateGraph. .invoke({...}) 로 실행 가능.
    """
    # 우리 프로젝트의 상태 스키마(GraphState) 를 기반으로 그래프 생성.
    graph = StateGraph(GraphState)

    # 각 단계를 "노드" 로 등록.
    graph.add_node("route_node", route_node)
    graph.add_node("embedding_slot_node", embedding_slot_node)
    graph.add_node("fixed_slot_node", fixed_slot_node)
    graph.add_node("connector_search_node", connector_search_node)
    graph.add_node("generate_node", generate_node)

    # 시작점 → route_node 로 들어간다.
    graph.add_edge(START, "route_node")

    # route_node 이후 조건부 분기:
    #   route_condition() 가 반환하는 문자열에 따라 목적지 노드가 달라진다.
    graph.add_conditional_edges(
        "route_node",
        route_condition,
        {
            "embedding": "embedding_slot_node",
            "fixed": "fixed_slot_node",
        },
    )

    # 슬롯 추출 결과는 둘 다 connector_search_node 로 수렴.
    graph.add_edge("embedding_slot_node", "connector_search_node")
    graph.add_edge("fixed_slot_node", "connector_search_node")

    # DB 조회 → 최종 답변 생성 → 종료.
    graph.add_edge("connector_search_node", "generate_node")
    graph.add_edge("generate_node", END)

    # .compile() 을 호출해야 실제로 실행 가능한 그래프 객체가 된다.
    return graph.compile()


def get_graph():
    """
    컴파일된 그래프를 반환한다. (싱글톤 캐싱)

    최초 호출 시 build_graph() 로 만들고, 이후 호출은 캐시 재사용.
    """
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


def run_qa(
    question: str,
    session_id: str = "default",
) -> dict[str, Any]:
    """
    외부에서 호출하는 "한 번의 질의응답" 실행 진입점.

    Args:
        question:   사용자 질문 원문
        session_id: 대화 히스토리를 구분할 세션 ID (기본 "default")

    Returns:
        dict[str, Any]:
            {
                "question":             입력 질문,
                "route":                선택된 경로 (embedding/fixed),
                "route_payload":        추출된 슬롯,
                "restaurant_list":      DB 가 돌려준 원본 식당 후보,
                "used_restaurant_list": 최종 답변에 사용된 식당 후보,
                "answer":               최종 답변 문자열
            }

    전체 흐름 속 위치:
        외부 모듈/서버/CLI 가 이 함수를 호출하면
        그래프 전체(route→slot→DB→generate) 가 한 번 실행된다.
    """
    # 컴파일된 그래프 준비 (최초 1회만 실제 빌드).
    graph = get_graph()

    # 그래프에 초기 state 를 넣어 실행.
    # 내부적으로 노드들이 순서대로 호출되며 state 가 채워진다.
    result = graph.invoke(
        {
            "question": question,
            "session_id": session_id,
        }
    )

    # 외부에 돌려줄 표준 포맷으로 정리.
    return {
        "question": question,
        "route": result.get("route"),
        "route_payload": result.get("route_payload", {}),
        "restaurant_list": result.get("restaurant_list", []),
        "used_restaurant_list": result.get("used_restaurant_list", []),
        "answer": result.get("answer", ""),
    }


def main() -> None:
    """
    `python -m src.pipeline` 실행 시 들어오는 CLI 진입점.

    터미널에서 사용자와 반복적으로 질문을 주고받는 루프.
    빈 Enter 또는 Ctrl+C / Ctrl+D 로 종료.

    전체 흐름 속 위치:
        개발/테스트 용도. 실제 서비스에서는 run_qa() 를 서버가 직접 호출한다.
    """
    print("=" * 60)
    print("맛집 추천 CLI 테스트 (빈 Enter 입력시 종료)")
    print("=" * 60)

    # 종료 입력이 올 때까지 무한 반복.
    while True:
        try:
            # 터미널에서 한 줄 입력 받기. 앞뒤 공백 제거.
            question = input("\n질문 > ").strip()
        except (EOFError, KeyboardInterrupt):
            # 사용자가 Ctrl+D / Ctrl+C 를 누르면 깔끔하게 종료.
            print("\n종료합니다.")
            break

        # 빈 입력이면 종료 신호로 간주.
        if not question:
            print("종료합니다.")
            break

        # 실제 파이프라인 실행.
        result = run_qa(
            question=question,
            session_id="default",
        )

        # 결과 출력: 답변과 실제 사용된 식당 리스트.
        print("\n[답변]")
        print(result["answer"])

        print("\n[restaurant list]")
        print(result["used_restaurant_list"])


# ===========================================================================
# 모듈을 직접 실행할 때만 main() 호출.
#   - `python -m src.pipeline` 또는 `python src/pipeline.py` 로 실행 가능.
#   - 다른 파일에서 `from src.pipeline import run_qa` 로 import 만 할 때는
#     이 블록은 실행되지 않는다.
# ===========================================================================
if __name__ == "__main__":
    main()
