"""라우터(Router).

사용자 질문을 보고 `embedding` / `fixed` 경로 중 하나를 선택한다.

─────────────────────────────────────────────────────────────────────────────
이 파일이 하는 일

    "이 질문은 조건(분위기/취향) 중심이야? 아니면 특정 식당 이름/메뉴 지정이야?"
    를 LLM 에게 물어보고 답을 받아, 뒤 단계에서 어떤 방식으로 검색할지 결정한다.

    → 반환값은 정확히 두 가지 문자열 중 하나:
        - "embedding" : 벡터 유사도 기반 탐색 경로로 진행
        - "fixed"     : 식당명/메뉴명 등 명시된 엔티티 기반 검색 경로로 진행

    이후 pipeline.py 의 LangGraph 에서
    이 반환값을 조건부 엣지(add_conditional_edges) 분기 기준으로 사용한다.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations
from langchain_openai import ChatOpenAI
from .config import SETTINGS
from .prompts import ROUTER_PROMPT


def decide_route(question: str) -> str:
    """
    사용자 질문을 입력받아 "embedding" 또는 "fixed" 중 어느 경로로 갈지 결정한다.

    Args:
        question: 사용자가 입력한 자연어 질문 (예: "강남 조용한 파스타집")

    Returns:
        "fixed"     : 특정 식당/메뉴/유저 등 엔티티가 명시된 검색이면 이쪽
        "embedding" : 조건 기반(분위기/취향) 검색이거나 애매하면 이쪽 (기본값)

    전체 흐름 속 위치:
        pipeline.route_node() 에서 호출되어, LangGraph 의 다음 노드
        (embedding_slot_node / fixed_slot_node) 를 결정하는 분기 값이 된다.
    """
    # -----------------------------------------------------------------
    # 1) 라우팅 판정용 LLM 인스턴스 생성.
    #    - temperature=0 : 항상 동일한 답이 나오도록(결정적). 분기 안정성이 중요.
    # -----------------------------------------------------------------
    llm = ChatOpenAI(
        model=SETTINGS.router_model,
        temperature=0,
        api_key=SETTINGS.openai_api_key,
    )

    # -----------------------------------------------------------------
    # 2) 실제 LLM 호출!
    #    - ROUTER_PROMPT 안의 {question} 자리에 사용자의 실제 질문을 끼워 넣고
    #      llm.invoke(...) 로 호출하여 응답 content 를 문자열로 받는다.
    #    - 공백 제거 및 소문자화하여 포함 여부 검사에 유리하게 정규화.
    # -----------------------------------------------------------------
    raw = llm.invoke(ROUTER_PROMPT.replace("{question}", question)).content.strip().lower()
    # 모델이 "fixed" 라고 답했으면 엔티티 기반 검색 경로 선택.
    if "fixed" in raw:
        return "fixed"
    # 그 외 모든 경우(= "embedding" 이거나 애매한 출력)는 embedding 경로로 기본 분기.
    return "embedding"
