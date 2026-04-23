"""
임베딩(Embeddings) 모듈.

이 파일은 "텍스트 → 숫자 벡터(float 배열)" 변환을 담당한다.
즉, 문장을 의미 공간상의 좌표로 바꿔주는 역할이다.
(벡터 DB 에 질문이나 문서를 저장/검색할 때 이 벡터가 사용된다.)

제공 기능:
    - get_embedding_model(): OpenAIEmbeddings 객체를 싱글톤으로 반환
    - embed_query(text):     한 개의 질의 문자열을 벡터로 변환
    - embed_documents(list): 여러 개의 문서 문자열을 벡터 리스트로 변환

전체 파이프라인 속 위치:
    사용자 질문 → (router 판단) → 임베딩 경로로 가면 이 모듈이 호출되어
    질문/문서를 벡터로 바꾼다. 바뀐 벡터는 DB 유사도 검색 등에 이용된다.
"""

from typing import List
from langchain_openai import OpenAIEmbeddings
from .config import SETTINGS


# ---------------------------------------------------------------------------
# 모듈 전역 캐시 변수.
#   - 임베딩 모델 객체를 매번 새로 만들지 않고 재사용하기 위한 싱글톤 자리.
# ---------------------------------------------------------------------------
_embedding_model: OpenAIEmbeddings | None = None


def get_embedding_model() -> OpenAIEmbeddings:
    """
    OpenAI 임베딩 모델(OpenAIEmbeddings)을 싱글톤으로 반환한다.

    Returns:
        OpenAIEmbeddings: 텍스트를 벡터로 바꿔줄 수 있는 모델 객체

    전체 흐름 속 위치:
        embed_query / embed_documents 함수가 실제 임베딩을 만들기 직전에
        이 함수를 호출하여 모델 객체를 확보한다.
    """
    # 모듈 전역에 있는 _embedding_model 을 고치기 위해 global 선언.
    global _embedding_model

    # 아직 모델이 만들어지지 않았을 때만 생성 (이후에는 재사용).
    if _embedding_model is None:
        # API Key 가 비어 있으면 호출 자체가 불가능하므로 즉시 실패.
        if not SETTINGS.openai_api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되어 있지 않습니다.")

        # LangChain 의 OpenAIEmbeddings 래퍼 생성.
        #   - model: text-embedding-3-small 등 설정된 모델명
        #   - api_key: OpenAI 키
        _embedding_model = OpenAIEmbeddings(
            model=SETTINGS.embedding_model,
            api_key=SETTINGS.openai_api_key,
        )

    # 준비된 모델 객체 반환.
    return _embedding_model


def embed_query(text: str) -> List[float]:
    """
    한 문장의 질의(query) 텍스트를 하나의 벡터로 변환한다.

    Args:
        text: 임베딩하고 싶은 단일 문자열 (예: 사용자의 질문)

    Returns:
        List[float]: 임베딩 결과 벡터 (모델에 따라 길이가 다름)

    전체 흐름 속 위치:
        질문/쿼리를 벡터 DB 에서 유사도로 검색하기 전 단계에서 호출된다.
    """
    # 문자열의 앞뒤 공백 제거. None 이 들어와도 안전하게 처리하기 위해 or "" 사용.
    text = (text or "").strip()
    # 빈 문자열은 임베딩할 수 없으므로 즉시 에러 → 잘못된 데이터가 흘러가는 것을 차단.
    if not text:
        raise ValueError("임베딩할 query가 비어 있습니다.")

    # 싱글톤 임베딩 모델 가져오기.
    model = get_embedding_model()
    # ---------------------------------------------------------------
    # 실제 LLM(임베딩) 호출 지점!
    # model.embed_query 가 내부적으로 OpenAI 임베딩 API 를 때린다.
    # ---------------------------------------------------------------
    return model.embed_query(text)  # 함수명과 무관. 모델한테 임베딩 해달라고 시키는 것.(model 객체의 메서드 호출)


def embed_documents(texts: list[str]) -> list[list[float]]:
    """
    여러 문서(텍스트) 를 한 번에 임베딩해 벡터 리스트를 반환한다.

    Args:
        texts: 임베딩할 여러 문자열이 담긴 리스트

    Returns:
        list[list[float]]: 각 입력 문자열에 대응하는 벡터들의 리스트

    전체 흐름 속 위치:
        대량의 식당/리뷰 문서를 한꺼번에 벡터 DB 로 올릴 때 사용한다.
        (예: 데이터 적재 스크립트에서 활용)
    """
    # 리스트 안의 각 문자열을 안전하게 strip. None 이 섞여 있어도 "" 로 치환.
    clean_texts = [(t or "").strip() for t in texts]
    # 비어 있으면 호출 자체를 생략하고 빈 리스트 반환 → 불필요한 API 비용 방지.
    if not clean_texts:
        return []

    # 싱글톤 모델 로드.
    model = get_embedding_model()
    # ---------------------------------------------------------------
    # 실제 LLM(임베딩) 호출 지점! (여러 문서를 한 번에 보냄)
    # ---------------------------------------------------------------
    return model.embed_documents(clean_texts)  # 여러 문장을 한번에 모델에 넣고 각각의 벡터를 리스트로 받음
