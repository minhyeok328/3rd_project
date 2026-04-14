# 모델명, 임베딩 설정, 벡터DB 경로 등 전역 설정을 로드하는 파일입니다.
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

@dataclass(frozen=True)
class Settings:

    # Model
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4.1-mini")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    prompt_path = Path("prompts/system_prompt.txt")
    
# 다른 파일에서는 SETTINGS 하나만 import해서 사용
SETTINGS = Settings()