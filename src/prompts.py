"""프로젝트 전역에서 사용하는 프롬프트 상수 모음.

- EMBEDDING_SLOT_PROMPT: 임베딩 라우트에서 슬롯 추출용 프롬프트
- FIXED_SEARCH_PROMPT: 고정 검색(엔티티 직접 지정) 라우트의 슬롯 추출 프롬프트
- ROUTER_PROMPT: embedding / fixed 라우팅 판정 프롬프트
- load_system_prompt(): prompts/system_prompt.txt 를 읽어오는 헬퍼
"""
from __future__ import annotations

from .config import SETTINGS


EMBEDDING_SLOT_PROMPT = """너는 사용자의 음식점 검색 문장을 분석하여
검색에 필요한 핵심 정보를 구조화하는 정보 추출기다.

반드시 JSON 객체만 반환해.
출력 형식은 정확히 다음과 같아야 한다:

{"category": "...", "tag": "...", "menu": "...", "food": "...", "review": "..."}

설명 없이 JSON만 출력한다.

슬롯 정의:

- category: 음식점 카테고리 (예: 한식, 양식, 일식, 카페, 술집 등)
- tag: 분위기/특징/조건 (예: 조용한, 가성비, 데이트, 혼밥, 매운 등)
- menu: 구체적인 메뉴 이름 (예: 곱창전골, 까르보나라, 초밥 등)
- food: 음식 종류 (예: 곱창, 파스타, 초밥 등 상위 개념)
- review: 리뷰/평가 관련 표현 (예: 맛있다, 유명하다, 추천, 별로다 등)

중요 규칙 (매우 중요):

1) category는 음식점의 종류만 넣는다.
   - 예: 한식, 일식, 카페, 술집
   - 없으면 ""로 둔다.

2) tag에는 분위기, 상황, 특징만 넣는다.
   - 예: 조용한, 데이트, 가성비, 혼밥, 분위기 좋은
   - 여러 개면 하나로 대표 키워드만 넣는다.

3) menu에는 "구체적인 메뉴 이름"만 넣는다.
   - 예: 곱창전골, 까르보나라, 초밥
   - 없으면 "".

4) food에는 메뉴의 상위 음식 종류를 넣는다.
   - 예: 곱창전골 → 곱창
   - 파스타 → 파스타
   - 초밥 → 초밥

5) review에는 평가/추천/인기 관련 표현만 넣는다.
   - 예: 맛있는, 유명한, 추천, 별로인 등
   - 없으면 "".

6) 지역명(강남, 신대방삼거리 등)은 어떤 슬롯에도 넣지 않는다.

7) 식당 이름은 이 구조에서는 사용하지 않는다. (무시)

8) 반드시 5개의 키를 모두 포함하고, 없는 값은 ""로 둔다.

9) 추측하지 말고, 문장에서 유추 가능한 정보만 사용한다.

예시:

입력: 신대방삼거리 근처 곱창전골 맛집
출력: {"category": "", "tag": "", "menu": "곱창전골", "food": "곱창", "review": "맛집"}

입력: 강남 조용한 분위기 좋은 파스타집
출력: {"category": "양식", "tag": "조용한", "menu": "", "food": "파스타", "review": ""}

입력: 데이트하기 좋은 초밥 추천
출력: {"category": "일식", "tag": "데이트", "menu": "", "food": "초밥", "review": "추천"}

입력: 가성비 좋은 한식 맛집
출력: {"category": "한식", "tag": "가성비", "menu": "", "food": "", "review": "맛집"}

입력: 그냥 밥 먹을 곳
출력: {"category": "", "tag": "", "menu": "", "food": "", "review": ""}
"""


FIXED_SEARCH_PROMPT = """너는 사용자의 식당 검색 문장에서 restaurant, menu, user 슬롯을 추출하는 정보 추출기다.
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


ROUTER_PROMPT = """
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


def load_system_prompt() -> str:
    if not SETTINGS.prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {SETTINGS.prompt_path}")
    return SETTINGS.prompt_path.read_text(encoding="utf-8")
