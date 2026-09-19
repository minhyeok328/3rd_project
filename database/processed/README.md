# 전처리 자료

수집 HTML에서 추출한 식당·메뉴·리뷰를 CSV로 정리하고 관계 테이블로 분리하는 노트북과 중간 산출물입니다.

| 경로 | 내용 |
| --- | --- |
| `db_csv/` | HTML에서 추출한 식당·메뉴·리뷰 |
| `db_csv_preprocessed/` | 정제 자료와 좌표 보강 결과 |
| `db_csv_cat_tag/` | 카테고리·태그 분리 자료 |
| `db_csv_tablewise/` | 엔티티·관계 테이블별 CSV |

노트북 흐름은 HTML 구조화 → 정제 → 좌표 → 관계 분리입니다. 이 파일들은 최종 임베딩 DB와 같지 않습니다. DB 컬럼명 매핑, food·설명·임베딩 보강과 관계 검증을 완료해야 런타임에서 사용할 수 있습니다.

[데이터 흐름](../../docs/02-architecture/data-flow.md) · [스키마와 CSV 규모](../../docs/05-database/schema-and-erd.md) · [문서 목록](../../docs/README.md)
