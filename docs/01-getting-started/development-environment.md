# 개발 환경

[문서 목록](../README.md)

## 사전 조건

- Python 3.10 이상: 검색 유틸에서 `match` 문법을 사용합니다.
- [requirements.txt](../../requirements.txt)의 Python 패키지
- OpenAI API에 접근할 수 있는 환경과 `OPENAI_API_KEY`
- `database/sql/restaurant.db`: 스키마·관계·임베딩을 갖춘 별도 준비 DB
- 지도 사용 시 `KAKAO_MAP_KEY`와 해당 실행 주소의 Kakao 웹 도메인 설정

이 체크아웃에는 최종 DB가 없고 [.gitignore](../../.gitignore)에서도 `*.db`를 제외합니다. 아래 패키지 설치만으로 추천 기능이 실행 가능한 상태가 되지는 않습니다.

## 설치

원본 저장소를 새로 받을 때:

```powershell
git clone https://github.com/SKN26-3rd-3rd/3rd_project.git
cd 3rd_project
```

이미 체크아웃한 경우 해당 프로젝트 루트에서 시작합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS/Linux에서는 가상환경 활성화 명령을 `source .venv/bin/activate`로 바꿉니다. 의존성은 하한 버전만 선언되어 있고 잠금 파일이 없어, 설치 시점에 따라 조합이 달라질 수 있습니다.

## 환경변수

루트 `.env` 또는 프로세스 환경에 설정합니다. 비밀키 값은 저장소에 기록하지 않습니다.

| 변수 | 코드 기본값·용도 |
| --- | --- |
| `OPENAI_API_KEY` | 필수. 라우팅·슬롯·생성·임베딩 호출 |
| `KAKAO_MAP_KEY` | 지도 SDK용 JavaScript 키. 없으면 지도 영역에 안내 표시 |
| `LLM_MODEL` | `gpt-4.1-mini`, 답변 생성 |
| `ROUTER_MODEL` | `gpt-4.1-mini`, 경로 분류 |
| `FIXED_SEARCH_MODEL` | `gpt-4o-mini`, 두 경로의 슬롯 추출 |
| `TOP_K` | `5`, 생성기에 전달할 재정렬 후보 상한 |
| `EMBEDDING_MODEL` | `text-embedding-3-small`, 보조 래퍼 설정 |

설정 근거는 [src/config.py](../../src/config.py)입니다. 실제 DB 검색의 [get_embedding](../../database/sql/utils.py)은 모델명을 `text-embedding-3-small`로 고정하므로 `EMBEDDING_MODEL`만 변경해도 이 검색 경로는 바뀌지 않습니다.

검색 유틸은 import 때 `OpenAI()`를 만듭니다. 직접 SQL 검색만 확인하더라도 키가 없으면 화면 시작 전에 실패할 수 있습니다.

## DB 준비

1. 완성된 DB를 별도로 확보하거나 [데이터 흐름](../02-architecture/data-flow.md)의 노트북을 검토해 재구축합니다.
2. 파일을 프로젝트의 `database/sql/restaurant.db`에 둡니다.
3. [스키마](../05-database/schema-and-erd.md)의 10개 테이블과 조회 컬럼을 확인합니다.
4. `category`, `food`, `menu`, `tag`, `review`의 임베딩이 검색 모델과 같은 차원·형식인지 확인합니다.

재구축 노트북에는 개별 환경의 절대 경로, 중간 CSV 의존성, 외부 API 호출이 남아 있습니다. 실행 전 입력/출력 경로와 적재 순서를 조정해야 하며, 위에서 아래로 모두 실행하는 자동 설치 과정으로 간주하지 않습니다. 특히 최종 `food` 및 임베딩 CSV 전체가 포함된 것은 아닙니다.

DB 준비 후 [실행과 운영](run-and-operations.md)으로 진행합니다.
