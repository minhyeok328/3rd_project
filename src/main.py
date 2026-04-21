# main.py
from test_mockupdata import restaurant_list
from src.pipeline import run_qa


def main():
    while True:
        question = input("질문 > ").strip()

        if not question:
            break

        # 실제로는 커넥터가 이 구조를 반환한다고 가정
        connector_response = {
            "restaurant_list": restaurant_list,
            "search_mode": "embedding",
            "candidate_count": len(restaurant_list),
        }

        result = run_qa(
            question=question,
            connector_response=connector_response,
            session_id="default",
        )

        print(result["answer"])


if __name__ == "__main__":
    main()