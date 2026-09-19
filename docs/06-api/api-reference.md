# Python 인터페이스

[문서 목록](../README.md)

이 프로젝트에는 구현된 HTTP API가 없습니다. [api/server.py](../../api/server.py)는 주석만 있으므로 URL·HTTP 상태 코드·REST 인증 계약을 제공하지 않습니다.

## run_qa

소스: [src/pipeline.py](../../src/pipeline.py)

```python
run_qa(question: str, session_id: str = "default",
       stream: bool = False, stream_callback=None) -> dict
```

| 입력 | 의미 |
| --- | --- |
| question | 자연어 질문 |
| session_id | 생성기 메모리 이력 키. 호출자가 고유성과 수명을 관리 |
| stream | True이면 토큰 조각을 받아 누적 문자열로 처리 |
| stream_callback | 현재까지의 전체 답변 문자열을 받는 함수 |

| 반환 키 | 형태·의미 |
| --- | --- |
| question | 원본 질문 문자열 |
| route | embedding 또는 fixed |
| route_payload | 경로별 문자열 슬롯 사전 |
| restaurant_list | DB가 반환한 식당 후보 리스트 |
| used_restaurant_list | 재정렬 후 생성기에 전달한 후보 리스트 |
| answer | 생성된 답변 문자열 |

사용 예시는 프로젝트 환경·DB 준비 후 실행합니다.

```python
from src.pipeline import run_qa

result = run_qa(
    question="혼밥하기 좋은 초밥집을 찾아줘",
    session_id="local-example-1",
)
print(result["answer"])
```

콜백에는 새 토큰만이 아니라 누적 문자열이 전달됩니다. `stream=True`이고 콜백이 없으면 콘솔에 출력합니다. 모델·DB·JSON 처리 예외가 호출자에게 전파될 수 있습니다.

## 검색 함수

소스: [database/sql/utils.py](../../database/sql/utils.py)

| 함수 | 입력 | 결과 |
| --- | --- | --- |
| `db_fixed_search(indict, db_path=DB_PATH)` | restaurant/menu/user 세 키가 있는 문자열 사전 | 상세 식당 리스트 |
| `db_embedding_search(indict)` | category/tag/menu/food/review 다섯 키의 문자열 사전 | 상세 식당 리스트 |
| `get_detailed_restaurants(code_list)` | 식당 코드 문자열 또는 리스트 | 메뉴·리뷰·태그를 포함한 식당 리스트 |
| `search_embedding(table_name, query_text, top_n=5)` | 호출자가 제한한 내부 테이블명과 검색 텍스트 | 유사한 엔티티 코드 리스트 |

`search_embedding`은 테이블명을 SQL에 직접 넣으며 자체 허용 목록 검증이 없습니다. 내부 호출처럼 category/tag/menu/food/review 중에서 호출자가 제한하고, 외부 입력을 테이블명으로 직접 전달하지 않습니다.

검색하지 않는 슬롯도 빈 문자열로 포함합니다. 고정 검색 예:

```python
from database.sql.utils import db_fixed_search

restaurants = db_fixed_search({
    "restaurant": "검색할 이름", "menu": "", "user": "",
})
```

`db_path` 인자는 고정 검색의 첫 이름 조회에만 전달되고 후속 관계·상세 조회는 기본 DB를 사용합니다. 임의 DB를 완전히 전환하는 인터페이스로 사용하지 않습니다.

## 대화 초기화

[generator.clear_session(session_id)](../../src/generator.py)은 해당 키의 모델 이력을 제거합니다. 화면의 `st.session_state`까지 지우지는 않습니다. 인증·세션 분리는 [배포 제약](../09-deployment/deployment.md)을 참고합니다.
