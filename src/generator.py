"""최종 응답 생성(Generator).

system prompt + 검색 메타 + 후보 식당 리스트를 LLM에 넘겨
최종 답변 문장을 생성한다. 세션별 대화 히스토리도 유지.

─────────────────────────────────────────────────────────────────────────────
이 파일이 하는 일

    파이프라인의 마지막 단계.
    앞 단계에서 얻어낸 아래 재료들을 모아 LLM 에게 전달하여
    사용자에게 보여줄 "최종 답변 문장" 을 생성한다.

    - 재료 1: system_prompt.txt 에 적힌 전체 규칙 (load_system_prompt)
    - 재료 2: 어느 라우트로 왔는지 (embedding / fixed)
    - 재료 3: 추출된 slot (route_payload)
    - 재료 4: DB 에서 가져온 식당 후보들 (restaurant_list)
    - 재료 5: 간단한 검색 메타정보 (connector_meta)
    - 재료 6: 과거 대화 기록 (session 별 history)

    추가로:
    - simple_retrieve_restaurants 로 후보를 top-k 로 재랭킹
    - 세션 ID 별로 대화 히스토리를 메모리에 저장 (멀티턴 가능)

흐름상의 위치:
    pipeline.generate_node → generate_response() 호출 → 최종 answer 반환
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations
import json
from typing import Any, Callable


from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from .config import SETTINGS
from .prompts import load_system_prompt
from .retriever import simple_retrieve_restaurants


# ---------------------------------------------------------------------------
# 세션별 대화 히스토리 저장용 전역 캐시.
#   - key:   session_id (문자열)
#   - value: 그 세션의 지금까지 메시지들(Human/AI 번갈아) 리스트
#   - 같은 session_id 로 여러 번 호출하면 과거 대화가 이어져 멀티턴이 된다.
# ---------------------------------------------------------------------------
_SESSION_MESSAGES: dict[str, list[BaseMessage]] = {}


def clear_session(session_id: str) -> None:
    """
    특정 세션의 대화 히스토리를 초기화한다.

    Args:
        session_id: 초기화할 세션의 고유 ID.

    전체 흐름 속 위치:
        사용자가 "대화 초기화" 를 원할 때 외부에서 호출되는 API.
        내부적으로 _SESSION_MESSAGES 에서 해당 key 만 제거한다.
    """
    # pop 의 두 번째 인자를 None 으로 주면, 키가 없을 때도 KeyError 없이 안전하게 종료.
    _SESSION_MESSAGES.pop(session_id, None)


def get_llm() -> ChatOpenAI:
    """
    최종 답변 생성에 사용할 ChatOpenAI 인스턴스를 생성해 반환한다.

    Returns:
        ChatOpenAI: LangChain 의 ChatGPT 래퍼 객체.

    왜 매번 새로 만드는가?
        - 내부 상태가 거의 없고, temperature 등 호출 옵션을 바꿀 여지가 있어
          일단은 함수 단위로 생성한다. (임베딩 모델/클라이언트는 싱글톤이지만
          ChatOpenAI 는 그렇지 않아도 무해함)
    """
    return ChatOpenAI(
        # 생성용 모델명 (예: gpt-4.1-mini).
        model=SETTINGS.llm_model,
        # temperature=0: 가능한 한 일관된 답변을 얻기 위한 설정.
        temperature=0,
        # OpenAI API Key.
        api_key=SETTINGS.openai_api_key,
        streaming=True,
    )


def generate_response(
    question: str,
    restaurant_list: list[dict[str, Any]],
    route: str,
    session_id: str = "default",
    route_payload: dict[str, Any] | None = None,
    connector_meta: dict[str, Any] | None = None,
    stream: bool = False,
    stream_callback: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """
    최종 답변을 LLM 을 통해 생성하는 핵심 함수.

    Args:
        question:        사용자 원문 질문.
        restaurant_list: DB/커넥터에서 가져온 식당 후보 리스트.
        route:           "embedding" 또는 "fixed" (어떤 경로로 검색됐는지).
        session_id:      대화 히스토리 키. 기본은 "default".
        route_payload:   슬롯 추출 결과 dict.
        connector_meta:  검색 과정 메타정보 (예: 후보 개수).

    Returns:
        dict[str, Any]:
            {
                "answer":                 str,   # LLM 최종 답변 문장
                "used_restaurant_list":   list   # 실제 답변 생성에 사용된 후보 목록
            }

    전체 흐름 속 위치:
        pipeline.generate_node() 의 마지막 단계에서 호출된다.
        여기서 생성된 answer 가 run_qa() 의 최종 응답이 되어 사용자에게 반환된다.
    """
    # -----------------------------------------------------------------
    # 1) 재료 준비 단계
    # -----------------------------------------------------------------
    # 1-1) system prompt 텍스트 로드 (prompts/system_prompt.txt)
    prompt_rules = load_system_prompt()
    # 1-2) 세션 히스토리 가져오기 (없으면 빈 리스트를 만들어 저장).
    #      setdefault: 키가 이미 있으면 기존 값 반환, 없으면 기본값([])을 넣고 그 값 반환.
    history = _SESSION_MESSAGES.setdefault(session_id, [])

    # 1-3) None 방어 처리: 이후 json.dumps 에서 None 은 에러가 안 나지만,
    #      dict 형태를 보장하기 위해 미리 빈 dict 로 치환.
    route_payload = route_payload or {}
    connector_meta = connector_meta or {}

    # -----------------------------------------------------------------
    # 2) 후보 식당 재랭킹
    #    DB 에서 넘어온 list 가 너무 길 수 있으므로
    #    질문과 매칭이 잘 되는 상위 k개로 간추린다.
    # -----------------------------------------------------------------
    retrieved_restaurants = simple_retrieve_restaurants(
        query=question,
        docs=restaurant_list,
        k=SETTINGS.top_k,
    )

    # -----------------------------------------------------------------
    # 3) 시스템 프롬프트 조립
    #    - 규칙(prompt_rules) + 어떤 라우트로 왔는지 + 슬롯 payload + 메타정보
    #    - JSON 직렬화 시 한글 깨짐 방지를 위해 ensure_ascii=False 지정.
    #    - 이 문자열이 SystemMessage 의 content 로 들어간다.
    # -----------------------------------------------------------------
    system_prompt = f"""
{prompt_rules}

[Search Route]
{route}

[Search Payload]
{json.dumps(route_payload, ensure_ascii=False, indent=2)}

[Connector Meta]
{json.dumps(connector_meta, ensure_ascii=False, indent=2)}
""".strip()

    # -----------------------------------------------------------------
    # 4) 사용자 메시지용 RAG 입력 구성.
    #    - 질문 원문과 재랭킹된 식당 리스트를 한 덩어리 dict 로 묶어
    #      JSON 문자열화해 HumanMessage 로 전달한다.
    #      (LLM 이 정확히 어떤 데이터 위에서 답해야 하는지 알 수 있도록)
    # -----------------------------------------------------------------
    rag_input = {
        "question": question,
        "restaurant_list": retrieved_restaurants,
    }

    # -----------------------------------------------------------------
    # 5) 최종 LLM 호출용 메시지 리스트 구성.
    #    순서가 중요:
    #       (1) SystemMessage:   규칙/컨텍스트
    #       (2) *history:        과거 대화 (멀티턴 문맥)
    #       (3) HumanMessage:    이번에 새로 들어온 질문 + 데이터
    # -----------------------------------------------------------------
    messages: list[BaseMessage] = [
        SystemMessage(content=system_prompt),
        *history,
        HumanMessage(content=json.dumps(rag_input, ensure_ascii=False, indent=2)),
    ]

    # -----------------------------------------------------------------
    # 6) 실제 LLM 호출 지점!
    #    get_llm() 에서 만든 ChatOpenAI 로 .invoke(messages) 실행 →
    #    모델이 최종 답변을 돌려준다.
    # -----------------------------------------------------------------
    llm = get_llm()

    if stream:
        full_response = ""

        for chunk in llm.stream(messages):
            piece = chunk.content if hasattr(chunk, "content") else str(chunk)
            if piece:
                full_response += piece

                if stream_callback is not None:
                    stream_callback(full_response)
                else:
                    print(piece, end="", flush=True)

        if stream_callback is None:
            print()

        response = full_response
    else:
        result = llm.invoke(messages)
        response = result.content if hasattr(result, "content") else str(result)


    # -----------------------------------------------------------------
    # 7) 히스토리 업데이트
    #    - 이번 질문과 모델의 답변을 이어 붙여 두면
    #      다음 턴에 문맥으로 재사용 가능.
    # -----------------------------------------------------------------
    history.append(HumanMessage(content=question))
    history.append(AIMessage(content=response))

    # -----------------------------------------------------------------
    # 8) 최종 결과 반환.
    #    answer: 화면에 보여줄 문장.
    #    used_restaurant_list: 실제로 답변에 사용된 식당 목록.
    # -----------------------------------------------------------------
    return {
        "answer": response,
        "used_restaurant_list": retrieved_restaurants,
    }
