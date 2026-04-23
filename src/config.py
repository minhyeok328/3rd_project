"""
프로젝트 전역 설정(Settings) 모듈.

이 파일은 프로젝트 어디에서든 공통으로 사용하는 환경 설정값을 한곳에서 관리한다.
- 어떤 LLM 모델을 쓸지, 어떤 임베딩 모델을 쓸지
- OpenAI API Key 는 어디서 읽을지
- system prompt 파일의 위치
- 검색 결과 상위 몇 개(top_k)를 쓸지
등의 값을 `.env` 파일(환경변수)에서 로드하여 `SETTINGS` 라는 단일 객체로 제공한다.

다른 모듈(`llm_client`, `embeddings`, `router`, `generator` 등)은
`from .config import SETTINGS` 형태로 이 설정값을 꺼내 쓴다.
"""

from pathlib import Path
import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()

# ---------------------------------------------------------------------------
# BASE_DIR: 프로젝트 루트 디렉터리의 절대 경로
#   - __file__ 은 현재 파일(config.py)의 경로
#   - .resolve() 로 절대경로 변환 후, .parent.parent 로 두 단계 상위 폴더를 잡는다.
#     (src/config.py → src/ → 프로젝트 루트)
#   - prompt_path 같은 상대 위치를 계산할 때 기준점이 된다.
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ===========================================================================
# Settings 데이터 클래스
# ===========================================================================
@dataclass(frozen=True)
class Settings:
    """
    프로젝트 전역 설정 값들을 담는 불변(freeze) 데이터 클래스.

    역할:
        - 환경변수(.env) 에 정의된 값을 읽어 기본값과 함께 보관한다.
        - `frozen=True` 로 선언되어 있어 한 번 생성된 이후에는 값을 바꿀 수 없다.
          (실행 도중 설정이 바뀌어 버그가 생기는 것을 방지)

    주요 필드:
        llm_model          : 최종 답변 생성(generator)에 사용할 LLM 모델명
        embedding_model    : 텍스트 임베딩에 사용할 모델명
        fixed_search_model : fixed/embedding 슬롯 추출에 사용할 모델명
        router_model       : 질문을 embedding/fixed 로 분기시키는 라우터용 모델명
        openai_api_key     : OpenAI API 호출에 필요한 키 (없으면 호출 시 에러)
        prompt_path        : system prompt 텍스트 파일 경로
        top_k              : 검색 결과 중 상위 몇 개 식당을 쓸지 결정하는 숫자

    전체 흐름 속 위치:
        router → slot_extractor → retriever → generator 모든 단계에서
        이 Settings 인스턴스(SETTINGS)를 참조하여 동작한다.
    """

    # LLM 모델명. 환경변수 LLM_MODEL 이 없으면 기본값 "gpt-4.1-mini" 사용.
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4.1-mini")
    # 임베딩 모델명. 환경변수 EMBEDDING_MODEL 이 없으면 text-embedding-3-small 사용.
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    # 슬롯 추출(고정/임베딩) 호출 시 쓰는 모델명.
    fixed_search_model: str = os.getenv("FIXED_SEARCH_MODEL", "gpt-4o-mini")
    # 라우터(질문 분기) 전용 모델명.
    router_model: str = os.getenv("ROUTER_MODEL", "gpt-4.1-mini")

    # OpenAI API 호출에 필요한 키. 기본값은 빈 문자열로,
    # 빈 문자열이면 실제 호출 시점에 ValueError 로 안전하게 실패한다.
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # system prompt 텍스트 파일 경로.
    # prompts/load_system_prompt() 가 이 경로의 파일을 읽어 LLM 에 넘긴다.
    prompt_path: Path = BASE_DIR / "prompts" / "system_prompt.txt"

    # 검색 결과 상위 몇 개를 활용할지. 기본값 5.
    top_k: int = int(os.getenv("TOP_K", "5"))

# ---------------------------------------------------------------------------
# SETTINGS: 이 모듈을 import 하는 모든 파일이 공유하는 싱글턴 설정 객체.
#   - 일반적인 접근 방법: `from .config import SETTINGS` 후 SETTINGS.llm_model 처럼 사용.
# ---------------------------------------------------------------------------
SETTINGS = Settings()
