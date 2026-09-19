# 프런트엔드

[문서 목록](../README.md)

## 화면 구성

[main.py](../../main.py)의 Streamlit 앱은 검색/채팅 영역과 지도 영역으로 구성됩니다. URL 라우터 대신 세션 상태를 바꿔 목록·상세 화면을 전환합니다.

| 화면 | 입력 | 표시 |
| --- | --- | --- |
| 직접 검색 | 식당이름·메뉴·유저명 중 하나와 문자열 | 연결된 식당 카드·지도 |
| 채팅 | 자연어 질문 | 사용자/모델 메시지·스트리밍 답변·후보 카드 |
| 상세 | 식당 카드 선택 | 주소·메뉴·리뷰·태그·평점 |
| 지도 | 검색 후보·선택 식당 좌표 | Kakao SDK 마커와 중심 |

## 상태와 이벤트

`st.session_state`에 상세 식당, 채팅 표시 이력, 검색 결과, 좌표, 지도 중심, 처리 대기 입력을 저장합니다.

- `add_search` → `db_fixed_search` → `update_search_result`
- `add_chat` → `call_agent` → `run_qa` → 누적 답변 콜백 → `update_search_result`
- `open_restaurant_page`/`close_restaurant_page` → 상세 상태 변경
- 지도 중심은 후보 좌표 평균 또는 상세 식당 좌표로 갱신됩니다.

UI의 메시지 기록과 모델 생성기의 대화 이력은 별도 저장소입니다. `call_agent`는 기본 `test_session`을 사용하므로 멀티유저 대화 격리가 구현된 것으로 해석하면 안 됩니다.

## 렌더링과 의존성

메뉴·리뷰·카드는 HTML 문자열을 `unsafe_allow_html=True`로 표시합니다. 지도는 `components.html` iframe에서 외부 SDK를 사용합니다. 외부 이미지나 사용자 데이터의 삽입 규칙을 수정할 때 HTML 안전성과 결측값 처리를 함께 확인해야 합니다.

지도 키가 없으면 안내가 표시됩니다. 이 동작은 모델 API 키 없이 전체 앱이 시작된다는 의미는 아닙니다.

## 초기 실험 파일

[experiments/frontend/app.py](../../experiments/frontend/app.py)는 현재 앱과 다른 초기 검색/지도 실험입니다. `import utils`와 함수 호출 인자가 현재 유틸 계약과 맞지 않습니다. [experiments/frontend/streamlit.py](../../experiments/frontend/streamlit.py)는 설명 주석만 있어 실행 가능한 대체 앱이 아닙니다.

화면 검증 항목은 [기능 명세](../08-features/README.md)와 [검증 문서](../10-quality/verification-and-limitations.md)를 따릅니다.
