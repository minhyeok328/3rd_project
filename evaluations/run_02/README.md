# 2차 LLM 평가 자산

동일한 50문항 골드셋으로 저장한 평가 자료입니다. 이 디렉터리는 당시 파이프라인 코드 전체를 보관한 독립 실행 버전이 아닙니다. 평가 스크립트는 현재 `src.pipeline.run_qa`를 불러옵니다.

## 파일 구성

| 파일 | 내용 |
| --- | --- |
| [build_llm_goldset.py](build_llm_goldset.py) | DB에서 골드셋 생성 |
| [llm_goldset.json](llm_goldset.json) | fixed 20개 + embedding 30개 기준 질문 |
| [evaluate_llm.py](evaluate_llm.py) | 경로·슬롯·후보·답변 문자열·후보 수 검사 |
| [llm_eval_report.json](llm_eval_report.json) | 저장된 평가 결과 |
| [llm_eval_report.html](llm_eval_report.html) | 저장된 결과의 HTML 보기 |
| [llm_eval_dashboard.ipynb](llm_eval_dashboard.ipynb) | 실험 실행·결과 탐색 노트북 |

## 실행 조건

최종 `database/sql/restaurant.db`, Python 의존성, `OPENAI_API_KEY`가 필요합니다. 현재 체크아웃에는 DB가 없습니다. 평가 실행에는 외부 모델 호출이 발생합니다.

프로젝트 루트에서 새 결과를 별도 경로로 저장합니다.

```powershell
New-Item -ItemType Directory -Force .local-evaluation
python evaluations/run_02/evaluate_llm.py --output .local-evaluation/run_02.json --html-output .local-evaluation/run_02.html
```

실패 케이스가 있으면 종료 코드는 1입니다. 골드셋 생성 스크립트의 기본 출력은 기존 골드셋을 덮어쓰므로, 과거 비교 자료를 보관한 후 새 DB 기준으로 재생성합니다.

## 결과 해석

통과율은 다섯 검사를 모두 통과한 문항의 비율입니다. 후보 포함 검사와 답변 문자열 검사는 최종 추천의 정확도나 전체 사실성 검증과 다릅니다.

[공통 평가 방법·3개 결과 비교·한계](../../docs/10-quality/verification-and-limitations.md) · [개발 환경](../../docs/01-getting-started/development-environment.md) · [문서 목록](../../docs/README.md)
