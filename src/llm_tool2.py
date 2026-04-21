import json
from typing import Dict

from openai import OpenAI
from langchain_core.tools import tool

from .config import SETTINGS

DEFAULT_FIXED_SEARCH_MODEL = SETTINGS.fixed_search_model

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        if not SETTINGS.openai_api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되어 있지 않습니다.")
        _client = OpenAI(api_key=SETTINGS.openai_api_key)
    return _client


prompt = """너는 사용자의 식당 검색 문장에서 restaurant, menu, user 슬롯을 추출하는 정보 추출기다.
반드시 JSON 객체만 반환해.
출력 형식은 정확히 {"restaurant": "...", "menu": "...", "user": "..."} 이어야 한다.

슬롯 정의:
- restaurant: 실제 식당/카페/브랜드/매장 이름으로 직접 지칭된 표현
- menu: 사용자가 직접 언급한 음식명, 메뉴명, 요리명, 음료명
- user: 리뷰어, 작성자, 유저, 닉네임, 블로거, 인플루언서 등 사람 이름

중요 규칙:
1) restaurant에는 실제 상호명으로 직접 지칭된 표현만 넣는다.
2) 지역명, 장소명, "근처", "맛집", "카페", "식당", "음식점", "분위기 좋은", "데이트", "조용한" 같은 일반 탐색 표현은 restaurant에 넣지 않는다.
3) menu에는 사용자가 직접 말한 음식/메뉴만 넣는다.
4) user에는 사람 이름/닉네임만 넣는다.
5) 어떤 표현이 음식명일 수도 있고 상호명일 수도 있어 애매하면 추측하지 말고 해당 슬롯은 빈 문자열로 둔다.
6) 식당명, 메뉴명, 유저명이 동시에 등장하면 각각 해당 슬롯에 채운다.
7) 반드시 restaurant, menu, user 세 키를 모두 포함하고, 없으면 ""로 둔다.
8) 설명, 마크다운, 코드블록 없이 JSON만 출력한다.

예시:
입력: 신대방삼거리 근처 곱창전골 맛집
출력: {"restaurant": "", "menu": "곱창전골", "user": ""}

입력: 강남 파스타 연구소 까르보나라
출력: {"restaurant": "강남 파스타 연구소", "menu": "까르보나라", "user": ""}

입력: 먹잘알_민수 추천 초밥
출력: {"restaurant": "", "menu": "초밥", "user": "먹잘알_민수"}

입력: 분위기 좋은 데이트 카페
출력: {"restaurant": "", "menu": "", "user": ""}

입력: 곱창
출력: {"restaurant": "", "menu": "곱창", "user": ""}"""


def _make_fixed_search_json(instr: str, model: str = DEFAULT_FIXED_SEARCH_MODEL) -> str:
    completion = _get_client().chat.completions.create(
        model=model,
        messages=[
            {"role": "developer", "content": prompt},
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


def _parse_fixed_search_json(raw_json: str) -> Dict[str, str]:
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 파싱 실패: {e}") from e

    if not isinstance(data, dict):
        raise ValueError("모델 응답이 JSON object가 아닙니다.")

    restaurant = data.get("restaurant", "") or ""
    menu = data.get("menu", "") or ""
    user = data.get("user", "") or ""

    if not isinstance(restaurant, str) or not isinstance(menu, str) or not isinstance(user, str):
        raise ValueError("restaurant, menu, user 값은 문자열이어야 합니다.")

    return {
        "restaurant": restaurant.strip(),
        "menu": menu.strip(),
        "user": user.strip(),
    }


@tool("fixed_search")
def fixed_search(instr: str) -> Dict[str, str]:
    """
    사용자 검색 문장을 restaurant/menu/user 슬롯으로 분류해 반환한다.
    """
    instr = (instr or "").strip()
    if not instr:
        return {"restaurant": "", "menu": "", "user": ""}

    raw_json = _make_fixed_search_json(instr)
    parsed = _parse_fixed_search_json(raw_json)
    return parsed

# 구조 테스트용
if __name__ == "__main__":
    test_input = "신대방삼거리 근처 곱창전골 맛집"
    result = fixed_search.invoke(test_input)
    print(result)
    print("타입: ", type(result))