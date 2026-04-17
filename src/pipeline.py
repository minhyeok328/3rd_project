from typing import List, Dict

from .generate import generate_response

def run_qa(question: str) -> Dict[str, object]:
    # 전달받은 질문을 LLM 응답 생성 함수에 넘겨 답변을 생성한다.
    answer = generate_response(question)
    # 원본 질문과 생성된 답변을 하나의 딕셔너리 형태로 반환한다.
    return {
        "question": question,
        "answer": answer,
    }

def main() -> None:
    # 사용자가 빈 입력을 줄 때까지 질문/답변 루프를 반복한다.
    while True:
        # 질문 입력 구간 시작을 콘솔에 표시한다.
        print("\n[질문]")
        # 사용자 입력을 받고 앞뒤 공백을 제거한다.
        question = input(">").strip()
        # 입력이 비어 있으면 종료 메시지를 출력하고 루프를 끝낸다.
        if not question:
            print("종료합니다.")
            break

        # 질문 처리 파이프라인을 실행해 결과를 얻는다.
        result = run_qa(question)
        # 답변 출력 구간 시작을 콘솔에 표시한다.
        print("\n[답변]")
        # 결과 딕셔너리에서 답변 텍스트를 꺼내 출력한다.
        print(result["answer"])

if __name__ == "__main__":
    # 이 파일이 직접 실행될 때만 main 함수를 시작한다.
    main()