"""
src 패키지 초기화 파일.

이 파일이 존재함으로써 파이썬은 `src/` 폴더를 "패키지(모듈 묶음)" 로 인식한다.
덕분에 다른 곳에서 아래처럼 import 할 수 있게 된다:

    from src.pipeline import run_qa
    from src.config import SETTINGS

별도의 공개 심볼을 여기서 직접 export 하지는 않고,
각 서브모듈(config, llm_client, embeddings, prompts, router,
retriever, slot_extractor, generator, pipeline)을 필요할 때 개별 import 한다.
"""
# src 패키지를 Python 모듈로 인식시키는 초기화 파일입니다.
