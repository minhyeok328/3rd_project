# PICKLE 🥒 — 신대방삼거리 맛집 추천 챗봇

> SKN26 3rd Project · LangGraph + RAG 기반 맛집 검색/추천 서비스

---

## 👥 Team
<table>
  <tr>
    <td align="center">
      <img src="https://tamagotchi-official.com/tamagotchi/jp/character/2024/05/08/X9QXrv0KcSLHIzUl/12_%E3%81%BF%E3%82%8B%E3%81%8F%E3%81%A3%E3%81%A1.png" width="110px;" /><br />
      <b>박기은</b><br />
    </td>
    <td align="center">
      <img src="https://i.namu.wiki/i/bpNfyV2EO3ktFabEh7y_2Mi6dC1jQwjb87Df6IwaWFWZF6l6dOjiaYwKhACtE5kJgZz5TEX6dA8M3IqdDkhpCsG2sO3rmQxFRwuTirPtzeN5P4BG_cG6Wnko6Ge30upzJddWYkC8qcVzR3Z3mEtScA.webp" width="110px;" /><br />
      <b>서민혁</b><br />
    </td>
    <td align="center">
      <img src="https://i.namu.wiki/i/iWqehAOlzWPA-xfifB92okVTnhJSFBj-k633W8aHxc-EW57srm7A5IXwVsJ4rgwPo1kPAoDz_cKjONSWQ3vwKb3GtRLQgFF7m3moHup98KtISftIgs96YS6viGFW_Wtu8eQB0DA4VxHuKbf3O-rzyA.webp" width="110px;" /><br />
      <b>유동현</b><br />
    </td>
    <td align="center">
      <img src="https://i.namu.wiki/i/wOGUauoibb0a2w-jLXvKhjd53tDQARKn_Z_vPzoTstH1AgoQXmtmwt_S6HgNwh7Dhso52_xjT8uEJnNnBe_yaA.webp" width="110px;" /><br />
      <b>윤정연</b><br />
    </td>
    <td align="center">
      <img src="https://i.namu.wiki/i/Va9_ASdKJ_Vd8Neo3gKw2p5D-gzePCcrJP25bg6QgE2w21yZuNAhLxGljLISe-d90WnWfEHsSRUNbeuwa0M5Pg.webp" width="110px;" /><br />
      <b>이레</b><br />
    </td>
    <td align="center">
      <img src="https://i.namu.wiki/i/bXkgQGQUNylk38qKKYmFFRkdfadMyH1ej-wEDI3syJX6JYDPlh0L3SFXGPEWvZOjuCFoUGKIWsiz9RB6jfPTpAdvByVnXaO6D3WZHYT7Y1O4VOBolw_3BvmkuBonu6s-hmiNThLrSrlQMb0S8UMoYg.webp" width="110px;" /><br />
      <b>정영일</b><br />
    </td>
  </tr>
  <tr>
    <td align="center"><b>Role</b><br>Data<br>Map API<br>Frontend</td>
    <td align="center"><b>Role</b><br>LLM<br>Frontend</td>
    <td align="center"><b>Role</b><br>Data<br>Streamlit</td>
    <td align="center"><b>Role</b><br>Data<br>Map API<br>Frontend</td>
    <td align="center"><b>Role</b><br>Data<br>LLM</td>
    <td align="center"><b>Role</b><br>Data<br>DataBase</td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/gieun-Park"><img src="https://img.shields.io/badge/gieun-Park-34495e?style=flat&logo=github&logoColor=white"></a></td>
    <td align="center"><a href="https://github.com/minhyeok328"><img src="https://img.shields.io/badge/minhyeok328-34495e?style=flat&logo=github&logoColor=white"></a></td>
    <td align="center"><a href="https://github.com/Ocean-2930"><img src="https://img.shields.io/badge/Ocean-2930-34495e?style=flat&logo=github&logoColor=white"></a></td>
    <td align="center"><a href="https://github.com/dimolto3"><img src="https://img.shields.io/badge/dimolto3-34495e?style=flat&logo=github&logoColor=white"></a></td>
    <td align="center"><a href="https://github.com/leere2424"><img src="https://img.shields.io/badge/leere2424-34495e?style=flat&logo=github&logoColor=white"></a></td>
    <td align="center"><a href="https://github.com/wjdduddlf112"><img src="https://img.shields.io/badge/wjdduddlf112-34495e?style=flat&logo=github&logoColor=white"></a></td>
  </tr>

</table>

---

## 1. Overview

### 1.1 소개
**PICKLE**은 신대방삼거리 지역의 식당 데이터를 기반으로, 사용자의 자연어 질의에 대해 **분위기·메뉴·가성비·상황** 조건을 반영한 식당 **1곳**을 추천하는 AI 맛집 챗봇입니다.

다이닝코드(diningcode.com)에서 수집한 식당 100곳, 메뉴 2,000여 개, 리뷰 400여 건을 **SQLite + 벡터 임베딩**으로 구축했으며, LangGraph 기반 파이프라인으로 **자연어 질문 → 라우팅 → 슬롯 추출 → DB 검색 → 근거 기반 답변 생성**을 수행합니다.

### 1.2 문제 정의
기존 맛집 검색 서비스는 다음과 같은 한계가 있습니다.

- **키워드 기반**: "조용한 데이트 하기 좋은 가성비 좋은 초밥집"처럼 복합 조건을 한 번에 걸러내기 어렵다.
- **신뢰도 부족**: 리뷰는 많지만 **사용자 질문과 리뷰 근거 사이의 연결**이 약하다.
- **환각(hallucination) 위험**: 순수 LLM에 맛집을 물으면 존재하지 않는 식당·메뉴·주소를 그럴듯하게 지어낸다.
- **좁지만 깊은 데이터 부족**: 한 지역의 식당들을 카테고리/태그/리뷰/메뉴까지 교차로 볼 수 있는 서비스가 많지 않다.

### 1.3 목표
- **데이터 기반 Grounded 추천**: LLM이 DB에 존재하는 식당·메뉴·리뷰만 근거로 응답하도록 시스템 프롬프트에서 제약합니다.
- **의도 기반 라우팅**: 분위기·조건 기반 질의(`embedding`)와 식당/메뉴/유저 직접 지정 질의(`fixed`)를 자동 분기합니다.
- **근거 인용 응답**: 추천 사유를 실제 리뷰 문장에서 인용하여 설명합니다.
- **지도 연동 UX**: 응답에 포함된 식당을 Kakao Map 마커로 시각화합니다.

---

## 2. Features

| 구분 | 기능 | 설명 |
|------|------|------|
| 💬 추천 챗봇 | 자연어 맛집 추천 | "신대방삼거리 혼밥 가성비 좋은 초밥집" 한 줄로 근거 있는 식당 1곳을 제시 |
| 🔀 자동 라우팅 | `embedding` / `fixed` 분기 | 조건 기반 탐색 vs 엔티티 직접 지정 검색을 LLM이 자동 판단 |
| 🧩 슬롯 추출 | JSON Schema 강제 출력 | `category / tag / menu / food / review` · `restaurant / menu / user` 구조로 질문을 분해 |
| 🧮 임베딩 검색 | 코사인 유사도 교집합 | 슬롯별 임베딩(category/tag/menu/food/review)으로 후보를 뽑고 교차시켜 의도가 겹치는 식당만 남김 |
| 🔎 엔티티 검색 | SQL LIKE + 관계 테이블 이동 | 식당명·메뉴명·유저명이 들어오면 중간 관계 테이블을 따라가 연관 식당을 복원 |
| 🧠 근거 기반 생성 | system prompt + RAG | 후보 dict 리스트를 그대로 LLM에 넘겨 "리스트 밖 정보 생성 금지" 제약으로 답변 생성 |
| 🗺️ Kakao 지도 | 마커 자동 렌더 | 검색/추천 결과 좌표를 지도에 실시간 표시, 중심 좌표 자동 재조정 |
| 🖼️ 식당 상세 카드 | 리뷰·메뉴 카드 | 평점·맛/가성비/서비스 레벨·태그·리뷰 원문·메뉴 가격을 카드 UI로 제공 |
| 🧵 세션 히스토리 | 대화 맥락 유지 | `session_id` 단위로 챗봇 대화를 이어갈 수 있음 |

---

## 3. Tech Stack

| 레이어 | 기술 |
|---|---|
| **Language** | Python 3.10+ |
| **LLM / Embedding** | OpenAI `gpt-4.1-mini`, `gpt-4o-mini`, `text-embedding-3-small` |
| **Orchestration** | LangChain, LangGraph |
| **Vector / Similarity** | NumPy, scikit-learn (`cosine_similarity`), base64 인코딩 임베딩 |
| **Database** | SQLite (`restaurant.db`) |
| **Frontend** | Streamlit, Kakao Maps JS SDK |
| **Data Pipeline** | BeautifulSoup, Selenium(동적 크롤링), Pandas |
| **Config** | python-dotenv |

---

## 4. Directory Structure

```
3rd_project/
├── main.py                       # Streamlit 진입점 (== frontend/app.py와 동일 구조)
├── frontend/
│   └── app.py                    # Streamlit UI: 채팅/검색 토글 + 지도 + 식당 상세
├── src/                          # RAG 파이프라인 본체
│   ├── config.py                 # 환경변수/모델명/프롬프트 경로 (Settings)
│   ├── llm_client.py             # OpenAI 클라이언트 싱글톤
│   ├── embeddings.py             # LangChain OpenAIEmbeddings 래퍼
│   ├── prompts.py                # ROUTER / SLOT / SYSTEM 프롬프트 상수
│   ├── router.py                 # 질문 → "embedding" | "fixed" 판정
│   ├── slot_extractor.py         # JSON Schema 강제로 슬롯 추출 (@tool 2종)
│   ├── retriever.py              # restaurant_list를 질문과의 키워드 매칭으로 top-k 재랭킹
│   ├── generator.py              # 시스템 프롬프트 + 후보 리스트 → 최종 답변 생성
│   └── pipeline.py               # LangGraph StateGraph 정의 + run_qa() + CLI
├── prompts/
│   └── system_prompt.txt         # 챗봇의 최종 선택/출력 규칙 (한국어, 대화체)
├── database/
│   ├── raw/                      # 크롤링 원본 · 파서
│   │   ├── 0_page_search_parser.py     # 검색 페이지 HTML → 식당 링크 리스트
│   │   ├── 1_dynamic_crawling.ipynb    # Selenium 기반 식당 상세/리뷰 동적 크롤링
│   │   ├── page_search.txt, page_sample.txt, link_restaurants.txt
│   │   └── restaurants/                # 개별 식당 HTML 덤프
│   ├── processed/                # 전처리·가공
│   │   ├── 1_html_to_csv.ipynb         # HTML → 구조화 CSV
│   │   ├── 2_csv_preprocesse.ipynb     # 결측/중복/타입 정리
│   │   ├── 3_restaurant_df_long_lat.ipynb  # 주소 → 위경도
│   │   ├── 4_database_draft.ipynb
│   │   ├── 5_database_final.ipynb
│   │   └── db_csv*/                    # 중간 산출 CSV 모음
│   └── sql/                      # SQLite 빌드 · 검색 유틸
│       ├── db_setup.ipynb              # 테이블 스키마 + CSV 적재
│       ├── embedding_*.ipynb           # category/food/menu/tag/review 임베딩 생성·저장
│       ├── restaurant.db               # 최종 SQLite (약 26MB)
│       └── utils.py                    # 임베딩 검색 · 고정 검색 · 상세 조인 로직
├── api/
│   └── server.py                 # (예정) 외부 서비스용 API 서버
├── scripts/
│   └── build_index.py            # (예정) 인덱스 빌드 실행 스크립트
├── img/profile.png               # 리뷰 카드용 기본 프로필
├── tests/                        # 실험 노트북 (llm_tool1.ipynb, test.ipynb)
├── requirements.txt
├── .env                          # OPENAI_API_KEY · KAKAO_MAP_KEY (git 제외)
├── LICENSE                       # MIT
└── README.md
```

---

## 5. Data Pipeline

### 5.1 수집
- **대상**: [diningcode.com](https://www.diningcode.com) "신대방삼거리" 검색 결과 상위 100개 식당
- **도구**:
  - `database/raw/0_page_search_parser.py` — BeautifulSoup으로 검색 결과 페이지에서 식당 프로필 링크 추출 → `link_restaurants.txt`
  - `database/raw/1_dynamic_crawling.ipynb` — Selenium으로 각 식당의 상세 페이지(카테고리/태그/메뉴/리뷰/영업시간 등) 동적 로딩 후 HTML 저장
- **원본 산출물**: `database/raw/restaurants/*.html`, `page_search.txt`, `page_sample.txt`

### 5.2 전처리
- `database/processed/1_html_to_csv.ipynb` — HTML → `restaurant_df.csv`, `menu_df.csv`, `review_df.csv`
- `database/processed/2_csv_preprocesse.ipynb` — 결측/중복 정리, 태그·카테고리 분리, 텍스트 클리닝
- `database/processed/3_restaurant_df_long_lat.ipynb` — 주소 지오코딩으로 `lat`, `lng` 부여
- `database/processed/{4,5}_database_*.ipynb` — 릴레이션(카테고리↔식당, 태그↔식당, 태그↔리뷰) 분리, 테이블별 CSV(`db_csv_tablewise/`) 생성

### 5.3 저장
- `database/sql/db_setup.ipynb` 에서 SQLite(`restaurant.db`)에 테이블 생성 + CSV 적재
- `database/sql/embedding_{category,food,menu,tag,review}.ipynb` 에서 `text-embedding-3-small`로 벡터 생성 → **base64 인코딩**하여 각 테이블 `embedding TEXT` 컬럼에 저장
  - 이렇게 하면 별도 벡터 DB 없이도 SQLite만으로 유사도 검색 가능

### 5.4 활용 (Runtime)
```
[User Question]
      │
      ▼
 ┌──────────────┐
 │  route_node  │  ROUTER_PROMPT로 embedding / fixed 판정
 └──────────────┘
   │            │
embedding     fixed
   │            │
   ▼            ▼
embedding_slot  fixed_slot              (JSON Schema 강제 슬롯 추출)
 {category,      {restaurant,
  tag, menu,      menu, user}
  food, review}
   │            │
   └──────┬─────┘
          ▼
 ┌─────────────────────┐
 │ connector_search    │ db_embedding_search / db_fixed_search
 │                     │  · 슬롯별 코사인 유사도 top-N
 │                     │  · 관계 테이블(category↔식당, 태그↔식당/리뷰) 이동
 │                     │  · restaurant_code 교집합 → 상세 조인
 └─────────────────────┘
          │
          ▼  restaurant_list[dict] (name/menus/reviews/tags/lat,lng ...)
 ┌─────────────────────┐
 │    generate_node    │ system_prompt.txt + 후보 리스트 + 세션 히스토리
 │                     │ → 단 1개 식당을 "대화체"로 추천
 └─────────────────────┘
          │
          ▼
 answer (Markdown 대화체) + used_restaurant_list (지도 마커·카드 렌더)
```

---

## 6. Database Schema

SQLite 파일 경로: `database/sql/restaurant.db`

### 엔티티 테이블
| Table | Rows | 주요 컬럼 |
|---|---:|---|
| `restaurant` | 100 | `restaurant_code` (PK), `name`, `img_link`, `region`, `address`, `lat`, `lng`, `open_time`, `close_time`, `tel_no` |
| `menu` | 2,008 | `menu_code` (PK), `restaurant_code` (FK), `food_code` (FK), `name`, `price`, `description`, `prompted_description`, `embedding` |
| `review` | 422 | `review_code` (PK), `restaurant_code` (FK), `user_code` (FK), `score`, `taste_level`, `price_level`, `service_level`, `content`, `menu`, `embedding` |
| `users` | 171 | `user_code` (PK), `name`, `avg_score`, `review_cnt`, `follower_cnt` |
| `category` | 123 | `category_code` (PK), `name`, `description`, `embedding` |
| `food` | 323 | `food_code` (PK), `name`, `description`, `embedding` |
| `tag` | 143 | `tag_code` (PK), `name`, `description`, `embedding` |

### 관계 테이블
| Table | Rows | 의미 |
|---|---:|---|
| `rel_restaurant_category` | 176 | 식당 ↔ 카테고리 (M:N) |
| `rel_restaurant_tag` | 625 | 식당 ↔ 태그 (M:N) |
| `rel_review_tag` | 2,336 | 리뷰 ↔ 태그 (M:N) |

### ERD (개요)

<img src="https://github.com/SKN26-3rd-3rd/.github/blob/main/png/rename.png?raw=true" width="1100px;" /><br />


> `category / food / menu / tag / review` 테이블은 각자 `embedding` 컬럼(base64로 인코딩된 `float32` 벡터)을 갖고 있어, 런타임에 코사인 유사도 검색이 가능합니다.

---

## 7. Installation

### 7.1 사전 요구사항
- Python 3.10 이상
- OpenAI API Key
- (선택) Kakao Maps JavaScript 앱 키 — 지도 마커 기능 사용 시

### 7.2 설치 절차 (Windows / PowerShell 기준)

```powershell
git clone https://github.com/<org>/skn26_3rd_3rd.git
cd skn26_3rd_3rd\3rd_project

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

> macOS / Linux 는 `source .venv/bin/activate` 로 가상환경을 활성화하세요.

### 7.3 환경변수 설정
프로젝트 루트에 `.env` 파일을 만듭니다.

```env
OPENAI_API_KEY=sk-...
KAKAO_MAP_KEY=your_kakao_js_key

LLM_MODEL=gpt-4.1-mini
EMBEDDING_MODEL=text-embedding-3-small
FIXED_SEARCH_MODEL=gpt-4o-mini
ROUTER_MODEL=gpt-4.1-mini
TOP_K=5
```

### 7.4 데이터베이스
`database/sql/restaurant.db` 가 **이미 빌드되어 저장소에 포함**되어 있어 별도 구축 없이 바로 실행할 수 있습니다.

DB를 처음부터 재구축하려면 다음 노트북을 **순서대로** 실행하세요.

```
database/raw/0_page_search_parser.py
database/raw/1_dynamic_crawling.ipynb
database/processed/1_html_to_csv.ipynb
database/processed/2_csv_preprocesse.ipynb
database/processed/3_restaurant_df_long_lat.ipynb
database/processed/4_database_draft.ipynb
database/processed/5_database_final.ipynb
database/sql/db_setup.ipynb
database/sql/embedding_category.ipynb
database/sql/embedding_food.ipynb
database/sql/embedding_menu.ipynb
database/sql/embedding_food_menu.ipynb
database/sql/embedding_tag.ipynb
database/sql/embedding_review.ipynb
```

---

## 8. Usage

### 8.1 Streamlit 앱 실행 (권장)

```powershell
streamlit run main.py
```

또는

```powershell
streamlit run frontend/app.py
```

브라우저에서 `http://localhost:8501` 열람.

- 좌측 상단 **🔎 / 💬 버튼**으로 검색 모드 ↔ 챗봇 모드 전환
- 검색 모드: "식당이름 / 메뉴 / 유저명" 중 선택 후 검색어 입력 → `db_fixed_search`
- 챗봇 모드: 자연어 질문 입력 → LangGraph `run_qa` 파이프라인
- 검색 결과 카드의 **➡️** 버튼으로 식당 상세 페이지(리뷰·메뉴·태그) 오픈
- 우측 Kakao Map 에 마커/중심 자동 갱신

### 8.2 CLI로 파이프라인 직접 실행 (LLM 동작 검증용)

```powershell
python -m src.pipeline
```

```
============================================================
맛집 추천 CLI 테스트 (빈 Enter 입력시 종료)
============================================================

질문 > 신대방삼거리 혼밥하기 좋은 가성비 초밥집
```

### 8.3 Python API로 임베드

```python
from src.pipeline import run_qa

result = run_qa(
    question="조용하고 분위기 좋은 데이트 파스타집",
    session_id="user_42",
)
print(result["answer"])
print(result["used_restaurant_list"][0]["name"])
```

---

## 9. Example

**질문**
```
신대방삼거리 근처 혼밥하기 좋은 가성비 초밥집 알려줘
```

**파이프라인 내부 상태 (개략)**
```json
{
  "route": "embedding",
  "route_payload": {
    "category": "일식",
    "tag": "혼밥",
    "menu": "",
    "food": "초밥",
    "review": "가성비"
  },
  "restaurant_count": 4
}
```

**답변 (Generator 출력 예시)**
> 신대방삼거리역 쪽에 있는 **유태우스시** 어떠세요? 혼자서도 가볍게 가성비 좋은 초밥 드시기 딱 좋은 회전초밥집이에요. 실제로 한 리뷰어분도 *"요즘 회전초밥집 정말 비싼데 여긴 가성비 갑이었어요!"* 라고 하셨을 만큼 `가성비좋은`, `바테이블`, `혼밥` 태그로 자주 언급되는 곳이거든요. 위치는 서울 동작구 보라매로 113 1층이고, 영업시간은 11:00~22:00예요. 퇴근길에 가볍게 한 접시 하시기 딱 좋으실 거예요!

(오른쪽 지도에는 유태우스시 좌표에 마커가 자동 표시됩니다.)

---

## 10. Evaluation Results

본 프로젝트는 동일한 평가 프레임(`50 cases = fixed 20 + embedding 30`)으로 1차, 2차, 최종(3차) 실험을 순차 수행했습니다.

### 10.1 평가 설정
- **공통 골드셋 구조**: 총 50개 (`fixed` 20, `embedding` 30)
- **평가 항목**: route / payload / target hit / answer / retrieval
- **가중치**: route 30%, payload 25%, target 25%, answer 10%, retrieval 10%
- **리포트 경로**:
  - 1차: `src_test/llm_eval_report.json`
  - 2차: `src_test2/llm_eval_report.json`
  - 최종(3차): `src_test3/llm_eval_report.json`

### 10.2 차수별 핵심 성능 비교

| Stage | Report | Pass/Total | Pass Rate | Avg Score | Route | Payload | Target | Answer | Retrieval |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1차 | `src_test` | 23 / 50 | 46.0% | 0.8575 | 100.0% | 82.0% | 52.0% | 100.0% | 100.0% |
| 2차 | `src_test2` | 39 / 50 | 78.0% | 0.9625 | 100.0% | 86.0% | 92.0% | 100.0% | 100.0% |
| 최종(3차) | `src_test3` | 41 / 50 | 82.0% | 0.9725 | 100.0% | 86.0% | 96.0% | 100.0% | 100.0% |

### 10.3 질의 유형별 비교 (`embedding` / `fixed`)

| Stage | Embedding Pass Rate | Fixed Pass Rate |
|---|---:|---:|
| 1차 (`src_test`) | 13.3% (4/30) | 95.0% (19/20) |
| 2차 (`src_test2`) | 63.3% (19/30) | 100.0% (20/20) |
| 최종(3차, `src_test3`) | 73.3% (22/30) | 95.0% (19/20) |

해석 기준으로 보면, 난이도가 높은 `embedding` 질의에서 성능이 단계적으로 개선되었고, `fixed` 질의는 전 차수에서 높은 정확도를 유지했습니다.

### 10.4 차수별 실패 패턴과 보완 포인트

#### 1차 (`src_test`)
- **실패 규모**: 27건 실패
- **주요 유형**:
  - `target restaurant not retrieved`: 18건
  - `payload miss`: 9건
- **진단**:
  - 라우팅과 답변 생성은 안정적이지만, `embedding` 경로에서 타깃 식당 미포함이 대량 발생했습니다.
  - 슬롯 추출 결과가 의도와 미세하게 어긋나면(예: 태그 표현 편차) 검색 후보 교집합이 급격히 좁아지는 문제가 확인되었습니다.

#### 2차 (`src_test2`)
- **실패 규모**: 11건 실패
- **주요 유형**:
  - `payload miss`: 7건
  - `target restaurant not retrieved`: 4건
- **보완 효과**:
  - 타깃 포함률이 52.0% → 92.0%로 크게 향상되었습니다.
  - `fixed` 질의는 20/20으로 안정화되었습니다.
- **남은 과제**:
  - `embedding` 질의에서 payload 표준화(카테고리/태그 표현 정합) 이슈가 지속되었습니다.

#### 최종(3차, `src_test3`)
- **실패 규모**: 9건 실패
- **주요 유형**:
  - `payload miss`: 7건
  - `target restaurant not retrieved`: 2건
- **개선 요약**:
  - target 정확도가 96.0%까지 상승했습니다.
  - 실패 원인이 “검색 미검출”보다 “슬롯 추출 정밀도”로 집중되는 단계에 도달했습니다.

### 10.5 무엇을 추가로 보완해야 하는가
- **슬롯 정규화 강화**: `category/tag/menu/food/review` 슬롯에 대해 동의어 사전 및 표준화 규칙을 추가하여 payload miss를 완화해야 합니다.
- **Embedding 검색 재랭킹 고도화**: 현재 교집합 중심 전략에 BM25/가중 합산 점수를 결합해 타깃 누락 가능성을 줄여야 합니다.
- **Recall@K 중심 평가 지표 추가**: pass/fail 외에 retrieval 단계의 중간 품질을 추적할 수 있도록 정량 지표를 확장해야 합니다.
- **회귀 테스트 자동화**: `embedding` 실패 케이스를 고정 회귀셋으로 운영하여 프롬프트/검색 로직 변경 시 성능 저하를 즉시 탐지해야 합니다.

### 10.6 재현 방법
프로젝트 루트에서 각 차수별 평가를 다음 명령으로 재현할 수 있습니다.

```powershell
python src_test\build_llm_goldset.py
python src_test\evaluate_llm.py

python src_test2\build_llm_goldset.py
python src_test2\evaluate_llm.py

python src_test3\build_llm_goldset.py
python src_test3\evaluate_llm.py
```

---

## 11. Limitations

1. **지역 커버리지가 좁다**: 현재 DB는 신대방삼거리역 일대 100개 식당만 포함합니다. 다른 지역 질문에는 "데이터 기준으로 찾을 수 없다"로 응답합니다.
2. **크롤링 시점 데이터 고정**: 영업시간·메뉴·가격·리뷰 등은 크롤링 시점 스냅샷이며 실시간 반영되지 않습니다.
3. **벡터 저장소가 SQLite**: 식당 100곳 규모에서는 충분히 빠르지만(전체 풀 스캔 후 코사인), 데이터가 수만 건 이상으로 커지면 FAISS/Chroma 등 전용 벡터 DB로의 이관이 필요합니다.
4. **단일 식당 추천 전제**: 시스템 프롬프트가 "최종 1곳 추천"을 강제하기 때문에, "여러 곳 비교"나 "코스 짜기"류 질문은 기본 플로우가 아닙니다.
5. **한국어 · 단일 도메인 최적화**: 프롬프트/슬롯 구조가 한국어 맛집 도메인에 맞춰져 있어 타 도메인 재사용 시 재설계가 필요합니다.
6. **LLM 비용 · 지연**: 한 질문당 최대 3회 LLM 호출(라우팅 → 슬롯 추출 → 생성)이 발생합니다.
7. **리뷰 신뢰도 미보정**: `users.follower_cnt` / `review_cnt` 를 리트리버에서 아직 가중치로 충분히 활용하지 않습니다.
8. **유사도 기반 검색의 한계**: 현재 검색 방식은 임베딩 기반 유사도 상위 N개를 기준으로 후보를 추출하기 때문에, 질문과 직접적으로 관련된 식당이 없는 경우에도 유사도가 상대적으로 높은 식당이 반환될 수 있습니다. 이로 인해 사용자의 의도와 맞지 않는 추천 결과가 포함될 가능성이 있습니다.
---

## 12. Future Work

- [ ] **지역 확장**: 크롤러를 파라미터화하여 N개 역/동 단위로 DB 자동 빌드
- [ ] **벡터 DB 이관**: `Chroma` / `FAISS` 기반 인덱스 (`scripts/build_index.py`)
- [ ] **API 서버 공개**: `api/server.py` 에 FastAPI 엔드포인트로 `run_qa` 노출
- [ ] **Top-N 추천 / 코스 추천 모드**: 현재 "1곳" 고정 정책에 모드 파라미터 추가
- [ ] **리뷰 신뢰도 가중**: `follower_cnt`, 리뷰 작성 일자, 태그 집중도 기반 재랭킹
- [ ] **하이브리드 검색**: BM25 + 임베딩 점수 결합 (현재 `retriever.py` 는 키워드 매칭만)
- [ ] **대화형 슬롯 보정**: "좀 더 조용한 곳으로" 같은 후속 질문에서 이전 슬롯 상속
- [ ] **평가 파이프라인**: 정답 세트 기반 Recall@K, 프롬프트 regression test
- [ ] **모바일 레이아웃 대응**: Streamlit 레이아웃을 반응형으로 개선
- [ ] **CI / 린팅**: `ruff`, `mypy`, GitHub Actions 도입
---
## 13. Service Expansion & Business Model

- **위치 기반 확장**: 신대방삼거리 중심의 단일 지역에서 사용자 위치 기반으로 다지역 확장하여 하이퍼로컬 추천 범위를 확장

- **행동 데이터 기반 로컬 랭킹**: 방문, 체류 시간, 반복 선택 등의 사용자 행동 데이터를 반영하여 단순 리뷰가 아닌 실제 이용 기반 ‘로컬 Pick’ 생성

- **신규 식당 초기 노출 지원**: 리뷰 데이터가 부족한 오픈 1년 이내 식당에 대해 초기 홍보 기회를 제공하고, 일정 기간 이후에는 품질 기준을 적용

- **품질 기반 홍보 모델**: 일정 평점 이상의 식당에 한해 유료 노출을 허용하여, 수익화와 추천 신뢰도를 동시에 유지

- **캐릭터 기반 참여 구조**: QR 기반 방문 인증, 리뷰 활동 등을 통해 경험치를 적립하고 PICKLE을 성장시키는 사용자 참여형 시스템 도입

- **추천 대상 확장**: 식당 중심 추천에서 카페, 술집, 문화시설 등으로 확장하여 로컬 라이프 전반을 아우르는 추천 플랫폼으로 발전

---