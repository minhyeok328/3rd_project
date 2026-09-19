# 데이터 흐름

[문서 목록](../README.md)

## 수집과 정제

| 단계 | 입력·처리 | 소스 |
| --- | --- | --- |
| 링크 추출 | 저장한 검색 HTML에서 식당 링크 추출 | [0_page_search_parser.py](../../database/raw/0_page_search_parser.py) |
| 동적 수집 | 식당별 상세·메뉴·리뷰 HTML 저장 | [1_dynamic_crawling.ipynb](../../database/raw/1_dynamic_crawling.ipynb) |
| 구조화 | HTML에서 식당·메뉴·리뷰 CSV 생성 | [1_html_to_csv.ipynb](../../database/processed/1_html_to_csv.ipynb) |
| 정제 | 결측·타입·태그와 카테고리 정리 | [2_csv_preprocesse.ipynb](../../database/processed/2_csv_preprocesse.ipynb) |
| 좌표 보강 | 주소 기반 좌표 추가 | [3_restaurant_df_long_lat.ipynb](../../database/processed/3_restaurant_df_long_lat.ipynb) |
| 관계 분리 | 식당·리뷰·태그 관계 CSV 구성 | [4_database_draft.ipynb](../../database/processed/4_database_draft.ipynb), [5_database_final.ipynb](../../database/processed/5_database_final.ipynb) |

## DB 재구축 경계

[db_setup.ipynb](../../database/sql/db_setup.ipynb)는 SQLite 스키마와 CSV 적재 코드를 포함합니다. 임베딩 노트북은 category/food/menu/tag/review의 설명·벡터를 준비하고, 최종 CSV/DB에 연결하는 실험 자료입니다.

- 실행 디렉터리에 따라 `restaurant.db` 출력 위치가 달라집니다. 런타임 경로는 `database/sql/restaurant.db`로 맞춥니다.
- 수집·정제 CSV의 컬럼명과 DB 스키마가 다릅니다. `category_name→name`, `rv_cnt→review_cnt` 및 관계 파일명 매핑을 확인합니다.
- `food`, `food_code`, 설명·임베딩은 추가 가공 결과에 의존합니다. 테이블별 원본 CSV만 적재하면 검색용 완성 DB가 되지 않습니다.
- 노트북의 `append` 적재를 기존 DB에 반복하면 중복 또는 기본키 충돌이 생길 수 있습니다. 출력 DB를 명확히 구분합니다.
- 절대 경로와 누락된 중간 파일이 있으므로 재구축은 수동 검토가 필요한 절차입니다. [build_index.py](../../scripts/build_index.py)는 이를 자동 실행하지 않습니다.

## 실행 중 질의 처리

1. `route_node`가 질문을 `embedding` 또는 `fixed`로 분류합니다.
2. 해당 슬롯 추출기가 JSON Schema에 맞는 문자열 필드를 반환합니다.
3. `fixed`는 이름 `LIKE` 조회 후 연결된 식당 코드를 합칩니다.
4. `embedding`은 비어 있지 않은 슬롯마다 유사도 상위 8개 코드를 찾고 식당 코드로 변환합니다. 식당 코드가 한 건 이상 나온 슬롯 목록 수에 따른 제한을 적용해 후보를 모읍니다. 결과가 없는 슬롯은 이 개수에 포함하지 않습니다.
5. 상세 조인으로 메뉴·리뷰·태그·좌표를 포함한 식당 목록을 만듭니다.
6. `simple_retrieve_restaurants`가 키워드로 후보를 재정렬해 `TOP_K`개 이내를 생성기에 전달합니다.
7. 생성기는 후보와 대화 이력으로 응답을 만들고, UI는 답변과 사용 후보를 표시합니다.

현재 임베딩 후보 수집은 모든 슬롯의 교집합을 강제하지 않습니다. 생성 모델이 선택한 식당과 `used_restaurant_list`도 동일 개념이 아닙니다. 후자는 생성기에 제공한 후보 목록입니다.
