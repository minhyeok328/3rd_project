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

### 5.5 시스템 및 LLM 아키텍처

#### 시스템 아키텍처
<img src="https://github.com/SKN26-3rd-3rd/.github/blob/main/png/system.png?raw=true" width="1100px;" /><br />

#### LLM 아키텍처
<img src="https://github.com/SKN26-3rd-3rd/.github/blob/main/png/llm.png?raw=true" width="1100px;" /><br />

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

### 8.4 RAG 기반 LLM·벡터DB 연동 구현 코드

#### (1) 파이프라인 진입점 — `run_qa()` & LangGraph 조립

```python
# 335:385:src/pipeline.py
def run_qa(
    question: str,
    session_id: str = "default",
    stream: bool = False,
    stream_callback=None,
) -> dict[str, Any]:
    # 컴파일된 그래프 준비 (최초 1회만 실제 빌드).
    graph = get_graph()

    # 그래프에 초기 state 를 넣어 실행.
    # 내부적으로 노드들이 순서대로 호출되며 state 가 채워진다.
    result = graph.invoke(
        {
            "question": question,
            "session_id": session_id,
            "stream": stream,
            "stream_callback": stream_callback,
        }
    )

    # 외부에 돌려줄 표준 포맷으로 정리.
    return {
        "question": question,
        "route": result.get("route"),
        "route_payload": result.get("route_payload", {}),
        "restaurant_list": result.get("restaurant_list", []),
        "used_restaurant_list": result.get("used_restaurant_list", []),
        "answer": result.get("answer", ""),
    }
```

```python
# 297:317:src/pipeline.py
    # 시작점 → route_node 로 들어간다.
    graph.add_edge(START, "route_node")

    # route_node 이후 조건부 분기:
    #   route_condition() 가 반환하는 문자열에 따라 목적지 노드가 달라진다.
    graph.add_conditional_edges(
        "route_node",
        route_condition,
        {
            "embedding": "embedding_slot_node",
            "fixed": "fixed_slot_node",
        },
    )

    # 슬롯 추출 결과는 둘 다 connector_search_node 로 수렴.
    graph.add_edge("embedding_slot_node", "connector_search_node")
    graph.add_edge("fixed_slot_node", "connector_search_node")

    # DB 조회 → 최종 답변 생성 → 종료.
    graph.add_edge("connector_search_node", "generate_node")
    graph.add_edge("generate_node", END)
```

#### (2) 라우팅 — 질문을 `embedding` / `fixed` 로 분기

```python
# 45:62:src/router.py
    llm = ChatOpenAI(
        model=SETTINGS.router_model,
        temperature=0,
        api_key=SETTINGS.openai_api_key,
    )

    raw = llm.invoke(ROUTER_PROMPT.replace("{question}", question)).content.strip().lower()
    if "fixed" in raw:
        return "fixed"
    return "embedding"
```

#### (3) 슬롯 추출 — JSON Schema 강제로 구조화된 슬롯 획득

```python
# 172:204:src/slot_extractor.py
    completion = get_openai_client().chat.completions.create(
        model=model,
        messages=[
            {"role": "developer", "content": EMBEDDING_SLOT_PROMPT},
            {"role": "user", "content": instr},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "embedding_slot_result",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string"},
                        "tag": {"type": "string"},
                        "menu": {"type": "string"},
                        "food": {"type": "string"},
                        "review": {"type": "string"},
                    },
                    "required": ["category", "tag", "menu", "food", "review"],
                    "additionalProperties": False,
                },
            },
        },
        temperature=0,
        max_completion_tokens=120,
        top_p=1,
    )
```

#### (4) 벡터DB 연동 핵심 — SQLite에 저장된 base64 임베딩으로 코사인 유사도 검색

```python
# 18:33:database/sql/utils.py
def get_embedding(text: str):
    if not text or not text.strip():
        text = " "
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(response.data[0].embedding, dtype=np.float32)

def decode_embedding(encoded_str: str):
    if not encoded_str:
        return None
    try:
        return np.frombuffer(base64.b64decode(encoded_str), dtype=np.float32)
    except:
        return None
```

```python
# 45:78:database/sql/utils.py
def search_embedding(table_name: str, query_text: str, top_n: int = 5):
    t_name = table_name if table_name != "users" else table_name[:-1]

    query_vec = get_embedding(query_text)

    # 임베딩이 존재하는 review 테이블에서 데이터 로드
    rows_df = query_sender(f"SELECT {t_name}_code, embedding FROM {table_name}")
    if rows_df.empty:
        return []

    rows_df = rows_df.dropna(subset=['embedding'])
    codes = rows_df[t_name + "_code"].tolist()
    embs = [decode_embedding(b) for b in rows_df["embedding"].tolist()]

    valid_indices = [i for i, v in enumerate(embs) if v is not None]
    if not valid_indices:
        return []

    filtered_codes = [codes[i] for i in valid_indices]
    filtered_embs = np.array([embs[i] for i in valid_indices])

    # 유사도 계산 및 중복 식당 제외
    similarities = cosine_similarity(query_vec.reshape(1, -1), filtered_embs)[0]
    top_indices = similarities.argsort()[::-1]

    unique_codes = []
    for idx in top_indices:
        c = filtered_codes[idx]
        if c not in unique_codes:
            unique_codes.append(c)
        if len(unique_codes) >= top_n:
            break

    return unique_codes
```

```python
# 272:299:database/sql/utils.py
embedding_search_keys = ["category", "tag", "menu", "food", "review"]
def db_embedding_search(indict:dict):
    if not all(k in indict for k in embedding_search_keys):
        return []

    buff = []
    for k in embedding_search_keys:
        if indict[k] == "":
            continue

        codes = search_embedding(k, indict[k], 8)
        rcodes = search_table(k, codes)
        if not rcodes:
            continue
        buff.append(rcodes)

    if not buff:
        return []

    rlist = []
    cnt_space = [5, 3, 2, 1, 1]
    for i in range(cnt_space[len(buff)-1]):
        for b in buff:
            if len(b) <= i:
                continue
            rlist.append(b[i])

    return get_detailed_restaurants(rlist)
```

#### (5) RAG 답변 생성 — system prompt + 후보 리스트 + 세션 히스토리

```python
# 151:186:src/generator.py
    system_prompt = f"""
{prompt_rules}

[Search Route]
{route}

[Search Payload]
{json.dumps(route_payload, ensure_ascii=False, indent=2)}

[Connector Meta]
{json.dumps(connector_meta, ensure_ascii=False, indent=2)}
""".strip()

    rag_input = {
        "question": question,
        "restaurant_list": retrieved_restaurants,
    }

    messages: list[BaseMessage] = [
        SystemMessage(content=system_prompt),
        *history,
        HumanMessage(content=json.dumps(rag_input, ensure_ascii=False, indent=2)),
    ]
```

#### (6) 보조 모듈

- **후보 재랭킹**: `src/retriever.py` — `simple_retrieve_restaurants()` 가 질문 토큰과 식당 키워드(카테고리/태그/메뉴/리뷰 태그) 매칭으로 top-k 추출.
- **프롬프트 / 규칙**:
  - `src/prompts.py` — `ROUTER_PROMPT`, `EMBEDDING_SLOT_PROMPT`, `FIXED_SEARCH_PROMPT`, `load_system_prompt()`
  - `prompts/system_prompt.txt` — 최종 답변 시 LLM 의 “DB 밖 정보 생성 금지” 등 출력 규칙

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

## 14. Output
- **시스템 및 LLM 아키텍처**: https://www.notion.so/LLM-34c229ee8c458020a50fc2b48b1eb155?source=copy_link
- **수집된 데이터 및 전처리 문서**: https://www.notion.so/34c229ee8c4580cca67be3eb6b45868a?source=copy_link
- **RAG기반 LLM과 벡터데이터베이스 연동 구현 코드**: https://www.notion.so/RAG-LLM-34c229ee8c4580f9a8e1f5d3651dcd37?source=copy_link
- **테스트 계획 및 결과 보고서**: https://www.notion.so/34c229ee8c4580bab0a9dc3682241835?source=copy_link

---
## 15. 프로젝트 회고

### 개인 회고
<table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd;">
    <thead>
        <tr style="background-color: #f8f9fa;">
            <th style="width: 20%; border: 1px solid #ddd; padding: 10px;">이름</th>
            <th style="border: 1px solid #ddd; padding: 10px;">회고</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">박기은</td>
            <td style="border: 1px solid #ddd; padding: 10px;">위도, 경도 API 매핑과 데이터 전처리를 담당하며 서비스 품질은 데이터 신뢰도에서 시작된다는 것을 배웠습니다. 또한 사용자 화면 구현까지 참여하며 서비스가 실제 사용자에게 전달되는 과정을 경험할 수 있었습니다. 좌표 변환 과정에서 발생하는 예외 데이터를 처리하는 과정을 좀 더 꼼꼼하게 수행해야 겠다는 점을 배웠습니다. 이번 프로젝트 경험을 바탕으로, 앞으로는 단순한 위치 표시를 넘어 실시간 경로 최적화나 공간 클러스터링 기반의 추천 등 더 심화된 모빌리티 서비스 구현에 도전해보고 싶습니다.
</td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">서민혁</td>
            <td style="border: 1px solid #ddd; padding: 10px;">이번 프로젝트에서는 LLM 시스템 설계와 프론트엔드 구현을 함께 담당하며, 모델 중심 기능을 실제 서비스 형태로 연결하는 역할을 수행했다. 초기에는 LangChain 기반 구조를 설계하고, 이후 LangGraph로 전환하며 RAG 기반 워크플로우를 보다 구조화된 형태로 구현했다. 특히 사용자 질의부터 데이터 검색, 응답 생성까지 이어지는 전체 흐름을 하나의 파이프라인으로 구성하는 데 집중했고, 프롬프트 엔지니어링을 통해 응답 품질을 개선했다.
<br>
이번 프로젝트를 통해 몇 가지 중요한 점을 깨달을 수 있었다. 먼저 LLM 시스템은 단순히 기능을 구현하는 것이 아니라, 초기에 구조를 얼마나 명확하게 설계하느냐에 따라 전체 개발 난이도가 크게 달라진다는 점을 느꼈다. 실제로 구조 설계가 충분하지 않은 상태에서 개발을 병행하다 보니, 이후 수정과 보완에 많은 시간이 소요되었다.

또한 프로젝트 초기에 아키텍처와 기술 스택을 보다 구체적으로 정의하고, 개발 과정에서 각자의 진행 상황을 지속적으로 공유하는 것이 전체 완성도를 좌우한다는 것을 알게 되었다. 이번 경험을 통해 단순 구현을 넘어, 구조 설계와 협업 방식까지 함께 고려하는 개발의 중요성을 배울 수 있었다.</td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">유동현</td>
            <td style="border: 1px solid #ddd; padding: 10px;">데이터 영역에서 데이터 크롤링을 활용한 수집과 전처리, vector db 구축, LLM의 Langraph 구조 기초, 프론트의 streamlit 구축을 맡게 되었다. streamlit에 html 코드를 넣을 때 자동으로 들어가는 padding을 처리하는데에 시간이 많이 뺏겼었고 시간에 쫓겨 프로젝트의 구조 설계와 개발을 동시에 진행하는 식이 되어 버렸던 점이 아쉬웠던 것 같다.
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">윤정연</td>
            <td style="border: 1px solid #ddd; padding: 10px;">이번 프로젝트에서 프론트엔드와 데이터 전처리를 담당하며, 유연한 문제 해결 능력을 기를 수 있었습니다. 초기에는 네이버 지도 API로 구현을 마쳤으나 예상치 못한 엄격한 정책 제약에 부딪혔고, 마감 기한을 고려해 빠르게 카카오 Map API로 전환하는 '플랜 B' 결단을 내렸습니다. 이 경험을 통해 완벽한 기술적 구현만큼이나, 외부 변수에 유연하게 대처하고 빠른 의사결정을 내리는 것이 중요하다는 점을 깊이 배웠습니다.</td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">이레</td>
            <td style="border: 1px solid #ddd; padding: 10px;">llm을 평소에 직접 다뤄보고 싶었고, 필요성도 느끼고 있던 분야라 스스로 제안한 주제로 프로젝트를 진행하게 되어 더욱 열정을 가지고 임하였다. 
기존의 프로젝트들과는 달리 낯선 개념을 실제 프로젝트에 적용하는 과정에서 확실히 프로젝트 난이도가 올라간 것을 체감할 수 있었다. 배운 내용을 적극적으로 활용해보고자 llm 파트를 맡았는데, 진행하면서 tool과 state 같은 구조가 어떻게 작동하는지 이해할 수 있었고 그 필요성도 느낄 수 있었다. 또한 모델을 직접 만들고 평가를 진행하면서 성능이 개선되는 과정을 확인할 때 큰 성취감과 흥미를 느꼈다.
프로젝트 초반에는 소통이 부족해 동료 간 의견 충돌이 발생하거나 업무가 겹치는 상황도 있었다. 이를 통해 역할을 명확히 나누고 산출물을 공유하며, 각자가 어떤 작업을 진행 중인지 지속적으로 소통하는 것이 프로젝트 진행에 매우 중요하다는 점을 깨달았다.</td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">정영일</td>
            <td style="border: 1px solid #ddd; padding: 10px;">이번 프로젝트를 통해 LLM 기반 서비스는 단순히 AI 모델을 연결하는 기술 구현이 아니라, 사용자 문제를 정의하고 이를 어떤 서비스 가치와 사업 전략으로 발전시킬지 고민하는 과정이라는 점을 느꼈다. 초반에는 RAG, 임베딩, DB connector 등 기술 구조를 이해하는 데 어려움이 있었지만, 프로젝트가 진행되면서 맛집 검색 서비스를 하나의 사업 아이템처럼 바라보게 되었고, 기존 맛집 검색에서 사용자가 느끼는 불편함, 리뷰 기반 추천의 필요성, AI 추천이 줄 수 있는 차별점, MVP 범위와 기능 우선순위 등을 고민할 수 있었다. 특히 단순히 “맛집을 추천한다”는 기능보다, 사용자가 왜 이 서비스를 써야 하는지와 어떤 경험을 제공해야 경쟁력이 생길지를 생각하며 사업 기획에 대한 심층적인 고민을 하게 되었다. 또한 DB 구축, 임베딩 검색, LLM 연동, 화면 구현이 각각 따로 존재하는 것이 아니라 하나의 사용자 경험과 서비스 구조 안에서 연결되어야 한다는 점을 배웠다. 앞으로는 기술 구현뿐 아니라 서비스 방향성, 사용자 가치, 사업 전략까지 함께 고려하며 프로젝트에 더 적극적으로 기여하고 싶다.</td>
        </tr>
    </tbody>
</table>


---


### 팀원 회고

<table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd; margin-bottom: 30px;">
    <thead>
        <tr style="background-color: #f8f9fa;">
            <th style="width: 15%; border: 1px solid #ddd; padding: 10px;">대상자</th>
            <th style="width: 15%; border: 1px solid #ddd; padding: 10px;">작성자</th>
            <th style="border: 1px solid #ddd; padding: 10px;">회고 내용</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td rowspan="5" style="text-align: center; font-weight: bold; border: 1px solid #ddd;">박기은</td>
            <td style="text-align: center; border: 1px solid #ddd;">서민혁</td>
            <td style="border: 1px solid #ddd; padding: 10px;">지도 기능 구현과 데이터 활용 구조 측면에서 안정적인 역할을 수행했다. Kakao Map API를 빠르게 코드화하여 초기 개발 속도를 끌어올렸고, 위경도 좌표 가공과 컬럼 설계 등 데이터 정제 단계에서도 기여도가 높았다. 또한 프론트엔드 디자인에도 참여해 사용자 경험 개선까지 신경 쓴 점이 인상적이었다.</td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">유동현</td>
            <td style="border: 1px solid #ddd; padding: 10px;">Kakao Map API를 주어진 조건에 맞게 빠르게 코드 형태로 가공해 팀원들과 공유하며 개발 초기 속도를 높였고, 동시에 DB embedding 기반 유사도 검색 SQL을 작성해 데이터 활용 구조 구축에도 기여했다. 또한 프론트엔드 디자인에도 참여하며 사용자 경험 개선에 힘썼고, 전반적으로 구현과 협업 모두에서 안정적인 역할을 수행했다.
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">윤정연</td>
            <td style="border: 1px solid #ddd; padding: 10px;">카카오 Map API를 활용하여 지도 기능을 안정적으로 구현했을 뿐만 아니라, 위치 기반 데이터의 정밀도를 높이기 위해 위경도 좌표 데이터를 가공하고 전용 컬럼을 추가하는 등 데이터 설계 단계부터 중추적인 역할을 수행해 주셨습니다. 또한, 프론트엔드 디자인을 도맡아 진행하며 사용자 편의성을 고려한 최적의 인터페이스를 완성하는 데 결정적인 기여를 해 주셨습니다.</td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">이레</td>
            <td style="border: 1px solid #ddd; padding: 10px;">데이터 전처리와 커넥터 코드를 안정적으로 구현하여 LLM 파트와의 연동을 원활하게 만들었습니다. 또한 감각적인 디자인으로 노션 기록과 프론트엔드 구현을 맡아 프로젝트 완성도를 높였습니다.</td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">정영일</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
            Notion을 구성하고 팀원들을 초대하여 작업 자료와 진행 상황을 정리할 수 있는 협업 기반을 마련하였다. Kakao API를 활용해 음식점 데이터에 위도·경도 좌표를 추가한 파일을 공유했고, 추가 수정 요청도 반영하여 데이터 완성도를 높이는 데 기여하였다. 이후 지도/API 연동 작업에도 참여하며 서비스 구현에 필요한 기능적 요소를 담당하였다.
            </td>
        </tr>
    </tbody>
</table>
<table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd; margin-bottom: 30px;">
    <thead>
        <tr style="background-color: #f8f9fa;">
            <th style="width: 15%; border: 1px solid #ddd; padding: 10px;">대상자</th>
            <th style="width: 15%; border: 1px solid #ddd; padding: 10px;">작성자</th>
            <th style="border: 1px solid #ddd; padding: 10px;">회고 내용</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td rowspan="5" style="text-align: center; font-weight: bold; border: 1px solid #ddd;">서민혁</td>
            <td style="text-align: center; border: 1px solid #ddd;">박기은</td>
            <td style="border: 1px solid #ddd; padding: 10px;">모델링뿐만 아니라 유저가 직접 마주하는 프론트엔드 영역까지 동시에 핸들링하며 서비스의 인터페이스를 구축했습니다. 백엔드 로직이 사용자 화면에 어떻게 구현되어야 하는지에 대한 높은 이해도를 보여주었습니다. 프론트와 모델링이라는 서로 다른 영역 사이에서 균형을 잡으며, 서비스의 전체적인 UI/UX 품질을 안정적으로 관리해준 덕분에 완성도 높은 프로젝트가 될 수 있었습니다.
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">유동현</td>
            <td style="border: 1px solid #ddd; padding: 10px;">LLM LangGraph 기반 tool 코딩을 수행하며 기능 구현에 기여하였고 프롬프트 엔지니어링을 통해 모델 응답 품질을 개선하였음. 동시에 프론트엔드 구축에도 참여하여 작성한 초안을 다른 팀원에게 제공해서 프론트 개발을 체계적으로 할 수 있게 했다.</td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">윤정연</td>
            <td style="border: 1px solid #ddd; padding: 10px;">프로젝트의 핵심 엔진인 LLM 시스템 구축 전반을 주도하였으며, 특히 LangGraph를 활용하여 고도화된 RAG 기반 워크플로우를 설계 및 구현해 주셨습니다. 단순히 모델을 연결하는 수준을 넘어 프론트엔드 개발 과정에도 깊이 참여하였으며, 정교한 프롬프트 엔지니어링을 통해 AI 응답과 인터페이스의 완성도를 극대화함으로써 프로젝트의 결과물을 한 단계 끌어올리는 데 결정적인 역할을 수행하셨습니다.</td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">이레</td>
            <td style="border: 1px solid #ddd; padding: 10px;">프로젝트에 적극적으로 참여하며 LLM 파트에서 초기 랭체인 구조를 설계해 랭그래프로의 전환에 큰 기여를 했습니다. 또한 프론트엔드 구현 과정에서도 팀원의 요구를 반영해 완성도를 높였습니다.</td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">정영일</td>
            <td style="border: 1px solid #ddd; padding: 10px;">디스코드 서버 개설을 통해 팀의 소통 및 기록 환경을 마련하고, 프로젝트 초반 기술 탐색 과정에서 RAG 구조와 LLM 관련 자료를 공유하며 팀원들의 이해를 돕는 데 기여하였다. 또한 GitHub 초기 세팅을 정리하고 README를 지속적으로 업데이트하며 프로젝트 전반의 코드 관리와 문서화 기반을 구축하였다. requirements 파일을 공유해 개발 환경을 맞추는 데에도 도움을 주었으며, LLM 모델 선정 및 활용 방향에 대해서도 의견을 제시하며 관련 구현 흐름을 이해하는 데 기여하였다. 프로젝트 진행 중에는 프론트엔드 구현 방식에 대해서도 방향을 제시하고 관련 도구를 검토하는 등 UI 구성 측면에서도 참여하였다. 전반적으로 필요한 자료와 방향을 먼저 제시하며 팀이 작업을 이어갈 수 있도록 기반을 정리하는 역할을 수행하였다.
            </td>
        </tr>
    </tbody>
</table>
<table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd; margin-bottom: 30px;">
    <thead>
        <tr style="background-color: #f8f9fa;">
            <th style="width: 15%; border: 1px solid #ddd; padding: 10px;">대상자</th>
            <th style="width: 15%; border: 1px solid #ddd; padding: 10px;">작성자</th>
            <th style="border: 1px solid #ddd; padding: 10px;">회고 내용</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td rowspan="5" style="text-align: center; font-weight: bold; border: 1px solid #ddd;">유동현</td>
            <td style="text-align: center; border: 1px solid #ddd;">박기은</td>
            <td style="border: 1px solid #ddd; padding: 10px;">팀의 구심점으로 프로젝트의 전체적인 아키텍처를 설계하고 크롤링부터 프론트엔드까지 전 과정을 조율하며 프로젝트의 방향성을 잡아주었습니다. 또한 에러가 발생할 때마다 해결책을 제시하는 뛰어난 문제 해결 능력을 보여주셨습니다. 복잡한 시스템의 흐름을 한눈에 파악하는 통찰력과, 데이터 전처리부터 유저 인터페이스까지 책임지는 폭넓은 기술 스펙트럼이 매우 인상적이었습니다.</td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">서민혁</td>
            <td style="border: 1px solid #ddd; padding: 10px;">프로젝트 전반의 파이프라인을 설계하고 데이터 수집·전처리·vector DB 구축까지 핵심 기반을 주도적으로 구축했다. 또한 Streamlit 기반 프론트 초기 구조를 잡으며 개발 방향성을 제시했고, 다양한 기술 스택 사이의 공백을 메우며 전체 흐름이 끊기지 않도록 조율하는 역할을 수행했다. 실질적으로 프로젝트의 구조와 실행 흐름을 만들어낸 중심 축에 가까운 역할이었다.</td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">윤정연</td>
            <td style="border: 1px solid #ddd; padding: 10px;">모든 영역을 총괄하며 팀의 중심을 잡아주셨습니다. 웹 크롤링을 통한 기초 데이터 수집과 전처리, 그리고 원활한 서비스 연동을 위한 데이터베이스 조회 및 관리 업무를 수행하며 프로젝트의 뼈대를 구축하였을 뿐만 아니라, 프론트엔드의 초기 기틀을 직접 설계하여 개발의 가이드라인을 제시해 주셨습니다. 프로젝트 전반의 기술적 공백을 파악하고 메우며, 팀원들의 업무가 유기적으로 진행될 수 있도록 모든 파트에서 중추적인 역할을 수행해 주셨습니다.</td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">이레</td>
            <td style="border: 1px solid #ddd; padding: 10px;">프로젝트 주제에 맞게 전체 파이프라인을 설계하고, 체계적인 데이터 처리와 프론트 구축으로 초기 구현에 큰 도움을 주었습니다. 또한 프로젝트 진행 중 다양한 상황에서도 침착하게 대응하며 안정적인 분위기를 유지해주었습니다.
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">정영일</td>
            <td style="border: 1px solid #ddd; padding: 10px;">프로젝트 초반부터 주제 방향과 기능 구현 범위를 구체적으로 정리하며 팀원들이 같은 목표를 바라볼 수 있도록 도와주었다. 데이터 전처리 파일, 최종 CSV, DB 파일, mock data 등을 지속적으로 공유하며 개발에 필요한 기반 자료를 마련하였고, 임베딩 벡터 저장 방식과 DB 세팅 방법, connector 사용 방법까지 상세히 안내하였다. 전반적으로 프로젝트의 데이터 구조와 개발 흐름을 주도적으로 잡아준 핵심적인 팀원이었다.</td>
        </tr>
    </tbody>
</table>
<table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd; margin-bottom: 30px;">
    <thead>
        <tr style="background-color: #f8f9fa;">
            <th style="width: 15%; border: 1px solid #ddd; padding: 10px;">대상자</th>
            <th style="width: 15%; border: 1px solid #ddd; padding: 10px;">작성자</th>
            <th style="border: 1px solid #ddd; padding: 10px;">회고 내용</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td rowspan="5" style="text-align: center; font-weight: bold; border: 1px solid #ddd;">윤정연</td>
            <td style="text-align: center; border: 1px solid #ddd;">박기은</td>
            <td style="border: 1px solid #ddd; padding: 10px;">프로젝트의 기초가 되는 벡터 데이터셋을 준비해주신 덕분에 이후 단계의 작업들이 원활하게 진행될 수 있었습니다. 또한 데이터베이스 테이블에 접근하여 필요한 정보를추출하고, 이를 후속 공정에서 활용하기 좋은 리스트 형태로 반환하는 효율적인 함수 코드를 만들어주셨습니다.
</td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">서민혁</td>
            <td style="border: 1px solid #ddd; padding: 10px;">데이터 전처리와 DB 활용 측면에서 안정적인 지원 역할을 수행했다. 벡터 데이터셋 구축을 통해 LLM 활용 기반을 마련했고, DB 접근 및 데이터 추출 로직을 함수 단위로 정리하여 후속 단계에서 재사용 가능하도록 구현한 점이 좋았다. 또한 API 구조 분석 및 정리 과정을 통해 팀원들의 이해도를 높이는 데에도 기여했다.</td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">유동현</td>
            <td style="border: 1px solid #ddd; padding: 10px;">데이터 전처리 파트에서 벡터 DB를 더하는 역할을 하여 모델 활용을 위한 기반을 마련했으며, Kakao Map API 구조를 팀원들과 함께 분석한 뒤 이를 이해하기 쉽게 정리해 공유했다. 또한 DB 검색어 기반 SQL을 작성해 데이터 조회 기능을 구현하였다.</td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">이레</td>
            <td style="border: 1px solid #ddd; padding: 10px;">기한 내에 정확한 데이터 처리를 수행하는 성실한 모습을 보여주었으며, 다양한 역할을 맡아 적극적으로 수행했습니다. 또한 API 연동을 통해 프론트에 필요한 데이터를 효과적으로 제공하며 프로젝트 완성도에 기여했습니다..</td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">정영일</td>
            <td style="border: 1px solid #ddd; padding: 10px;">프로젝트 초반부터 팀원들과의 소통에 참여하며 아이디어 공유 과정에 함께하였다. Figma 작업 참여 의사를 보이며 화면 구성 단계에도 관심을 보였고, 임베딩 작업에서는 사용한 모델 정보를 공유하여 팀 전체가 동일한 기준으로 작업할 수 있도록 도왔다. 또한 category 관련 파일을 제출하며 데이터 처리 과정에도 기여하였다.
            </td>
        </tr>
    </tbody>
</table>
<table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd; margin-bottom: 30px;">
    <thead>
        <tr style="background-color: #f8f9fa;">
            <th style="width: 15%; border: 1px solid #ddd; padding: 10px;">대상자</th>
            <th style="width: 15%; border: 1px solid #ddd; padding: 10px;">작성자</th>
            <th style="border: 1px solid #ddd; padding: 10px;">회고 내용</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td rowspan="5" style="text-align: center; font-weight: bold; border: 1px solid #ddd;">이레</td>
            <td style="text-align: center; border: 1px solid #ddd;">박기은</td>
            <td style="border: 1px solid #ddd; padding: 10px;">서비스의 핵심인 LLM 모델링에 집중하여 사용자의 질문 의도를 정확하게 파악하는 추천 엔진을 구현했습니다. 프롬프트 엔지니어링과 RAG 로직 최적화를 통해 답변의 품질을 상승시켰습니다. 덕분에 데이터 출력의 정확도가 높아질 수 있었습니다.</td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">서민혁</td>
            <td style="border: 1px solid #ddd; padding: 10px;">LLM 파트로 역할을 전환한 이후 빠르게 적응하며 핵심 기능 구현에 집중했다. LangGraph 기반 워크플로우 설계에 참여해 시스템 구조를 구체화했고, embedding 및 데이터 전처리를 통해 모델 응답 품질 향상에 기여했다. 또한 팀 내에서 필요한 데이터 및 작업 결과를 꾸준히 공유하며 협업 흐름을 유지하는 데에도 역할을 했다.</td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">유동현</td>
            <td style="border: 1px solid #ddd; padding: 10px;">데이터의 embedding vector DB 구축에 기여를 함. LLM 구축 팀에 참여를 하여 LLM LangGraph 구조 설계를 주도적으로 이끌어 시스템의 핵심 아키텍처를 구축했고, 팀원이 구축한 tool을 활용해 답변을 생성하는 LLM 모델을 구현하여 프로젝트의 중심 기능을 완성했다.</td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">윤정연</td>
            <td style="border: 1px solid #ddd; padding: 10px;">본래 프론트엔드 개발을 담당할 계획이었으나, 프로젝트의 핵심 동력인 LLM 파트로 역할을 전환하여 뛰어난 기술적 적응력과 역량을 증명해 주셨습니다. RAG 시스템의 답변 품질을 좌우하는 LLM 맞춤형 데이터 전처리 과정을 세밀하게 수행하여 서비스의 신뢰성을 확보하였고, LangGraph 기반의 정교한 워크플로우를 설계 및 구축함으로써 프로젝트의 기술적 완성도를 비약적으로 높여 주셨습니다.</td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">정영일</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
                회의 일정과 그라운드룰 논의 등 팀 운영 과정에 적극적으로 참여하며 협업 흐름을 유지하는 데 도움을 주었다. food, menu 관련 데이터 파일을 공유하고 base64 변환 작업을 수행했으며, DB connector를 LLM src와 연동해 push하는 등 실제 구현 작업에도 성실히 참여하였다. 작업 완료 상황을 꾸준히 공유하여 팀원들이 진행 상태를 파악하는 데 기여하였다.
            </td>
        </tr>
    </tbody>
</table>
<table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd; margin-bottom: 30px;">
    <thead>
        <tr style="background-color: #f8f9fa;">
            <th style="width: 15%; border: 1px solid #ddd; padding: 10px;">대상자</th>
            <th style="width: 15%; border: 1px solid #ddd; padding: 10px;">작성자</th>
            <th style="border: 1px solid #ddd; padding: 10px;">회고 내용</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td rowspan="5" style="text-align: center; font-weight: bold; border: 1px solid #ddd;">정영일</td>
            <td style="text-align: center; border: 1px solid #ddd;">박기은</td>
            <td style="border: 1px solid #ddd; padding: 10px;">한 기획 단계에서는 서비스의 확장성이나 캐릭터화 방향 등 비즈니스 관점의 아이디어를 제시하고, 사용자 유입을 고려한 전략을 함께 고민하면서 기술과 기획을 자연스럽게 연결하는데 기여하셨습니다.</td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">서민혁</td>
            <td style="border: 1px solid #ddd; padding: 10px;">데이터 적재 및 DB 구축을 체계적으로 수행하며 프로젝트의 데이터 안정성을 확보했다. SQL 기반 처리 흐름을 정리해 데이터 활용 기반을 안정적으로 마련했으며, LLM tool 개발에도 일부 기여했다. 특히 기획 단계에서 서비스 확장성과 캐릭터화 전략 등 비즈니스 관점의 아이디어를 제시하며 기술과 기획을 연결하려는 시도가 의미 있었다.</td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">유동현</td>
            <td style="border: 1px solid #ddd; padding: 10px;">SQL을 활용해 DB를 구축하고 데이터를 적재하는 과정을 체계적으로 담당했으며, LLM tool 개발에 기여하였음. 특히 기획 단계에서 사업적 확장 가능성과 캐릭터화 전략 등 서비스 측면의 아이디어와 고객 유치 전략 아이디어를 구상하며 기술과 기획을 연결하는 데 의미 있는 기여를 했다.</td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">윤정연</td>
            <td style="border: 1px solid #ddd; padding: 10px;">SQL을 활용하여 방대한 데이터를 효율적으로 DB에 적재함으로써 프로젝트의 데이터 안정성을 확보하는 데 크게 기여해 주셨습니다. 또한, 생성형 AI 기반의 마스코트 브랜딩을 통해 발표의 몰입감을 높였으며, 발표자로서 프로젝트의 핵심 메시지를 친숙하고 짜임새 있게 시각화하여 효과적으로 전달해 주셨으며, 프로젝트의 대외적인 완성도를 한층 더 끌어올려 주셨습니다.</td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">이레</td>
            <td style="border: 1px solid #ddd; padding: 10px;">데이터 처리를 깔끔하게 수행하고 기한을 철저히 준수하여 프로젝트가 원활하게 진행될 수 있도록 기여했습니다. 또한 안정적인 발표 실력으로 준비한 내용을 명확하게 전달해주었습니다.</td>
        </tr>
    </tbody>
</table>
