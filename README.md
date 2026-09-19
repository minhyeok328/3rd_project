# PICKLE

신대방삼거리 식당 데이터를 검색하고, 자연어 질문에 맞는 식당을 추천하는 Streamlit 애플리케이션입니다.

## 프로젝트 소개

PICKLE은 식당·메뉴·리뷰·태그를 연결한 데이터에서 사용자가 원하는 장소를 찾습니다. 이름을 알고 있을 때는 직접 검색하고, 음식이나 분위기만 정해져 있을 때는 LangGraph 기반 RAG 파이프라인으로 후보와 추천 이유를 확인할 수 있습니다.

식당 정보는 수집된 데이터의 스냅샷입니다. 실시간 영업 여부나 최신 가격을 보장하지 않으며, 생성된 답변은 검색 결과와 함께 확인해야 합니다. 실행에는 별도로 준비한 SQLite DB와 OpenAI API 설정이 필요합니다.

## 주요 기능

| 기능 | 설명 |
| --- | --- |
| 자연어 추천 | 질문 의도를 분류하고 음식·분위기·리뷰 조건을 추출해 후보 식당을 검색합니다. |
| 직접 검색 | 식당명·메뉴명·리뷰 작성자명으로 연결된 식당을 찾습니다. |
| 근거 기반 답변 | 검색한 식당의 메뉴·태그·리뷰를 문맥으로 전달해 한 곳의 추천 이유를 생성합니다. |
| 상세 정보 | 식당의 주소, 수집 당시 영업시간, 메뉴 가격과 리뷰를 보여줍니다. |
| 지도 | Kakao Maps에 후보와 선택한 식당의 위치를 표시합니다. |
| 스트리밍 대화 | 답변을 점진적으로 표시하고 대화 이력을 프로세스 메모리에 보관합니다. |

## 사용 흐름

1. 검색 모드에서 식당·메뉴·작성자 이름을 입력하거나, 채팅 모드에서 원하는 조건을 질문합니다.
2. 검색 결과 카드와 지도에서 후보를 확인합니다.
3. 카드를 열어 메뉴·리뷰·주소를 비교합니다.
4. 채팅에서는 검색 결과를 바탕으로 생성한 추천 이유를 함께 확인합니다.

현재 화면의 대화 식별자는 고정값이므로 여러 사용자가 공유하는 서비스로 운영하려면 세션 분리 작업이 필요합니다.

## 기술 구성

| 구분 | 기술과 사용 목적 |
| --- | --- |
| 애플리케이션 | Python, Streamlit — 검색·채팅·상세 화면 |
| 질의 처리 | LangGraph, LangChain — 라우팅·슬롯 추출·검색·생성 연결 |
| 생성·임베딩 | OpenAI 모델 — 구조화된 슬롯 추출, 답변 생성, 텍스트 임베딩 |
| 저장·검색 | SQLite, NumPy, scikit-learn — 관계 조회와 코사인 유사도 검색 |
| 데이터 준비 | pandas, BeautifulSoup, Selenium, Jupyter Notebook |
| 지도 | Kakao Maps JavaScript SDK |

외부 HTTP API 서버는 구현되어 있지 않으며, 화면에서 Python 함수를 직접 호출합니다.

## 프로젝트 구조

```text
main.py                 Streamlit 메인 애플리케이션
src/                    질의 라우팅·슬롯 추출·RAG 파이프라인
prompts/                답변 생성 규칙
database/               수집 자료·전처리 CSV·DB 구축 노트북·검색 함수
experiments/frontend/   초기 화면 실험 파일
evaluations/            평가 스크립트·골드셋·저장된 리포트
docs/                   개발 문서
```

## 문서 안내

- [전체 문서와 읽는 순서](docs/README.md)
- [개발 환경과 데이터 준비](docs/01-getting-started/development-environment.md)
- [실행 및 문제 해결](docs/01-getting-started/run-and-operations.md)
- [시스템 구조](docs/02-architecture/system-architecture.md)
- [Python 인터페이스](docs/06-api/api-reference.md)
- [평가 방법과 알려진 한계](docs/10-quality/verification-and-limitations.md)

소스 코드 라이선스는 [LICENSE](LICENSE)를 따릅니다. 수집 데이터와 외부 이미지의 이용 범위는 코드 라이선스와 별도로 확인해야 합니다.

## 원본 저장소

[SKN26-3rd-3rd/3rd_project](https://github.com/SKN26-3rd-3rd/3rd_project)
