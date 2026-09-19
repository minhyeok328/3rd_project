# 백엔드 처리 모듈

[문서 목록](../README.md)

독립 HTTP 백엔드는 없습니다. Streamlit과 같은 프로세스의 Python 모듈이 질의를 처리합니다.

## 모듈 책임

| 모듈 | 공개 함수·책임 |
| --- | --- |
| [pipeline.py](../../src/pipeline.py) | `run_qa`, `build_graph`: 그래프 실행·상태 계약 |
| [router.py](../../src/router.py) | `decide_route`: LLM 응답에 `fixed`가 포함되면 fixed, 그 외 embedding |
| [slot_extractor.py](../../src/slot_extractor.py) | `embedding_slot_extract`, `fixed_search`: 구조화된 문자열 슬롯 |
| [utils.py](../../database/sql/utils.py) | DB/벡터 검색, 관계 이동, 식당 상세 구성 |
| [retriever.py](../../src/retriever.py) | `simple_retrieve_restaurants`: 키워드 후보 재정렬 |
| [generator.py](../../src/generator.py) | `generate_response`, `clear_session`: 생성과 메모리 대화 |

## 상태 계약

`GraphState`에 question/session_id, route/route_payload, restaurant_list, used_restaurant_list, answer, 스트리밍 옵션을 전달합니다. 검색 결과 정규화는 `None`, 리스트, `restaurant_list` 키를 가진 사전을 지원하고 다른 형식은 `ValueError`를 발생시킵니다.

`_graph`는 캐시되지만 요청 상태를 영속 저장하는 체크포인터는 구성되지 않았습니다. 대화는 생성 모듈의 전역 사전에 별도로 쌓입니다.

## 오류 처리

- 슬롯 JSON 오류·알 수 없는 슬롯 구조·비문자열 필드는 `ValueError`입니다.
- 슬롯 입력이 빈 문자열이면 키를 갖춘 빈 슬롯 사전을 반환합니다.
- DB 검색에 필수 슬롯 키가 없으면 빈 리스트를 반환합니다.
- `query_sender`는 SQL 조회 예외를 빈 DataFrame으로 바꾸므로 정상적인 검색 없음과 장애가 구분되지 않을 수 있습니다.
- 모델 호출 실패를 공통 오류 응답으로 변환하는 HTTP 계층이나 작업 재시도 큐는 없습니다.

직접 호출 계약은 [API 문서](../06-api/api-reference.md), 검색 세부 정책은 [AI·모델링](../07-ai-modeling/README.md)에 정리합니다.
