from typing import List

from langchain_openai import OpenAIEmbeddings

from .config import SETTINGS

_embedding_model: OpenAIEmbeddings | None = None


def get_embedding_model() -> OpenAIEmbeddings:
    global _embedding_model

    if _embedding_model is None:
        if not SETTINGS.openai_api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되어 있지 않습니다.")

        _embedding_model = OpenAIEmbeddings(
            model=SETTINGS.embedding_model,
            api_key=SETTINGS.openai_api_key,
        )

    return _embedding_model


def embed_query(text: str) -> List[float]:
    text = (text or "").strip()
    if not text:
        raise ValueError("임베딩할 query가 비어 있습니다.")

    model = get_embedding_model()
    return model.embed_query(text)  # 함수명과 무관. 모델한테 임베딩 해달라고 시키는 것.(model 객체의 메서드 호출)


def embed_documents(texts: list[str]) -> list[list[float]]:
    clean_texts = [(t or "").strip() for t in texts]
    if not clean_texts:
        return []

    model = get_embedding_model()
    return model.embed_documents(clean_texts)  # 여러 문장을 한번에 모델에 넣고 각각의 벡터를 리스트로 받음