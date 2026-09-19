# 검증과 알려진 한계

[문서 목록](../README.md)

## 검증 자산과 범위

[evaluations/run_01](../../evaluations/run_01/README.md), [evaluations/run_02](../../evaluations/run_02/README.md), [evaluations/run_03](../../evaluations/run_03/README.md)에 평가 스크립트·골드셋·JSON/HTML 결과가 있습니다. 저장된 세 골드셋 파일은 내용 해시가 동일하며 fixed 20문항, embedding 30문항으로 구성됩니다.

각 평가 스크립트는 현재의 `src.pipeline.run_qa`를 import합니다. 폴더를 바꿔 실행한다고 당시 모델·프롬프트·검색 코드가 복원되지는 않습니다.

## 평가 기준

| 항목 | 실제 검사 | 점수 가중치 |
| --- | --- | ---: |
| route | 예상 경로와 일치 | 30% |
| payload | 지정 슬롯에 기대 문자열이 포함됨 | 25% |
| target | 원본 또는 사용 후보에 목표 코드·이름이 포함됨 | 25% |
| answer | 지정 문자열 포함/미포함 조건 | 10% |
| retrieval | 사용 후보 수가 설정된 최소치 이상 | 10% |

케이스 통과는 다섯 검사 모두 통과한 경우입니다. `target`은 최종 추천 정답률이 아니라 후보 포함 검사입니다. `answer` 100%도 문장 전체의 사실성·추천 적절성 검증을 뜻하지 않습니다.

## 저장된 평가 결과

근거: [1차 JSON](../../evaluations/run_01/llm_eval_report.json), [2차 JSON](../../evaluations/run_02/llm_eval_report.json), [3차 JSON](../../evaluations/run_03/llm_eval_report.json). 새로 실행한 결과가 아닙니다.

| 평가 자산 | 전체 통과 | 평균 가중 점수 | route | payload | target | answer | retrieval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| evaluations/run_01 | 23/50 (46%) | 0.8575 | 100% | 82% | 52% | 100% | 100% |
| evaluations/run_02 | 39/50 (78%) | 0.9625 | 100% | 86% | 92% | 100% | 100% |
| evaluations/run_03 | 41/50 (82%) | 0.9725 | 100% | 86% | 96% | 100% | 100% |

| 평가 자산 | embedding | fixed |
| --- | ---: | ---: |
| evaluations/run_01 | 4/30 | 19/20 |
| evaluations/run_02 | 19/30 | 20/20 |
| evaluations/run_03 | 22/30 | 19/20 |

마지막 리포트의 실패 9건은 payload 미충족 7건과 목표 후보 미포함 2건으로 기록되어 있습니다. 동일 골드셋에 대한 내부 평가이며, 다른 지역·신규 질문·실사용 환경으로 일반화하지 않습니다.

## 재평가

DB·API 키를 준비한 뒤 프로젝트 루트에서 실행합니다. 아래 경로로 출력하면 기존 리포트를 덮어쓰지 않습니다. 실제 외부 모델 호출이 발생합니다.

```powershell
New-Item -ItemType Directory -Force .local-evaluation
python evaluations/run_03/evaluate_llm.py --output .local-evaluation/result.json --html-output .local-evaluation/report.html
```

실패 케이스가 있으면 종료 코드가 1입니다. 환경 실패와 품질 실패는 리포트의 `preflight`, `environment_failure`, 개별 `error`를 나눠 읽습니다. 평가 산출물은 의도적으로 검토한 후에만 버전 관리에 포함합니다.

DB가 달라져 골드셋을 재생성하면 과거 결과와 같은 평가 조건이 아니게 됩니다. [build_llm_goldset.py](../../evaluations/run_03/build_llm_goldset.py)는 기본 골드셋을 덮어쓰므로 기존 기준을 보관한 뒤 실행합니다.

각 `llm_eval_dashboard.ipynb`는 프로젝트 루트 또는 해당 `evaluations/run_01`·`run_02`·`run_03` 폴더를 작업 디렉터리로 사용합니다. 노트북에 저장된 출력의 과거 경로는 실행 당시 기록이며, 현재 입력·출력 경로는 첫 번째 코드 셀에서 정합니다.

## 수동 검증

1. DB 테이블·컬럼·임베딩 차원과 연결 코드 검사
2. 이름·메뉴·작성자 검색의 결과와 상세 조인 확인
3. 음식/분위기 질문의 route·payload·후보·최종 답변 대조
4. 지도 키 누락, 검색 없음, DB 오류, 모델 오류 구분
5. 좁은 화면·긴 문장·결측 가격·좌표 없는 식당 표시
6. 서로 다른 브라우저 세션의 모델 이력 분리 여부 확인

## 현재 확인된 한계

- 최종 SQLite DB가 없어 이 체크아웃만으로 end-to-end 실행을 확인하지 못했습니다.
- 노트북의 절대 경로·중간 CSV·모델 의존성 때문에 자동 재구축을 보장하지 않습니다.
- 직접 검색/조회 오류가 빈 결과로 처리되는 경로가 있습니다.
- 임베딩 검색은 모든 조건을 동시에 충족시키는 필터가 아닙니다.
- 고정 웹 대화 ID, 이력 만료 부재, 라우터/슬롯의 이전 대화 미사용이 있습니다.
- 모델 출력의 근거 일치 여부를 자동 강제하는 검증 계층이 없습니다.

이번 문서 정리는 소스·설정·CSV 행 수·저장된 평가 JSON을 대조했습니다. 모델 평가·브라우저 실행·배포 검증을 새로 수행했다는 의미는 아닙니다.
