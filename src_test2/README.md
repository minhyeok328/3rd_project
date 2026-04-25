# src_test2 LLM 평가 가이드

이 폴더는 `src_test`와 같은 방식의 평가 자산을 별도로 복제해 둔 실험용 테스트 공간입니다.  
기준 데이터는 `database/sql/restaurant.db`이며, 이 폴더 안에서만 골드셋 생성과 평가를 돌릴 수 있습니다.

## 파일 구성

- `build_llm_goldset.py`
  - `restaurant.db`를 읽어 `fixed 20개 + embedding 30개`, 총 50개 케이스의 골드셋을 만듭니다.
- `llm_goldset.json`
  - 생성된 골드셋 파일입니다.
- `evaluate_llm.py`
  - `src.pipeline.run_qa(...)`를 호출해 평가를 수행합니다.
- `llm_eval_dashboard.ipynb`
  - 개발 환경에서 골드셋 생성, 평가 실행, 요약 표, 실패 케이스 표, HTML 리포트를 한 번에 확인하는 노트북입니다.
- `llm_eval_report.json`
  - 평가 결과 JSON 리포트입니다.
- `llm_eval_report.html`
  - 평가 결과 HTML 리포트입니다.

## 실행 방법

프로젝트 루트에서 실행합니다.

```powershell
python src_test2\build_llm_goldset.py
python src_test2\evaluate_llm.py
```

## 노트북으로 보기

아래 노트북을 열면 개발 환경에서 바로 볼 수 있습니다.

- `src_test2\llm_eval_dashboard.ipynb`

노트북 흐름:

- 경로/환경 확인
- 골드셋 재생성
- 골드셋 샘플 확인
- 평가 실행
- 전체 요약 표
- query type 요약 표
- 실패 케이스 표
- HTML 리포트 본문 보기

## 참고

- 실제 평가는 `OPENAI_API_KEY`가 설정되어 있어야 의미 있게 동작합니다.
- `restaurant.db`가 바뀌면 골드셋도 다시 생성하는 편이 좋습니다.
