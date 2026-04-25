import os
import math
from dotenv import load_dotenv

import streamlit as st
import streamlit.components.v1 as components

import database.sql.utils as dbconnector
from src.pipeline import run_qa

######################################################################
# 변수 설정
######################################################################

st.set_page_config(layout="wide")

load_dotenv()

KAKAO_KEY = os.getenv("KAKAO_MAP_KEY")

content_height = 560
search_height = 90
selectbox_height = 48
# 검색 탭 하단 입력 컨테이너 (hint-bar + chat_input + selectbox) 고정 높이
# → 내부 스크롤 방지용으로 충분히 확보
search_input_height = 190

# 지도 영역 높이 (shell padding 5px*2 + map inner height 기준으로 components.html 높이를 맞춘다)
map_inner_height = 600
map_shell_padding = 5
map_component_height = map_inner_height + map_shell_padding * 2 + 6  # shadow 살짝 여유

st.markdown("""
<style>
/* 최상단 Hero: columns보다 위에 위치 */
.hero {
    position: relative;
    background: linear-gradient(135deg, #03C75A 0%, #06D668 50%, #00A947 100%);
    color: #ffffff;
    padding: 18px 24px;
    border-radius: 20px;
    box-shadow: 0 12px 30px rgba(3, 199, 90, 0.25), inset 0 1px 0 rgba(255,255,255,0.25);
    margin: 24px 0 18px 0;
    overflow: hidden;
}
.hero::before { content:""; position:absolute; top:-60px; right:-40px; width:220px; height:220px; border-radius:50%; background:rgba(255,255,255,0.15); filter:blur(4px); }
.hero::after  { content:""; position:absolute; bottom:-80px; left:30%; width:260px; height:260px; border-radius:50%; background:rgba(255,255,255,0.08); filter:blur(8px); }
.hero-inner { position:relative; display:flex; align-items:center; gap:14px; z-index:1; }
.hero-logo { background:rgba(255,255,255,0.22); border:1px solid rgba(255,255,255,0.45); backdrop-filter:blur(6px); color:#fff; width:46px; height:46px; border-radius:14px; display:inline-flex; align-items:center; justify-content:center; font-weight:900; font-size:22px; box-shadow:0 6px 18px rgba(0,0,0,0.10); }
.hero-title { font-size:22px; font-weight:900; color:#fff; margin:0; letter-spacing:-0.3px; text-shadow:0 1px 2px rgba(0,0,0,0.12); }
.hero-subtitle { font-size:13px; color:rgba(255,255,255,0.92); margin:2px 0 0 0; }
.hero-badges { margin-left:auto; display:flex; gap:8px; z-index:1; position:relative; }
.hero-badge { background:rgba(255,255,255,0.22); border:1px solid rgba(255,255,255,0.4); color:#fff; padding:6px 12px; border-radius:999px; font-size:12px; font-weight:600; backdrop-filter:blur(6px); }
</style>
<div class="hero">
    <div class="hero-inner">
        <div class="hero-logo">🍽</div>
        <div>
            <p class="hero-title">맛집 추천 · Mini Place</p>
            <p class="hero-subtitle">지도에서 찾아보는 우리 동네 진짜 맛집</p>
        </div>
        <div class="hero-badges">
            <span class="hero-badge">✨ AI 추천</span>
            <span class="hero-badge">📍 실시간 지도</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

map_field, left_sidebar = st.columns([5.2, 4.8], gap="large")

start_lat = 37.4997
start_lng = 126.9281

######################################################################
# session_state 초기화
######################################################################

# 레스토랑 페이지 표기할지 여부
open_restaurant = "open_restaurant"
if open_restaurant not in st.session_state:
    st.session_state[open_restaurant] = None

# 채팅 기록
session_chat = "session_chat"
if session_chat not in st.session_state:
    st.session_state[session_chat] = []

# 검색 결과 restaurant dictionary list
search_result = "search_result"
if search_result not in st.session_state:
    st.session_state[search_result] = []

# 지도 마커 위치 지정
search_coordinates = "search_coordinates"
if search_coordinates not in st.session_state:
    st.session_state[search_coordinates] = []

# 지도 중심 위치 지정
lat = "lat"
lng = "lng"
if lat not in st.session_state:
    # 초기 위치는 신대방 삼거리역 위치
    st.session_state[lat] = start_lat
    st.session_state[lng] = start_lng

# 채팅 실시간 출력용 pending 입력
pending_user_input = "pending_user_input"
if pending_user_input not in st.session_state:
    st.session_state[pending_user_input] = None

######################################################################
# 함수 선언
######################################################################

def call_agent(
    user_input: str,
    session_id: str = "test_session",
    stream: bool = False,
    stream_callback=None,
) -> tuple[str, list[dict]]:
    result = run_qa(
        question=user_input,
        session_id=session_id,
        stream=stream,
        stream_callback=stream_callback,
    )
    return result["answer"], result["used_restaurant_list"]


# 검색 결과 세션 저장
def update_search_result(rlist: list[dict]):
    st.session_state[search_result] = rlist

    # 지도 마커 위치 갱신
    st.session_state[search_coordinates] = [(r["lat"], r["lng"]) for r in rlist]

    # 지도 위치 갱신
    coord_cnt = len(rlist)
    if coord_cnt == 0:
        st.session_state[lat] = start_lat
        st.session_state[lng] = start_lng
    else:
        st.session_state[lat] = sum([c[0] for c in st.session_state[search_coordinates]]) / coord_cnt
        st.session_state[lng] = sum([c[1] for c in st.session_state[search_coordinates]]) / coord_cnt

    # 지도 갱신
    st.rerun()


# 레스토랑 표기 함수
def open_restaurant_page(restaurant_data: dict):
    st.session_state[lat] = restaurant_data["lat"]
    st.session_state[lng] = restaurant_data["lng"]
    st.session_state[open_restaurant] = restaurant_data


# 레스토랑 페이지 닫기
def close_restaurant_page():
    st.session_state[open_restaurant] = None


# 레스토랑 평균 별점 계산
def restaurant_avg_score(rdata: dict) -> float:
    revs = rdata["reviews"]
    if len(revs) == 0:
        return 0.0
    avg = sum([r["score"] for r in revs]) / len(revs)
    return round(avg, 1)


profile_src = "data:image/png;base64,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"


def parse_level(level) -> str:
    base_style = "height:20px;line-height:20px;padding:1px 10px 6px 10px;border-radius:9px;display:inline-block;"
    match level:
        case 0:
            return f"<span style=\"{base_style}background-color:#e53935;color:#fafafa;\">불만족</span>"
        case 1:
            return f"<span style=\"{base_style}background-color:#f59e0b;color:#fafafa;\">보통</span>"
        case 2:
            return f"<span style=\"{base_style}background-color:#16a34a;color:#fafafa;\">만족</span>"
        case _:
            return ""


def format_hashtag(instr: str) -> str:
    return (
        '<span style="display:inline-block;padding:2px 10px;margin:2px 4px 2px 0;'
        'border-radius:999px;background:#EBF9F0;color:#0E8E44;'
        f'border:1px solid #D2F3DF;font-size:11px;line-height:1.6;"># {instr}</span>'
    )


def is_not_na(data) -> bool:
    if data is None:
        return False
    if isinstance(data, float) and math.isnan(data):
        return False
    return True


def review_card(review_data: list) -> str:
    html_code = ""
    for r in review_data or []:
        taste_level = parse_level(r.get("taste_level"))
        price_level = parse_level(r.get("price_level"))
        service_level = parse_level(r.get("service_level"))

        level_code = f"""
                    <p style="margin:0px;color:#374151;font-size:12px;">맛&nbsp;&nbsp;{taste_level}&nbsp;&nbsp;&nbsp;가격&nbsp;&nbsp;{price_level}&nbsp;&nbsp;&nbsp;서비스&nbsp;&nbsp;{service_level}</p>""" if taste_level != "" else ""

        menu_code = f"""
                    <p style="margin:6px 0 0 0;color:#374151;font-size:12px;">메뉴: {r.get("menu", "")}</p>""" if is_not_na(r.get("menu")) else ""

        r_tags = r.get("tags", []) or []
        tag_code = f"""
                    <p style="margin:10px 0px 0px 0px;">{" ".join([format_hashtag(t) for t in r_tags])}</p>""" if len(r_tags) != 0 else ""

        reviewer_name = r.get("name", "익명")
        avg_score = r.get("avg_score", "-")
        review_cnt = r.get("review_cnt", 0)
        follower_cnt = r.get("follower_cnt", 0)
        score = r.get("score", "-")
        content = r.get("content", "") or ""

        html_code += f"""
            <div style="width:100%;border:1px solid #E5E7EB;border-radius:12px;margin-bottom:8px;padding:12px;background:#FFFFFF;">
                <div style="display:flex;align-items:center;gap:10px;">
                    <img src="{profile_src}" style="width:40px;height:40px;object-fit:cover;border-radius:50%;border:1px solid #E5E7EB;" />
                    <div style="flex:1;">
                        <p style="margin:0;font-weight:700;color:#111827;font-size:13px;">{reviewer_name}</p>
                        <p style="margin:2px 0 0 0;color:#6B7280;font-size:11px;">평균 ★{avg_score} · 리뷰 {review_cnt} · 팔로워 {follower_cnt}</p>
                    </div>
                    <div style="color:#0F9F48;font-weight:700;font-size:13px;">★ {score}</div>
                </div>
                <div style="margin-top:10px;">{level_code}{menu_code}
                    <p style="margin:8px 0 0 0;color:#111827;font-size:13px;line-height:1.5;">{content}</p>{tag_code}
                </div>
            </div>"""
    return html_code


def menu_card(menu_data: list) -> str:
    html_code = ""

    for m in menu_data or []:
        price_val = m.get("price")
        description_val = m.get("description")
        name_val = m.get("name", "이름 없음")

        price_code = ""
        if is_not_na(price_val):
            try:
                price_code = f"""
                <span style="margin:0;color:#0F9F48;font-weight:700;font-size:13px;">{int(price_val):,}원</span>"""
            except Exception:
                price_code = f"""
                <span style="margin:0;color:#0F9F48;font-weight:700;font-size:13px;">{price_val}</span>"""

        description_code = f"""
                <p style="color:#6B7280;margin:4px 0 0 0;font-size:12px;">{description_val}</p>""" if is_not_na(description_val) else ""

        html_code += f"""
            <div style="width:100%;border-bottom:1px solid #F3F4F6;padding:12px 4px;">
                <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;">
                    <span style="margin:0;font-weight:600;color:#111827;font-size:13px;">{name_val}</span>{price_code}
                </div>{description_code}
            </div>"""
    return html_code


def restaurant_page(restaurant_data: dict):
    style_center = "display:flex;justify-content:center;align-items:center;"
    style_container = "width:100%;"
    style_divider = "border:none;border-top:1px solid #E5E7EB;margin:14px 4px;"
    style_main_container = "width:100%;"
    style_section_title = "font-size:15px;font-weight:700;margin:0 0 10px 0;color:#111827;"

    name = restaurant_data.get("name", "이름 없음")
    img_link = restaurant_data.get("img_link", "") or ""
    region = restaurant_data.get("region", "") or ""
    address = restaurant_data.get("address", "") or ""
    categories = restaurant_data.get("category", []) or []
    rest_tags = restaurant_data.get("tags", []) or []
    reviews = restaurant_data.get("reviews", []) or []
    menus = restaurant_data.get("menus", []) or []
    avg = 0.0
    if reviews:
        try:
            avg = round(sum([r.get("score", 0) or 0 for r in reviews]) / len(reviews), 1)
        except Exception:
            avg = 0.0

    open_close_code = f"""
        <p style="margin:6px 0 0 0;color:#374151;">⏰ {restaurant_data.get("open_time", "")} ~ {restaurant_data.get("close_time", "")}</p>""" if is_not_na(restaurant_data.get("open_time")) else ""

    tel_code = f"""
        <p style="margin:6px 0 0 0;color:#374151;">☎️ {restaurant_data.get("tel_no", "")}</p>""" if is_not_na(restaurant_data.get("tel_no")) else ""

    tag_code = f"""
                <div style="margin:8px 0 0 0;">{" ".join([format_hashtag(t) for t in rest_tags])}</div>""" if len(rest_tags) != 0 else ""

    category_line = " · ".join(["#" + c for c in categories]) if categories else "카테고리 정보 없음"

    thumb_html = (
        f'<img class="detail-hero-img" src="{img_link}">'
        if img_link
        else '<div class="detail-hero-img" style="background:linear-gradient(135deg,#F3F4F6,#E5E7EB);'
             'display:flex;align-items:center;justify-content:center;color:#9CA3AF;">No Image</div>'
    )

    html_code = f"""
<div class="detail-shell">
    <div style="{style_container+style_center}">
        {thumb_html}
    </div>
    <div style="{style_container}margin-top:14px;">
        <h3 style="margin:0 0 6px 0;color:#111827;font-weight:900;letter-spacing:-0.3px;">{name}</h3>
        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
            <span class="r-rating">★ {avg}</span>
            <span style="color:#6B7280;font-size:13px;">리뷰 <b style="color:#111827;">{len(reviews)}</b>개</span>
        </div>
        <p style="margin:8px 0 0 0;color:#6B7280;font-size:13px;">{category_line}</p>
    </div>
    <div style="{style_divider}"></div>
    <div style="{style_container}">
        <h5 class="detail-section-title">기본 정보</h5>
        <p style="margin:0;color:#374151;">📍 <strong>{region}</strong>{" · " + address if address else ""}</p>{open_close_code}{tel_code}{tag_code}
    </div>
    <div style="{style_divider}"></div>
    <div style="{style_container}">
        <h5 class="detail-section-title">리뷰 {len(reviews)}</h5>
        <div style="{style_container}">{review_card(reviews)}</div>
    </div>
    <div style="{style_divider}"></div>
    <div style="{style_container}">
        <h5 class="detail-section-title">메뉴 {len(menus)}</h5>
        <div style="{style_container}">{menu_card(menus)}</div>
    </div>
</div>
"""
    return html_code


st.markdown("""
<style>
:root {
    --naver-green: #03C75A;
    --naver-green-dark: #0E8E44;
    --naver-green-light: #06D668;
    --naver-green-glow: rgba(3, 199, 90, 0.25);
    --line: #E5E7EB;
    --line-soft: #F3F4F6;
    --text-main: #111827;
    --text-sub: #6B7280;
    --bg-soft: #F8FAFC;
    --grad-main: linear-gradient(135deg, #03C75A 0%, #06D668 50%, #00A947 100%);
    --grad-soft: linear-gradient(135deg, #F1FBF5 0%, #EBF9F0 100%);
}

html, body, .stApp {
    background:
        radial-gradient(1200px 500px at 10% -10%, rgba(3, 199, 90, 0.08), transparent 60%),
        radial-gradient(1000px 500px at 110% 0%, rgba(3, 199, 90, 0.05), transparent 60%),
        #FAFCFB !important;
}

.block-container {
    padding-top: 3.8rem;
    padding-bottom: 1rem;
    max-width: 1600px;
}
/* Streamlit 상단 헤더 영역이 Hero와 겹치지 않게 투명 유지 + 여유 공간 확보 */
[data-testid="stHeader"] {
    background: transparent;
    height: 0;
}
[data-testid="stToolbar"] {
    right: 1rem;
}

/* ------- HERO HEADER ------- */
.hero {
    position: relative;
    background: var(--grad-main);
    color: #ffffff;
    padding: 18px 24px;
    border-radius: 20px;
    box-shadow: 0 12px 30px var(--naver-green-glow), inset 0 1px 0 rgba(255,255,255,0.25);
    margin-top: 24px;
    margin-bottom: 18px;
    overflow: hidden;
}
.hero::before {
    content: "";
    position: absolute;
    top: -60px; right: -40px;
    width: 220px; height: 220px;
    border-radius: 50%;
    background: rgba(255,255,255,0.15);
    filter: blur(4px);
}
.hero::after {
    content: "";
    position: absolute;
    bottom: -80px; left: 30%;
    width: 260px; height: 260px;
    border-radius: 50%;
    background: rgba(255,255,255,0.08);
    filter: blur(8px);
}
.hero-inner {
    position: relative;
    display: flex;
    align-items: center;
    gap: 14px;
    z-index: 1;
}
.hero-logo {
    background: rgba(255,255,255,0.22);
    border: 1px solid rgba(255,255,255,0.45);
    backdrop-filter: blur(6px);
    color: #ffffff;
    width: 46px;
    height: 46px;
    border-radius: 14px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 22px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.10);
}
.hero-title {
    font-size: 22px;
    font-weight: 900;
    color: #ffffff;
    margin: 0;
    letter-spacing: -0.3px;
    text-shadow: 0 1px 2px rgba(0,0,0,0.12);
}
.hero-subtitle {
    font-size: 13px;
    color: rgba(255,255,255,0.92);
    margin: 2px 0 0 0;
}
.hero-badges {
    margin-left: auto;
    display: flex;
    gap: 8px;
    z-index: 1;
    position: relative;
}
.hero-badge {
    background: rgba(255,255,255,0.22);
    border: 1px solid rgba(255,255,255,0.4);
    color: #fff;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    backdrop-filter: blur(6px);
}

/* ------- PANELS ------- */
.panel {
    background: #ffffff;
    border: 1px solid var(--line);
    border-radius: 20px;
    box-shadow: 0 6px 20px rgba(17, 24, 39, 0.06);
    padding: 14px;
}

/* ------- MAP TOOLBAR ------- */
.map-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 14px;
    margin-bottom: 10px;
    background: #ffffff;
    border: 1px solid var(--line);
    border-radius: 14px;
    box-shadow: 0 4px 14px rgba(17, 24, 39, 0.05);
}
.map-toolbar-left {
    display: flex;
    align-items: center;
    gap: 10px;
}
.map-pin {
    width: 30px; height: 30px;
    border-radius: 10px;
    background: var(--grad-main);
    color: #fff;
    display: inline-flex;
    align-items: center; justify-content: center;
    font-size: 14px;
    box-shadow: 0 4px 12px var(--naver-green-glow);
}
.map-title {
    font-weight: 800;
    color: var(--text-main);
    font-size: 14px;
}
.map-count {
    background: var(--grad-soft);
    color: var(--naver-green-dark);
    border: 1px solid #CEEBDA;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
}

/* ------- EMPTY STATE ------- */
.naver-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100%;
    min-height: 260px;
    padding: 24px 16px;
    color: var(--text-sub);
    gap: 8px;
    background:
        radial-gradient(600px 200px at 50% 0%, rgba(3,199,90,0.06), transparent 70%);
    border-radius: 16px;
}
.empty-emoji {
    font-size: 44px;
    filter: drop-shadow(0 6px 14px rgba(3,199,90,0.25));
}

/* Empty-state(검색/채팅 결과 없음)가 포함된 결과 박스:
   - 불필요한 스크롤바 제거
   - 내부 블록을 세로 중앙 정렬해서 메시지를 박스 정가운데에 고정 */
[data-testid="stVerticalBlockBorderWrapper"]:has(.naver-empty) {
    overflow: hidden !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.naver-empty) [data-testid="stVerticalBlock"] {
    height: 100%;
    justify-content: center;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.naver-empty) .stMarkdown {
    width: 100%;
}

/* ------- CHAT INPUT ------- */
.stChatInput > div {
    border-radius: 14px;
    border: 1px solid var(--line);
    box-shadow: 0 4px 14px rgba(17, 24, 39, 0.04);
    transition: all .18s ease;
}
.stChatInput > div:focus-within {
    border-color: var(--naver-green);
    box-shadow: 0 0 0 3px rgba(3, 199, 90, 0.18), 0 10px 24px rgba(3, 199, 90, 0.12);
}

/* ------- SELECTBOX ------- */
.stSelectbox [data-baseweb="select"] > div {
    border-radius: 12px;
    border-color: var(--line);
    transition: all .15s ease;
}
.stSelectbox [data-baseweb="select"] > div:hover {
    border-color: var(--naver-green);
    box-shadow: 0 0 0 3px rgba(3, 199, 90, 0.12);
}

/* ------- GENERIC BUTTONS ------- */
button[kind="secondary"] {
    border-radius: 12px;
    border: 1px solid var(--line);
    transition: all .15s ease;
}
button[kind="secondary"]:hover {
    border-color: var(--naver-green);
    color: var(--naver-green);
    background: #F1FBF5;
}

/* ------- CHAT MESSAGES ------- */
[data-testid="stChatMessage"] {
    border-radius: 16px;
    padding: 10px 12px;
    margin-bottom: 8px;
    border: 1px solid var(--line-soft);
    background: #ffffff;
    box-shadow: 0 4px 12px rgba(17, 24, 39, 0.04);
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: var(--grad-soft);
    border-color: #D2F3DF;
}

/* ------- SEARCH RESULT COUNT ------- */
.result-count-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px;
    background: var(--grad-soft);
    border: 1px solid #D2F3DF;
    border-radius: 12px;
    margin-bottom: 10px;
}
.result-count-left {
    font-size: 12px;
    color: var(--naver-green-dark);
    font-weight: 700;
}
.result-count-right {
    font-size: 11px;
    color: var(--text-sub);
}

/* ------- RESTAURANT CARD ------- */
.r-card {
    position: relative;
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 12px;
    margin-bottom: 10px;
    background: #ffffff;
    box-shadow: 0 4px 14px rgba(17, 24, 39, 0.05);
    transition: all .2s ease;
    overflow: hidden;
}
.r-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; bottom: 0;
    width: 4px;
    background: var(--grad-main);
    opacity: 0;
    transition: opacity .2s ease;
}
.r-card:hover {
    border-color: #B7EBCD;
    transform: translateY(-2px);
    box-shadow: 0 14px 30px rgba(3, 199, 90, 0.15);
}
.r-card:hover::before {
    opacity: 1;
}
.r-title {
    font-size: 17px;
    font-weight: 800;
    margin: 0;
    color: var(--text-main);
    line-height: 1.3;
    letter-spacing: -0.2px;
}
.r-rating {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 10px;
    border-radius: 999px;
    background: var(--grad-soft);
    color: var(--naver-green-dark);
    border: 1px solid #D2F3DF;
    font-size: 12px;
    font-weight: 800;
}
.r-meta {
    font-size: 12px;
    color: var(--text-sub);
    margin: 0;
}
.r-category {
    font-size: 12px;
    color: #374151;
    margin: 6px 0 0 0;
    font-weight: 500;
}
.r-chip {
    display: inline-block;
    padding: 3px 10px;
    margin: 3px 4px 0 0;
    border-radius: 999px;
    background: #EBF9F0;
    color: var(--naver-green-dark);
    border: 1px solid #D2F3DF;
    font-size: 11px;
    font-weight: 600;
}
.r-thumb {
    display: block;
    width: 100%;
    max-width: 124px;
    aspect-ratio: 1 / 1;
    margin: 4px auto;
    border-radius: 12px;
    object-fit: cover;
    border: 1px solid var(--line);
    box-shadow: 0 4px 14px rgba(17, 24, 39, 0.08);
}
.r-thumb-ph {
    display: flex;
    width: 100%;
    max-width: 124px;
    aspect-ratio: 1 / 1;
    margin: 4px auto;
    border-radius: 12px;
    background: linear-gradient(135deg, #F3F4F6, #E5E7EB);
    align-items: center; justify-content: center;
    color: #9CA3AF; font-size: 12px;
}

/* ------- DETAIL PAGE ------- */
.detail-shell {
    border: 1px solid var(--line);
    border-radius: 20px;
    padding: 16px;
    background: #ffffff;
    box-shadow: 0 10px 30px rgba(17, 24, 39, 0.06);
}
.detail-hero-img {
    width: 100%;
    max-width: 460px;
    height: 280px;
    border-radius: 16px;
    object-fit: cover;
    border: 1px solid var(--line);
    box-shadow: 0 12px 30px rgba(17, 24, 39, 0.10);
}
.detail-section-title {
    font-size: 15px;
    font-weight: 800;
    margin: 0 0 10px 0;
    color: var(--text-main);
    letter-spacing: -0.2px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.detail-section-title::before {
    content: "";
    width: 4px;
    height: 16px;
    border-radius: 4px;
    background: var(--grad-main);
    display: inline-block;
}

/* ------- HINT BAR ------- */
.hint-bar {
    background: linear-gradient(135deg, #F8FAFC 0%, #F1FBF5 100%);
    border: 1px solid #E5E7EB;
    padding: 6px 10px;
    border-radius: 10px;
    margin-bottom: 6px;
}

/* ------- NAVER-STYLE TABS ------- */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 2px solid var(--line);
    background: transparent;
    padding: 0 4px;
    margin-bottom: 10px;
}
.stTabs [data-baseweb="tab"] {
    height: 44px;
    padding: 0 18px;
    background: transparent;
    border: none;
    border-bottom: 3px solid transparent;
    border-radius: 0;
    font-weight: 700;
    font-size: 14px;
    color: var(--text-sub);
    transition: all .15s ease;
    margin-bottom: -2px;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--naver-green-dark);
    background: transparent;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: var(--naver-green) !important;
    border-bottom: 3px solid var(--naver-green) !important;
    font-weight: 800;
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {
    display: none !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 6px;
}

/* scrollbar for container */
[data-testid="stVerticalBlockBorderWrapper"] ::-webkit-scrollbar {
    width: 8px;
}
[data-testid="stVerticalBlockBorderWrapper"] ::-webkit-scrollbar-thumb {
    background: #D1D5DB;
    border-radius: 8px;
}
[data-testid="stVerticalBlockBorderWrapper"] ::-webkit-scrollbar-thumb:hover {
    background: var(--naver-green);
}
</style>
""", unsafe_allow_html=True)


# 검색창 함수
def _safe_get(d: dict, key, default=""):
    v = d.get(key, default)
    return v if is_not_na(v) else default


def print_restaurant_card(rdata: dict, card_index: int):
    # restaurant_code 중복 시 위젯 key 충돌이 나지 않도록 index 기반 key를 사용한다.
    button_key = f"rbtn_{card_index}"
    card_key = f"rcard_{card_index}"

    # 카드 컨테이너 자체(.st-key-rcard_xxx)에 r-card 스타일을 적용한다.
    # 기존의 st.markdown('<div class="r-card">')+'</div>' 방식은 Streamlit이 각 markdown을
    # 별도 블록으로 감싸 "빈 .r-card 박스"가 먼저 렌더되는 버그가 있어 제거한다.
    st.markdown(f"""
<style>
.st-key-{card_key} {{
    position: relative;
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 12px 14px;
    margin-bottom: 10px;
    background: #ffffff;
    box-shadow: 0 4px 14px rgba(17, 24, 39, 0.05);
    transition: all .2s ease;
    overflow: hidden;
}}
.st-key-{card_key}::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; bottom: 0;
    width: 4px;
    background: var(--grad-main);
    opacity: 0;
    transition: opacity .2s ease;
}}
.st-key-{card_key}:hover {{
    border-color: #B7EBCD;
    transform: translateY(-2px);
    box-shadow: 0 14px 30px rgba(3, 199, 90, 0.15);
}}
.st-key-{card_key}:hover::before {{
    opacity: 1;
}}
.st-key-{button_key} button {{
    width: 100%;
    height: 34px;
    border-radius: 10px;
    border: 1px solid #D1D5DB;
    background: #ffffff;
    color: #111827;
    font-size: 12px;
    font-weight: 700;
    transition: all .18s ease;
}}
.st-key-{button_key} button:hover {{
    border-color: transparent;
    color: #ffffff;
    background: linear-gradient(135deg, #03C75A 0%, #06D668 50%, #00A947 100%);
    box-shadow: 0 8px 20px rgba(3, 199, 90, 0.3);
    transform: translateY(-1px);
}}
</style>
""", unsafe_allow_html=True)

    avg = restaurant_avg_score(rdata)
    review_cnt = len(rdata.get("reviews", []) or [])
    name = _safe_get(rdata, "name", "이름 없음")
    img_link = _safe_get(rdata, "img_link", "")
    address = _safe_get(rdata, "address", "")
    region = _safe_get(rdata, "region", "")
    categories = rdata.get("category", []) or []
    rest_tags = rdata.get("tags", []) or []

    category_line = " · ".join(categories) if categories else "카테고리 정보 없음"
    location_line = f"{region} · {address}".strip(" ·") if (region or address) else "위치 정보 없음"

    tag_chips = "".join([
        f'<span class="r-chip">#{t}</span>' for t in rest_tags[:4]
    ])

    thumb_html = (
        f'<img class="r-thumb" src="{img_link}" />'
        if img_link
        else '<div class="r-thumb-ph">No Image</div>'
    )

    with st.container(key=card_key):
        col1, col2 = st.columns([3, 7], vertical_alignment="center")
        with col1:
            st.markdown(thumb_html, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
<div style="width:100%;">
    <div style="display:flex;align-items:center;gap:8px;justify-content:space-between;">
        <p class="r-title">{name}</p>
        <span class="r-rating">★ {avg}</span>
    </div>
    <p class="r-meta" style="margin-top:4px;">리뷰 <b style="color:#111827;">{review_cnt}</b>개</p>
    <p class="r-category">{category_line}</p>
    <p class="r-meta" style="margin-top:4px;">📍 {location_line}</p>
    <div style="margin-top:8px;">{tag_chips}</div>
</div>
""", unsafe_allow_html=True)

            st.button("상세보기 →", key=button_key, on_click=open_restaurant_page, args=[rdata])


def print_search():
    results = st.session_state[search_result]
    if not results:
        st.markdown(
            """
<div class="naver-empty">
    <div class="empty-emoji">🍴</div>
    <p style="margin:0;font-weight:700;color:#111827;font-size:15px;">아직 검색 결과가 없어요</p>
    <p style="margin:0;font-size:12px;color:#6B7280;">
        아래 검색창에 <b style="color:#03C75A;">식당명 · 메뉴 · 유저</b>를 입력해보세요
    </p>
    <div style="margin-top:6px;display:flex;gap:6px;flex-wrap:wrap;justify-content:center;">
        <span class="r-chip">#파스타</span>
        <span class="r-chip">#강남</span>
        <span class="r-chip">#데이트</span>
        <span class="r-chip">#분위기</span>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f"""
<div class="result-count-bar">
    <div class="result-count-left">🔎 검색 결과 {len(results)}건</div>
    <div class="result-count-right">지도 마커를 확인해 보세요</div>
</div>
""",
        unsafe_allow_html=True,
    )
    for idx, s in enumerate(results):
        print_restaurant_card(s, idx)


# fixed_search 활용
fixed_search_options = ["식당이름", "메뉴", "유저명"]
fixed_search_data_keys = ["restaurant", "menu", "user"]


def add_search(intype: str, instr: str):
    close_restaurant_page()

    indict = {
        fixed_search_data_keys[0]: "",
        fixed_search_data_keys[1]: "",
        fixed_search_data_keys[2]: ""
    }

    target_key = fixed_search_data_keys[fixed_search_options.index(intype)]
    indict[target_key] = instr

    update_search_result(dbconnector.db_fixed_search(indict))


# 채팅창 함수
def print_chat():
    if not st.session_state[session_chat]:
        st.markdown(
            """
<div class="naver-empty">
    <div class="empty-emoji">💬</div>
    <p style="margin:0;font-weight:700;color:#111827;font-size:15px;">AI에게 맛집을 물어보세요</p>
    <p style="margin:0;font-size:12px;color:#6B7280;">
        자연스럽게 원하는 조건을 얘기해 주세요
    </p>
    <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;justify-content:center;max-width:420px;">
        <span class="r-chip">강남역 파스타</span>
        <span class="r-chip">조용한 데이트</span>
        <span class="r-chip">혼밥 좋은 곳</span>
        <span class="r-chip">분위기 좋은 카페</span>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
        return

    for chat in st.session_state[session_chat]:
        role = chat["role"]
        content = chat["content"]

        with st.chat_message(role):
            st.write(content)


# 새 채팅 출력 함수
def add_chat(instr: str, answer_placeholder):
    st.session_state[session_chat].append({"role": "user", "content": instr})

    def stream_callback(current_text: str):
        answer_placeholder.markdown(current_text)

    response, restaurant_datas = call_agent(
        instr,
        stream=True,
        stream_callback=stream_callback,
    )

    answer_placeholder.markdown(response)

    st.session_state[session_chat].append({"role": "assistant", "content": response})
    update_search_result(restaurant_datas)


# 지도 출력 함수
def render_kakao_map(lat, lon, markers=None):
    """카카오 지도를 렌더링하고 마커를 표시하는 함수"""
    if not KAKAO_KEY:
        st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #F8FAFC 0%, #F1FBF5 100%);
            border: 2px dashed #B7EBCD;
            color:#374151;
            padding: 30px;
            border-radius: 20px;
            width: 100%; height: 720px;
            display:flex; flex-direction:column;
            align-items:center; justify-content:center; gap:12px;
            box-shadow: 0 10px 30px rgba(3, 199, 90, 0.1);">
            <div style="font-size:54px;filter:drop-shadow(0 6px 14px rgba(3,199,90,0.25));">🗺️</div>
            <p style="margin:0;font-weight:800;font-size:16px;color:#111827;">지도 키가 설정되어 있지 않아요</p>
            <p style="margin:0;font-size:12px;color:#6B7280;">
                .env 파일의 <code style="background:#FFFFFF;padding:2px 6px;border-radius:6px;border:1px solid #E5E7EB;">KAKAO_MAP_KEY</code> 를 확인해주세요
            </p>
        </div>""",
        unsafe_allow_html=True)
        return

    if markers is None:
        markers = []

    # markers는 (lat, lng) 튜플 또는 dict({lat,lng,name,img,rating,category,address}) 모두 허용
    normalized = []
    for m in markers:
        if isinstance(m, dict):
            normalized.append({
                "lat": m.get("lat"),
                "lng": m.get("lng"),
                "name": m.get("name", "") or "",
                "img": m.get("img", "") or "",
                "rating": m.get("rating", 0),
                "category": m.get("category", "") or "",
                "address": m.get("address", "") or "",
            })
        else:
            mlat, mlng = m
            normalized.append({
                "lat": mlat, "lng": mlng,
                "name": "", "img": "", "rating": 0, "category": "", "address": "",
            })

    import json as _json
    markers_json = _json.dumps(normalized, ensure_ascii=False)

    html_code = f"""
    <style>
        html, body {{ margin:0; padding:0; background: transparent; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        .map-shell {{
            position: relative;
            padding: {map_shell_padding}px;
            border-radius: 22px;
            background: linear-gradient(135deg, #03C75A 0%, #06D668 40%, #00A947 100%);
            box-shadow:
                0 20px 40px rgba(3, 199, 90, 0.22),
                0 4px 12px rgba(17, 24, 39, 0.08);
        }}
        .map-shell::after {{
            content: "";
            position: absolute;
            inset: -2px;
            border-radius: 24px;
            padding: 2px;
            background: linear-gradient(135deg, rgba(255,255,255,0.6), rgba(255,255,255,0));
            -webkit-mask: linear-gradient(#000,#000) content-box, linear-gradient(#000,#000);
            -webkit-mask-composite: xor;
                    mask-composite: exclude;
            pointer-events: none;
        }}
        #map {{
            width: 100%;
            height: {map_inner_height}px;
            border-radius: 18px;
            overflow: hidden;
            background: #EEF2F1;
        }}
        .floating-badge {{
            position: absolute;
            top: 16px; left: 16px;
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.6);
            box-shadow: 0 8px 24px rgba(17, 24, 39, 0.12);
            padding: 8px 14px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
            color: #0E8E44;
            z-index: 10;
            display: inline-flex; align-items: center; gap: 6px;
        }}
        .floating-badge .dot {{
            width: 8px; height: 8px; border-radius: 50%;
            background: #03C75A;
            box-shadow: 0 0 0 4px rgba(3,199,90,0.25);
        }}

        /* Custom InfoWindow (CustomOverlay 기반 카드) */
        .info-card {{
            position: relative;
            width: 240px;
            background: #ffffff;
            border-radius: 14px;
            border: 1px solid #E5E7EB;
            box-shadow: 0 16px 36px rgba(17,24,39,0.18);
            overflow: hidden;
            transform: translateY(-10px);
            animation: pop .2s ease;
        }}
        @keyframes pop {{
            from {{ opacity: 0; transform: translateY(-4px) scale(.97); }}
            to   {{ opacity: 1; transform: translateY(-10px) scale(1); }}
        }}
        .info-card::after {{
            content: "";
            position: absolute;
            bottom: -8px; left: 50%;
            transform: translateX(-50%) rotate(45deg);
            width: 14px; height: 14px;
            background: #ffffff;
            border-right: 1px solid #E5E7EB;
            border-bottom: 1px solid #E5E7EB;
        }}
        .info-thumb {{
            width: 100%;
            height: 110px;
            object-fit: cover;
            background: linear-gradient(135deg,#F3F4F6,#E5E7EB);
            display: block;
        }}
        .info-thumb-ph {{
            width: 100%; height: 110px;
            background: linear-gradient(135deg,#F3F4F6,#E5E7EB);
            display: flex; align-items: center; justify-content: center;
            color: #9CA3AF; font-size: 12px;
        }}
        .info-body {{ padding: 10px 12px 12px 12px; }}
        .info-title {{
            font-size: 14px; font-weight: 800; color: #111827; margin: 0;
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }}
        .info-meta {{
            display: flex; align-items: center; gap: 6px;
            margin-top: 4px;
            font-size: 12px; color: #6B7280;
        }}
        .info-rating {{
            color: #0E8E44; font-weight: 800;
            background: #EBF9F0; border: 1px solid #D2F3DF;
            padding: 1px 8px; border-radius: 999px;
            font-size: 11px;
        }}
        .info-category {{ font-size: 11px; color: #374151; margin-top: 4px; }}
        .info-address {{ font-size: 11px; color: #6B7280; margin-top: 2px; line-height: 1.4; }}
        .info-close {{
            position: absolute; top: 6px; right: 6px;
            width: 22px; height: 22px;
            border-radius: 50%;
            background: rgba(17,24,39,0.55);
            color: #fff;
            display: flex; align-items: center; justify-content: center;
            font-size: 14px; cursor: pointer;
            border: none;
            z-index: 2;
        }}
        .info-close:hover {{ background: rgba(17,24,39,0.8); }}
    </style>
    <div class="map-shell">
        <div class="floating-badge"><span class="dot"></span>마커 {len(normalized)}개 표시 중</div>
        <div id="map"></div>
    </div>
    <script type="text/javascript" src="https://dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_KEY}&autoload=false"></script>
    <script>
        var MARKER_DATA = {markers_json};

        function escapeHtml(str) {{
            if (str === null || str === undefined) return "";
            return String(str)
                .replace(/&/g, "&amp;").replace(/</g, "&lt;")
                .replace(/>/g, "&gt;").replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }}

        function buildInfoHtml(d) {{
            var thumb = d.img
                ? '<img class="info-thumb" src="' + escapeHtml(d.img) + '"/>'
                : '<div class="info-thumb-ph">No Image</div>';
            var rating = (d.rating || d.rating === 0) ? d.rating : '-';
            var title = escapeHtml(d.name || '이름 없음');
            var cat = escapeHtml(d.category || '');
            var addr = escapeHtml(d.address || '');
            return ''
                + '<div class="info-card">'
                +   '<button class="info-close" onclick="window.__closeInfo && window.__closeInfo()">×</button>'
                +   thumb
                +   '<div class="info-body">'
                +     '<p class="info-title">' + title + '</p>'
                +     '<div class="info-meta">'
                +       '<span class="info-rating">★ ' + escapeHtml(rating) + '</span>'
                +     '</div>'
                +     (cat ? '<p class="info-category">' + cat + '</p>' : '')
                +     (addr ? '<p class="info-address">📍 ' + addr + '</p>' : '')
                +   '</div>'
                + '</div>';
        }}

        kakao.maps.load(function() {{
            var container = document.getElementById('map');

            var options = {{
                center: new kakao.maps.LatLng({lat}, {lon}),
                level: 3
            }};

            var map = new kakao.maps.Map(container, options);
            var activeOverlay = null;
            window.__closeInfo = function() {{
                if (activeOverlay) {{
                    activeOverlay.setMap(null);
                    activeOverlay = null;
                }}
            }};

            MARKER_DATA.forEach(function(d) {{
                if (d.lat == null || d.lng == null) return;
                var pos = new kakao.maps.LatLng(d.lat, d.lng);
                var marker = new kakao.maps.Marker({{ map: map, position: pos }});

                // 이름이 있을 때만 클릭 시 정보창 노출
                if (d.name) {{
                    kakao.maps.event.addListener(marker, 'click', function() {{
                        window.__closeInfo();
                        var overlay = new kakao.maps.CustomOverlay({{
                            position: pos,
                            yAnchor: 1.15,
                            xAnchor: 0.5,
                            content: buildInfoHtml(d),
                            zIndex: 3
                        }});
                        overlay.setMap(map);
                        activeOverlay = overlay;
                        map.panTo(pos);
                    }});
                }}
            }});

            // 빈 공간 클릭 시 닫기
            kakao.maps.event.addListener(map, 'click', function() {{
                window.__closeInfo();
            }});
        }});
    </script>
    """
    components.html(html_code, height=map_component_height)


######################################################################
# 우측 사이드: 탭 UI (맛집 탐색 / AI 상담)
######################################################################
with left_sidebar:
    tab_search, tab_chat = st.tabs(["🔎 맛집 탐색", "💬 AI 상담"])

    ######################################################################
    # 검색창 탭
    ######################################################################
    with tab_search:
        # 위: 검색 결과 / 식당 정보 블럭
        # 하단 입력 영역이 넉넉한 search_input_height(170)로 커진 만큼
        # 상단 결과 영역은 동일한 만큼 살짝만 줄여서 우측 전체 높이가 과하게 커지지 않게 맞춘다.
        with st.container(height=content_height - (search_input_height - (search_height + selectbox_height)) - selectbox_height, border=True):
            if st.session_state[open_restaurant] is not None:
                _, col = st.columns([8.7, 1.3])
                with col:
                    st.button("닫기", on_click=close_restaurant_page, key="close_detail_btn")

                st.markdown(restaurant_page(st.session_state[open_restaurant]), unsafe_allow_html=True)
            else:
                print_search()

        # 아래: 검색 입력 블럭 (내부 스크롤이 생기지 않도록 search_input_height 고정)
        with st.container(height=search_input_height):
            st.markdown(
                """
<div class="hint-bar">
    <p style="font-size:12px; color:#374151; margin:0;">
        🔍 <b style="color:#03C75A;">식당명 · 메뉴 · 유저</b> 로 빠르게 찾아보세요
    </p>
</div>
""",
                unsafe_allow_html=True,
            )

            user_input = st.chat_input(
                "검색어를 입력하세요 (예: 파스타, 강남)",
                key="search_chat_input",
            )

            user_input_type = st.selectbox(
                "검색 옵션",
                fixed_search_options,
                label_visibility="collapsed",
                key="search_type_select",
            )

            if user_input is not None:
                add_search(user_input_type, user_input)

    ######################################################################
    # 채팅창 탭
    ######################################################################
    with tab_chat:
        chatbox = st.container(height=content_height, border=True)

        # 아래: 채팅 입력 블럭
        with st.container(height=search_height):
            user_input = st.chat_input(
                "맛집 조건을 자유롭게 입력해보세요",
                key="ai_chat_input",
            )

            if user_input is not None:
                st.session_state[pending_user_input] = user_input

        # 위: 채팅 결과 블럭
        with chatbox:
            print_chat()

            if st.session_state[pending_user_input] is not None:
                pending_input = st.session_state[pending_user_input]
                st.session_state[pending_user_input] = None

                with st.chat_message("user"):
                    st.write(pending_input)

                with st.chat_message("assistant"):
                    answer_placeholder = st.empty()
                    add_chat(pending_input, answer_placeholder)

######################################################################
# 지도
######################################################################
with map_field:
    # 마커 데이터 조립 (UI 표시용으로만 활용, 상태 변경 없음)
    if st.session_state[open_restaurant] is not None:
        _r = st.session_state[open_restaurant]
        marker_payload = [{
            "lat": _r.get("lat"),
            "lng": _r.get("lng"),
            "name": _r.get("name", ""),
            "img": _r.get("img_link", ""),
            "rating": restaurant_avg_score(_r),
            "category": ", ".join(_r.get("category", []) or []),
            "address": _r.get("address", ""),
        }]
    else:
        marker_payload = [{
            "lat": _r.get("lat"),
            "lng": _r.get("lng"),
            "name": _r.get("name", ""),
            "img": _r.get("img_link", ""),
            "rating": restaurant_avg_score(_r),
            "category": ", ".join(_r.get("category", []) or []),
            "address": _r.get("address", ""),
        } for _r in st.session_state[search_result]]

    st.markdown(f"""
<div class="map-toolbar">
    <div class="map-toolbar-left">
        <div class="map-pin">📍</div>
        <div>
            <div class="map-title">지도 뷰</div>
            <div style="font-size:11px;color:#6B7280;">마커를 클릭하면 식당 정보가 바로 뜹니다</div>
        </div>
    </div>
    <div class="map-count">🗺 마커 {len(marker_payload)}개</div>
</div>
""", unsafe_allow_html=True)

    render_kakao_map(st.session_state[lat], st.session_state[lng], marker_payload)