from typing import List, Dict

from .generate import generate_response

def run_qa(question: str) -> Dict[str, object]:
    answer = generate_response(question)
    return {
        "question": question,
        "answer": answer,
    }

def main() -> None:
    while True:
        print("\n[질문]")
        question = input(">").strip()
        if not question:
            print("종료합니다.")
            break

        result = run_qa(question)
        print("\n[답변]")
        print(result["answer"])

if __name__ == "__main__":
    main()