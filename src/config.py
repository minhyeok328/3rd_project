from pathlib import Path
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

@dataclass(frozen=True)
class Settings:
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4.1-mini")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    fixed_search_model: str = os.getenv("FIXED_SEARCH_MODEL", "gpt-4o-mini")
    router_model: str = os.getenv("ROUTER_MODEL", "gpt-4.1-mini")

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    prompt_path: Path = BASE_DIR / "prompts" / "system_prompt.txt"
    data_path: Path = BASE_DIR / "data" / "restaurants.csv"

    top_k: int = int(os.getenv("TOP_K", "5"))

SETTINGS = Settings()