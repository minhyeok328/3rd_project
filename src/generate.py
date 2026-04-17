from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage

from typing import List, Dict, Callable, Any
import json

from .config import SETTINGS

def load_prompt_template() -> str:
    # 프롬프트 템플릿 파일이 실제로 존재하는지 먼저 확인한다.
    if not SETTINGS.prompt_path.exists():
        # 파일이 없으면 즉시 예외를 발생시켜 원인을 명확히 알린다.
        raise FileNotFoundError(f"Prompt file not found: {SETTINGS.prompt_path}")
    # UTF-8 인코딩으로 프롬프트 규칙 파일 내용을 문자열로 읽어 반환한다.
    return SETTINGS.prompt_path.read_text(encoding='utf-8')

# 세션별 대화 이력을 메모리에 보관하는 전역 저장소다.
_SESSION_MESSAGES: dict[str, list[BaseMessage]] = {}

# {
#     "default": [SystemMessage(...), HumanMessage(...), AIMessage(...)],
#     "user1": [...],
#     "abc123": [...]
# }

def clear_session(session_id: str) -> None:
    # 지정한 세션의 이력을 삭제한다(없으면 아무 동작도 하지 않음).
    _SESSION_MESSAGES.pop(session_id, None)

# def build_context(chunks: List[Dict[str, str]]) -> str:
#     if not chunks:
#         return "관련 문맥 없음"
#     return "\n\n".join(
#         f"[{i+1}] {chunk.get('text', '')}" for i, chunk in enumerate(chunks)
#     )

_llm_chain = None

def get_llm_chain():
    # 전역 체인을 재사용하기 위해 전역 변수 접근을 선언한다.
    global _llm_chain
    # 체인이 아직 생성되지 않았다면 최초 1회만 생성한다.
    if _llm_chain is None:
        # 설정 파일의 모델명을 사용해 OpenAI 채팅 모델 인스턴스를 만든다.
        llm = ChatOpenAI(model=SETTINGS.llm_model, temperature=0)
        # 모델 출력(Message)을 순수 문자열로 변환하는 파서를 체인에 연결한다.
        _llm_chain = llm | StrOutputParser()
    # 생성 또는 캐시된 체인을 반환한다.
    return _llm_chain

def generate_response(question: str, session_id: str = "default") -> str:
    # 시스템 프롬프트(규칙/지침) 템플릿을 로드한다.
    prompt_rules = load_prompt_template()
    # context = build_context(chunks)
    # if context == "관련 문맥 없음":
    #     return "해당 자료 기준으로는 확인되지 않습니다."

    # 세션별 이력을 가져오고, 없으면 빈 리스트로 새로 만든다.
    history = _SESSION_MESSAGES.setdefault(session_id, [])

    # prompt = f"{prompt_rules}\n\n[Context]\n{context}\n\n[Question]\n{question}"
    # 현재는 질문만 포함한 시스템 프롬프트를 구성한다.
    prompt = f"{prompt_rules}\n\n[Question]\n{question}"

    # 시스템 지침 + 기존 이력 + 현재 사용자 질문 순서로 메시지 배열을 만든다.
    messages: list[BaseMessage] = [
        SystemMessage(content=prompt),
        *history,
        HumanMessage(content=question),
    ]

    # 재사용 가능한 LLM 체인을 가져온다.
    chain = get_llm_chain()
    # 구성된 메시지를 LLM에 전달해 최종 텍스트 답변을 생성한다.
    response = chain.invoke(messages)
    
    # 현재 질문을 세션 이력에 추가해 다음 턴에서 문맥을 유지한다.
    history.append(HumanMessage(content=question))
    # 모델의 답변도 세션 이력에 추가해 대화 연속성을 확보한다.
    history.append(AIMessage(content=response))

    # 호출자에게 생성된 답변 문자열을 반환한다.
    return response


# def _parse_json_list(raw_text: str) -> list[dict[str, Any]]:
#     """LLM string 응답을 JSON list[dict]로 안전하게 변환한다."""
#     parsed = json.loads(raw_text)

#     if not isinstance(parsed, list):
#         raise ValueError("First LLM response must be a JSON array.")

#     for idx, item in enumerate(parsed):
#         if not isinstance(item, dict):
#             raise ValueError(f"JSON item at index {idx} must be an object.")

#     return parsed


# def generate_two_stage(
#     query: str,
#     search_fn: Callable[[str], Any],
#     prompt1_builder: Callable[[str, Any], str],
#     prompt2_builder: Callable[[str, dict[str, Any]], str],
# ) -> list[str]:
#     """
#     스케치한 구조를 그대로 반영한 2-stage 생성 파이프라인.

#     1) search_fn(query)로 검색 결과를 가져오고
#     2) prompt1_builder(query, search_result)로 1차 프롬프트 생성
#     3) LLM 문자열 응답을 JSON list[dict]로 파싱
#     4) 각 item마다 prompt2_builder(query, item)로 2차 프롬프트 생성 및 LLM 호출
#     5) 최종 문자열 결과 리스트 반환
#     """
#     chain = get_llm_chain()

#     search_result = search_fn(query)

#     prompt1 = prompt1_builder(query, search_result)
#     stage1_raw = chain.invoke([HumanMessage(content=prompt1)])
#     stage1_items = _parse_json_list(stage1_raw)

#     final_results: list[str] = []
#     for item in stage1_items:
#         prompt2 = prompt2_builder(query, item)
#         stage2_raw = chain.invoke([HumanMessage(content=prompt2)])
#         final_results.append(stage2_raw)

#     return final_results