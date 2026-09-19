# 디렉터리 구조

[문서 목록](../README.md)

```text
3rd_project/
├── main.py                      현재 웹 진입점
├── requirements.txt             패키지 하한 버전
├── src/
│   ├── config.py                환경변수와 프롬프트 경로
│   ├── pipeline.py              StateGraph, run_qa, CLI
│   ├── router.py                embedding/fixed 분류
│   ├── slot_extractor.py        JSON Schema 기반 조건 추출
│   ├── retriever.py             키워드 재정렬
│   ├── generator.py             스트리밍·생성·메모리 이력
│   ├── llm_client.py            슬롯 추출용 OpenAI 클라이언트
│   ├── embeddings.py            보조 임베딩 래퍼
│   └── prompts.py               라우터·슬롯 프롬프트
├── prompts/system_prompt.txt    최종 응답 규칙
├── database/
│   ├── raw/                     수집 HTML·크롤링 노트북
│   ├── processed/               전처리 노트북·중간 CSV
│   └── sql/                     스키마·임베딩 노트북·utils.py
├── experiments/frontend/        초기 화면 실험
├── api/server.py                주석만 있는 자리 파일
├── scripts/build_index.py       주석만 있는 자리 파일
├── evaluations/
│   ├── run_01/                  1차 평가 자산
│   ├── run_02/                  2차 평가 자산
│   └── run_03/                  3차 평가 자산
├── img/profile.png              리뷰 기본 이미지
└── docs/                        공통 목차와 개발 문서
```

실행에 필요한 `database/sql/restaurant.db`는 현재 파일 목록에 없으며 별도로 준비해야 합니다. `.env`도 개발 환경에서 작성합니다.

## 변경 위치 안내

| 바꾸려는 동작 | 먼저 볼 파일 |
| --- | --- |
| 화면·검색 모드·지도 | [main.py](../../main.py) |
| 분류·슬롯 필드 | [router.py](../../src/router.py), [slot_extractor.py](../../src/slot_extractor.py), [prompts.py](../../src/prompts.py) |
| 검색 후보 선정 | [utils.py](../../database/sql/utils.py), [retriever.py](../../src/retriever.py) |
| 생성 문체·근거 규칙 | [system_prompt.txt](../../prompts/system_prompt.txt), [generator.py](../../src/generator.py) |
| DB·CSV | [db_setup.ipynb](../../database/sql/db_setup.ipynb), [processed](../../database/processed) |
| 평가 기준 | [evaluate_llm.py](../../evaluations/run_03/evaluate_llm.py) |
