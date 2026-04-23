"""
슬롯 추출(Slot Extractor).

사용자 입력 문장에서 슬롯을 추출한다.
두 라우트(`embedding` / `fixed`) 가 있으며,
프롬프트와 JSON schema name만 다르고 클라이언트/파싱 로직은 동일하므로 한 파일에서 관리한다.

- `embedding_slot_extract` (@tool): 분위기/취향 중심 검색 경로의 슬롯 추출
- `fixed_search`            (@tool): 엔티티 직접 지칭 검색 경로의 슬롯 추출

─────────────────────────────────────────────────────────────────────────────
이 파일이 하는 일

    라우터(router.py)가 "이 질문은 embedding 이야 / fixed 야"를 정해 주면,
    이 파일은 그에 맞춰 다음 단계에서 DB 검색에 쓸 수 있도록
    사용자 문장을 "구조화된 키-값(JSON)"으로 분해한다.

    예시)
        embedding 경로: "강남 조용한 파스타집"
            → {"category":"양식", "tag":"조용한", "menu":"", "food":"파스타", "review":""}

        fixed 경로:     "강남 파스타 연구소 까르보나라"
            → {"restaurant":"강남 파스타 연구소", "menu":"까르보나라", "user":""}

    각 함수는 LangChain 의 @tool 데코레이터로 감싸져 있어
    LangGraph 등의 에이전트 워크플로우에서 "Tool" 로 등록/호출된다.

흐름상의 위치:
    pipeline.embedding_slot_node / fixed_slot_node 가 각각 아래 두 @tool 함수를 호출
    → 반환된 slot 딕셔너리가 state["route_payload"] 로 저장됨
    → connector_search_node 에서 DB 검색 질의로 사용.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations
import json
from typing import Dict
from langchain_core.tools import tool
from .config import SETTINGS
from .llm_client import get_openai_client
from .prompts import EMBEDDING_SLOT_PROMPT, FIXED_SEARCH_PROMPT


# fixed 경로에 사용할 기본 모델명. 전역 설정에서 끌어와 변수에 담아 둔다.
DEFAULT_FIXED_SEARCH_MODEL = SETTINGS.fixed_search_model


def _parse_slot_json(raw_json: str) -> Dict[str, str]:
    """
    LLM 이 반환한 JSON 문자열을 검증·정제해서 dict 로 바꿔주는 내부 함수.

    Args:
        raw_json: LLM 응답으로 받은 JSON 텍스트.

    Returns:
        Dict[str, str]:
            - embedding 스키마이면 {category, tag, menu, food, review} 5키
            - fixed 스키마이면     {restaurant, menu, user} 3키
            모든 값은 strip 된 문자열.

    Raises:
        ValueError:
            - JSON 파싱 실패
            - JSON 이 object 가 아님
            - 알려진 스키마(위 두 종류) 중 어디에도 해당하지 않음
            - 각 슬롯 값이 문자열이 아님

    전체 흐름 속 위치:
        _make_embedding_slot_json / _make_fixed_search_json 이 받아온
        원시 JSON 문자열을 최종 dict 로 바꿔 상위 함수(@tool)에게 넘겨준다.
    """
    # 1) 문자열 → Python 객체(dict 예상) 변환. 실패하면 명확한 에러로 감싼다.
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 파싱 실패: {e}") from e

    # 2) 최상위 구조가 dict 가 아니면 규격 위반이므로 거부.
    if not isinstance(data, dict):
        raise ValueError("모델 응답이 JSON object가 아닙니다.")

    # embedding 슬롯 구조
    # embedding 라우트에서 기대하는 키 집합.
    embedding_keys = {"category", "tag", "menu", "food", "review"}

    # fixed 슬롯 구조
    # fixed 라우트에서 기대하는 키 집합.
    fixed_keys = {"restaurant", "menu", "user"}

    # 실제 응답이 가진 키 집합.
    data_keys = set(data.keys())

    # 1) embedding 응답인 경우
    # -----------------------------------------------------------------
    # 3-A) embedding 스키마 매칭 (category/tag/menu/food/review 전부 포함)
    # -----------------------------------------------------------------
    if embedding_keys.issubset(data_keys):
        # 각 값이 None 일 수도 있으므로 or "" 로 안전하게 빈 문자열 치환.
        category = data.get("category", "") or ""
        tag = data.get("tag", "") or ""
        menu = data.get("menu", "") or ""
        food = data.get("food", "") or ""
        review = data.get("review", "") or ""

        # 타입 검증: 모든 값이 str 이어야 함.
        if not all(isinstance(v, str) for v in [category, tag, menu, food, review]):
            raise ValueError("category, tag, menu, food, review 값은 문자열이어야 합니다.")

        # strip 으로 좌우 공백 제거 후 깔끔한 dict 반환.
        return {
            "category": category.strip(),
            "tag": tag.strip(),
            "menu": menu.strip(),
            "food": food.strip(),
            "review": review.strip(),
        }

    # 2) fixed 응답인 경우
    # -----------------------------------------------------------------
    # 3-B) fixed 스키마 매칭 (restaurant/menu/user 전부 포함)
    # -----------------------------------------------------------------
    if fixed_keys.issubset(data_keys):
        restaurant = data.get("restaurant", "") or ""
        menu = data.get("menu", "") or ""
        user = data.get("user", "") or ""

        if not all(isinstance(v, str) for v in [restaurant, menu, user]):
            raise ValueError("restaurant, menu, user 값은 문자열이어야 합니다.")

        return {
            "restaurant": restaurant.strip(),
            "menu": menu.strip(),
            "user": user.strip(),
        }

    # -----------------------------------------------------------------
    # 3-C) 어떤 스키마에도 속하지 않으면 명확한 에러로 실패.
    # -----------------------------------------------------------------
    raise ValueError(
        "알 수 없는 슬롯 JSON 구조입니다. "
        "embedding(category/tag/menu/food/review) 또는 "
        "fixed(restaurant/menu/user) 구조여야 합니다."
    )


def _make_embedding_slot_json(
    instr: str,
    model: str | None = None,
) -> str:
    """
    "embedding 라우트용" 슬롯 JSON 문자열을 LLM 에게 받아오는 내부 함수.

    Args:
        instr: 사용자의 자연어 질문 문자열.
        model: 사용할 모델명. None 이면 SETTINGS.fixed_search_model 로 대체.

    Returns:
        str: LLM 이 반환한 JSON 문자열 (아직 파싱 전 상태)

    전체 흐름 속 위치:
        embedding_slot_extract() 에서 호출 → 반환 문자열을 _parse_slot_json() 으로 넘김.
    """
    # 호출 시점에 모델이 지정되지 않았으면 기본 모델 사용.
    model = model or SETTINGS.fixed_search_model

    # -----------------------------------------------------------------
    # 실제 LLM 호출 지점! (OpenAI chat.completions.create)
    #   - response_format 을 json_schema 로 엄격히 지정하여
    #     LLM 이 반드시 해당 스키마의 JSON 만 뱉도록 강제한다.
    #     (LLM 의 잡음 답변 방지)
    # -----------------------------------------------------------------
    completion = get_openai_client().chat.completions.create(
        model=model,
        messages=[
            # developer 역할: 시스템 지시문처럼 동작. 슬롯 추출 규칙을 담은 프롬프트.
            {"role": "developer", "content": EMBEDDING_SLOT_PROMPT},
            # user 역할: 실제 사용자 문장 (질문 원문).
            {"role": "user", "content": instr},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "embedding_slot_result",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string"},
                        "tag": {"type": "string"},
                        "menu": {"type": "string"},
                        "food": {"type": "string"},
                        "review": {"type": "string"},
                    },
                    "required": ["category", "tag", "menu", "food", "review"],
                    "additionalProperties": False,
                },
            },
        },
        # temperature=0: 동일 입력엔 동일 출력. 슬롯 추출 일관성 확보.
        temperature=0,
        # max_completion_tokens: 짧은 JSON 만 뽑으므로 120 토큰 정도면 충분.
        max_completion_tokens=120,
        top_p=1,
    )

    # 첫 번째 후보 응답의 내용물을 꺼내오고, 비어있으면 에러.
    content = completion.choices[0].message.content
    if not content:
        raise ValueError("모델이 빈 응답을 반환했습니다.")
    return content


def _make_fixed_search_json(
    instr: str,
    model: str = DEFAULT_FIXED_SEARCH_MODEL,
) -> str:
    """
    "fixed 라우트용" 슬롯 JSON 문자열을 LLM 에게 받아오는 내부 함수.

    Args:
        instr: 사용자의 자연어 질문 문자열.
        model: 사용할 모델명. 기본값은 DEFAULT_FIXED_SEARCH_MODEL.

    Returns:
        str: LLM 이 반환한 JSON 문자열 (아직 파싱 전 상태)

    전체 흐름 속 위치:
        fixed_search() 에서 호출 → 반환 문자열을 _parse_slot_json() 으로 넘김.
    """
    # -----------------------------------------------------------------
    # 실제 LLM 호출 지점! (_make_embedding_slot_json 과 프롬프트/스키마만 다름)
    # -----------------------------------------------------------------
    completion = get_openai_client().chat.completions.create(
        model=model,
        messages=[
            {"role": "developer", "content": FIXED_SEARCH_PROMPT},
            {"role": "user", "content": instr},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "fixed_search_result",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "restaurant": {"type": "string"},
                        "menu": {"type": "string"},
                        "user": {"type": "string"},
                    },
                    "required": ["restaurant", "menu", "user"],
                    "additionalProperties": False,
                },
            },
        },
        temperature=0,
        max_completion_tokens=120,
        top_p=1,
    )

    content = completion.choices[0].message.content
    if not content:
        raise ValueError("모델이 빈 응답을 반환했습니다.")
    return content


# ---------------------------------------------------------------------------
# @tool 데코레이터로 감싸 LangChain/LangGraph 에서 호출 가능한 툴로 노출.
#   - pipeline.py 의 embedding_slot_node 에서 .invoke(question) 형태로 호출됨.
# ---------------------------------------------------------------------------
@tool("embedding_slot_extract")
def embedding_slot_extract(instr: str) -> Dict[str, str]:
    """
    사용자 입력을 category/tag/menu/food/review 슬롯 구조로 1차 반환한다.

    Returns:
        {
            "category": "...",
            "tag": "...",
            "menu": "...",
            "food": "...",
            "review": "..."
        }
    """
    # 빈 문자열·공백만 들어오면 LLM 호출을 건너뛰고 빈 슬롯을 반환해 비용 절약.
    instr = (instr or "").strip()
    if not instr:
        return {
            "category": "",
            "tag": "",
            "menu": "",
            "food": "",
            "review": "",
        }

    # 1) LLM 으로 JSON 문자열 받기 → 2) 파싱/검증해서 dict 로 반환.
    raw_json = _make_embedding_slot_json(instr)
    return _parse_slot_json(raw_json)


# ---------------------------------------------------------------------------
# @tool 데코레이터로 감싸 LangChain/LangGraph 에서 호출 가능한 툴로 노출.
#   - pipeline.py 의 fixed_slot_node 에서 .invoke(question) 형태로 호출됨.
# ---------------------------------------------------------------------------
@tool("fixed_search")
def fixed_search(instr: str) -> Dict[str, str]:
    """
    사용자 검색 문장을 restaurant/menu/user 슬롯으로 분류해 반환한다.
    """
    # 입력 방어: 빈 문자열이면 바로 빈 슬롯을 반환.
    instr = (instr or "").strip()
    if not instr:
        return {"restaurant": "", "menu": "", "user": ""}

    # 1) LLM 호출로 JSON 문자열 → 2) 파싱/검증 → 3) dict 반환.
    raw_json = _make_fixed_search_json(instr)
    return _parse_slot_json(raw_json)


# ===========================================================================
# __main__ 실행부
#   - `python -m src.slot_extractor` 로 이 파일을 직접 실행하면
#     아래의 두 테스트 문장에 대해 embedding / fixed 결과를 찍어본다.
#   - 주로 개발/검증용.
# ===========================================================================
if __name__ == "__main__":
    # embedding 경로 예시 테스트.
    test_input = "조용하고 가성비 좋은 곳에서 먹을 만한 초밥집 추천해줘"
    print("[embedding]", embedding_slot_extract.invoke(test_input))

    # fixed 경로 예시 테스트.
    test_input2 = "초밥천사 집에 우동 팔아?"
    print("[fixed]", fixed_search.invoke(test_input2))
