"""프로젝트 전역에서 공유되는 OpenAI 클라이언트 싱글톤.

─────────────────────────────────────────────────────────────────────────────
왜 이 파일이 필요한가?
    - OpenAI API 호출은 여러 모듈(slot_extractor, embeddings, generator 등)에서
      반복적으로 일어난다.
    - 모듈마다 OpenAI(...) 를 새로 생성하면 자원 낭비 + API Key 체크 로직 중복.
    - 따라서 "한 번 만들어 두고 계속 재사용"하는 싱글톤(singleton) 패턴으로 관리한다.

흐름상의 위치:
    slot_extractor → get_openai_client() 로 클라이언트 가져옴 → LLM 호출
    embeddings     → (OpenAIEmbeddings 래퍼로 별도 호출. 이 파일의 클라이언트와는 별개)
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations
from openai import OpenAI
from .config import SETTINGS


# ---------------------------------------------------------------------------
# 모듈 전역 변수: 한 번 만들어진 OpenAI 클라이언트를 캐싱해 두는 자리.
#   - None 으로 시작하고, 최초 호출 시 실제 객체로 채워진다.
#   - 이후에는 계속 같은 객체를 반환한다. (싱글톤 패턴)
# ---------------------------------------------------------------------------
_client: OpenAI | None = None


def get_openai_client() -> OpenAI:
    """
    OpenAI API 호출에 사용할 클라이언트를 반환하는 함수.

    이미 생성된 클라이언트가 있으면 재사용하고,
    없으면 환경변수에 저장된 API 키로 새로 생성한다.
    API 키가 설정되지 않은 경우에는 에러를 발생시킨다.

    Returns:
        OpenAI: OpenAI API 요청에 사용할 클라이언트 객체

    전체 흐름 속 위치:
        slot_extractor._make_embedding_slot_json / _make_fixed_search_json
        등에서 이 함수를 호출해 실제 LLM 요청을 보낸다.
    """
    # 함수 바깥(모듈 전역)에 있는 _client 변수를 수정하기 위해 global 선언.
    global _client
    # 최초 호출(= 아직 클라이언트를 안 만들었을 때)만 실제 객체를 생성한다.
    if _client is None:
        # API 키가 비어 있으면 더 진행할 수 없으므로 즉시 에러.
        if not SETTINGS.openai_api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되어 있지 않습니다.")
        # OpenAI 공식 SDK 클라이언트 생성. 여기서 API Key 를 주입한다.
        _client = OpenAI(api_key=SETTINGS.openai_api_key)
    # 두 번째 호출부터는 곧바로 캐싱된 객체를 반환 → 불필요한 재생성 방지.
    return _client
