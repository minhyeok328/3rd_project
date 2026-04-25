# src_test LLM 평가 가이드

이 폴더는 `database/sql/restaurant.db`를 기준으로 LLM 평가용 골드셋과 평가 코드를 관리합니다.  
다른 폴더의 코드나 구조를 건드리지 않고, `src_test` 안에서만 골드셋 생성과 평가가 가능하도록 구성했습니다.

## 파일 구성

- `build_llm_goldset.py`
  - `database/sql/restaurant.db`를 읽어 평가용 골드셋을 생성합니다.
  - 기본적으로 `fixed` 20개, `embedding` 30개, 총 50개 케이스를 만듭니다.
- `llm_goldset.json`
  - DB 기준으로 생성된 실제 평가셋입니다.
- `evaluate_llm.py`
  - `src.pipeline.run_qa(...)`를 실행해 골드셋과 비교하고 리포트를 만듭니다.
- `llm_eval_dashboard.ipynb`
  - 개발 환경에서 골드셋 생성, 평가 실행, 요약 표, 실패 케이스 표, HTML 리포트를 한 번에 볼 수 있는 노트북입니다.
- `llm_eval_report.json`
  - 평가 결과 원본 JSON 리포트입니다.
- `llm_eval_report.html`
  - 평가 결과를 보기 쉽게 정리한 HTML 리포트입니다.

## 골드셋 생성

`restaurant.db`가 바뀌었거나 골드셋을 다시 만들고 싶을 때:

```powershell
python src_test\build_llm_goldset.py
```

이 스크립트는 실제 DB의 식당명, 카테고리, 태그, 메뉴를 읽어서 질문과 기대 조건을 자동으로 구성합니다.

## 평가 실행

```powershell
python src_test\evaluate_llm.py
```

실행하면 아래 파일이 같이 갱신됩니다.

- JSON 리포트: `src_test\llm_eval_report.json`
- HTML 리포트: `src_test\llm_eval_report.html`

## 노트북으로 보기

개발 환경에서 표 형태로 바로 확인하려면 아래 노트북을 사용하면 됩니다.

- `src_test\llm_eval_dashboard.ipynb`

노트북에서는 아래 흐름으로 확인할 수 있습니다.

- 골드셋 재생성
- 평가 실행
- 전체 요약 표
- query type 요약 표
- 실패 케이스 표
- HTML 리포트 본문 그대로 보기

특정 케이스만 실행할 수도 있습니다.

```powershell
python src_test\evaluate_llm.py --case fixed_001_hours
python src_test\evaluate_llm.py --case embedding_001 --case embedding_002
```

## 평가 기준

현재 평가는 아래 항목을 봅니다.

- `route` 일치 여부
- `payload` 안에 기대 키워드가 잡혔는지
- 실제 검색 결과에 목표 식당이 포함됐는지
- 답변에 기본 키워드가 포함됐는지
- 최소 추천 식당 수를 만족하는지

가중치는 아래처럼 적용됩니다.

- `route`: 30%
- `payload`: 25%
- `target hit`: 25%
- `answer`: 10%
- `retrieval`: 10%

## 리포트 해석

콘솔에서는 아래 순서로 보입니다.

- 전체 요약
- `fixed` / `embedding` 타입별 요약
- 실패 케이스 표
- 점수가 낮은 케이스 표

HTML 리포트에서는 같은 내용을 더 읽기 쉽게 볼 수 있습니다.

## 주의사항

- 실제 평가는 OpenAI API 키와 현재 검색/DB 파이프라인이 정상 동작해야 의미 있는 결과가 나옵니다.
- 골드셋은 `restaurant.db` 실데이터를 기준으로 만들어지므로, DB가 바뀌면 `build_llm_goldset.py`를 다시 실행하는 편이 좋습니다.
