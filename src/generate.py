from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage

from typing import List, Dict

from .config import SETTINGS

def load_prompt_template() -> str:
    if not SETTINGS.prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {SETTINGS.prompt_path}")
    return SETTINGS.prompt_path.read_text(encoding='utf-8')

_SESSION_MESSAGES: dict[str, list[BaseMessage]] = {}

def clear_session(session_id: str) -> None:
    _SESSION_MESSAGES.pop(session_id, None)

# def build_context(chunks: List[Dict[str, str]]) -> str:
#     if not chunks:
#         return "관련 문맥 없음"
#     return "\n\n".join(
#         f"[{i+1}] {chunk.get('text', '')}" for i, chunk in enumerate(chunks)
#     )

_llm_chain = None

def get_llm_chain():
    global _llm_chain
    if _llm_chain is None:
        llm = ChatOpenAI(model=SETTINGS.llm_model, temperature=0)
        _llm_chain = llm | StrOutputParser()
    return _llm_chain

def generate_response(question: str, session_id: str = "default") -> str:
    prompt_rules = load_prompt_template()
    # context = build_context(chunks)
    # if context == "관련 문맥 없음":
    #     return "해당 자료 기준으로는 확인되지 않습니다."

    history = _SESSION_MESSAGES.setdefault(session_id, [])

    # prompt = f"{prompt_rules}\n\n[Context]\n{context}\n\n[Question]\n{question}"
    prompt = f"{prompt_rules}\n\n[Question]\n{question}"

    messages: list[BaseMessage] = [
        SystemMessage(content=prompt),
        *history,
        HumanMessage(content=question),
    ]

    chain = get_llm_chain()
    response = chain.invoke(messages)
    
    history.append(HumanMessage(content=question))
    history.append(AIMessage(content=response))

    return response
