from __future__ import annotations

from typing import Any, Dict, List

from langchain_core.tools import tool

from .embedding_service import embedding_service


@tool("embedding_slot_extract")
def embedding_slot_extract(instr: str) -> Dict[str, str]:
    """
    사용자 입력을 restaurant/menu/user 슬롯 구조로 1차 반환한다.

    Returns:
        {"restaurant": "...", "menu": "...", "user": "..."}
    """
    return embedding_service.extract_slots(instr)

# 1차 구조 테스트 용
if __name__=="__main__":
    test_input = "초밥천사 집에 우동 팔아?"

    result = embedding_slot_extract.invoke(test_input)

    print("결과:", result)
    print("전체 타입: ", type(result))


