from __future__ import annotations

import ast
import json
import math
from typing import Any, Dict, List

from openai import OpenAI

from .config import SETTINGS
from .embeddings import embed_query
from .llm_tool2 import _parse_fixed_search_json


_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        if not SETTINGS.openai_api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되어 있지 않습니다.")
        _client = OpenAI(api_key=SETTINGS.openai_api_key)
    return _client


EMBEDDING_SLOT_PROMPT = """너는 사용자의 검색 문장에서
식당 이름, 메뉴 이름, 유저 이름만 정확하게 추출하는 정보 추출기다.

반드시 JSON 객체만 반환해.
출력 형식은 정확히 {"restaurant": "...", "menu": "...", "user": "..."} 이어야 한다.

슬롯 정의:
- restaurant: 실제 존재하는 식당 이름 (고유명사)
- menu: 실제 음식/메뉴 이름 (예: 곱창전골, 파스타, 초밥 등)
- user: 리뷰어, 작성자, 닉네임 등 사람 이름

중요 규칙 (매우 중요):

1) restaurant에는 반드시 "실제 식당 이름"만 넣는다.
   - "맛집", "근처", "카페", "식당", "데이트", "분위기 좋은 곳" 같은 일반 표현은 절대 넣지 않는다.
   - 식당 이름이 명확히 없으면 빈 문자열("")로 둔다.

2) menu에는 음식/메뉴 이름만 넣는다.
   - 예: 곱창전골, 파스타, 초밥, 라면 등

3) user에는 사람 이름/닉네임만 넣는다.

4) 지역명(신대방삼거리, 강남 등), 조건(데이트, 조용한 등), 일반 검색어는
   restaurant에 넣지 말고 무시한다.

5) 추측하지 말 것.
   명확한 식당 이름이 없으면 restaurant는 반드시 "".

6) 반드시 3개의 키를 모두 포함하고, 없는 값은 ""로 둔다.

7) 설명 없이 JSON만 출력한다.

예시:

입력: 신대방삼거리 근처 곱창전골 맛집
출력: {"restaurant": "", "menu": "곱창전골", "user": ""}

입력: 강남 파스타 연구소 까르보나라
출력: {"restaurant": "강남 파스타 연구소", "menu": "까르보나라", "user": ""}

입력: 먹잘알_민수 추천 초밥집
출력: {"restaurant": "", "menu": "초밥", "user": "먹잘알_민수"}

입력: 분위기 좋은 데이트 카페
출력: {"restaurant": "", "menu": "", "user": ""}"""


def _make_embedding_slot_json(
    instr: str,
    model: str | None = None,
) -> str:
    model = model or SETTINGS.fixed_search_model

    completion = _get_client().chat.completions.create(
        model=model,
        messages=[
            {"role": "developer", "content": EMBEDDING_SLOT_PROMPT},
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


class EmbeddingSearchService:
    """
    1) 사용자 입력 -> 슬롯 구조 추출
    2) DB connector 후보들(restaurant 단위 nested 구조) + 원본 query -> review 단위로 펼친 뒤 유사도 재정렬(top-k)
    """

    def extract_slots(self, instr: str) -> Dict[str, str]:
        instr = (instr or "").strip()
        if not instr:
            return {"restaurant": "", "menu": "", "user": ""}

        raw_json = _make_embedding_slot_json(instr)
        return _parse_fixed_search_json(raw_json)


embedding_service = EmbeddingSearchService()

# 1차 구조 테스트 용
if __name__ == "__main__":
    test_input = "초밥천사 집에 우동 팔아?"
    result = embedding_service.extract_slots(test_input)

    print("결과:", result)
    print("전체 타입:", type(result))

    print("\n--- 각 필드 타입 ---")
    for k, v in result.items():
        print(f"{k}: {v} / type={type(v)}")