import os
import math
from dotenv import load_dotenv

import streamlit as st
import streamlit.components.v1 as components

import database.sql.utils as dbconnector

######################################################################
# 변수 설정
######################################################################

st.set_page_config(layout="wide")

load_dotenv()

KAKAO_KEY = os.getenv("KAKAO_MAP_KEY")

content_height = 500
search_height = 100
selectbox_height = 50
left_sidebar, map_field = st.columns([3.5, 6.5])

start_lat = 37.4997
start_lng = 126.9281

######################################################################
# session_state 초기화
######################################################################

# 채팅창인지 검색창인지
open_chat = "open_chat"
if open_chat not in st.session_state:
    st.session_state[open_chat] = False

# 레스토랑 페이지 표기할지,  여부
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

######################################################################
# 함수 선언
######################################################################

# 검색 결과 세션 저장
def update_search_result(rlist:list[dict]):
    st.session_state[search_result] = rlist

    #<test> 지도 데이터 갱신
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
def open_restaurant_page(restaurant_data:dict):
    st.session_state[lat] = restaurant_data["lat"]
    st.session_state[lng] = restaurant_data["lng"]
    st.session_state[open_restaurant] = restaurant_data

# 레스토랑 페이지 닫기
def close_restaurant_page():
    st.session_state[open_restaurant] = None

# 레스토랑 평균 별점 계산
def restaurant_avg_score(rdata:dict) -> float:
    revs = rdata["reviews"]
    if len(revs) == 0:
        return 0.0
    avg = sum([r["score"] for r in revs]) / len(revs)
    return round(avg, 1)

profile_src="data:image/png;base64,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"
def parse_level(level) -> str:
    match level:
        case 0:
            return "불만족"
        case 1:
            return "보통"
        case 2:
            return "만족"
        case _:
            return ""

def review_card(review_data:dict) -> str:
    html_code=""
    for r in review_data:
        html_code += f"""
            <div style="width:425px;border:0.5px solid #c0c0c0;border-radius:10px;margin-bottom:5px;padding:10px 0px;">
                <div style="width:80px;height:80px;display:inline-block;padding:15px;vertical-align:top;"><img src="{profile_src}" style="width:100%;height:100%;object-fit:cover;" /></div>
                <div style="width:300px;height:80px;display:inline-block;padding-top:17px;vertical-align:top;">
                    <h6 style="padding:0 0 7px 0;">{r["name"]}</h6>
                    <p style="color:gray;">평균 평점 {r["avg_score"]} 리뷰 수 {r["review_cnt"]} 팔로워 수 {r["follower_cnt"]}</p>
                </div><br>
                <div style="width:425px;display:inline-block;padding:0 15px 0 15px;vertical-align:top;">
                    <p style="margin:0px;">맛: {parse_level(r["taste_level"])} 가격: {parse_level(r["price_level"])} 서비스: {parse_level(r["service_level"])}</p>
                    <p style="margin:0px;">⭐{r["score"]}</p>
                    <p style="margin:0px;">메뉴: {r["menu"]}</p>
                    <p style="margin:0px;">{r["content"]}</p>
                    <p style="margin:10px 0px 0px 0px;">{" ".join(["#"+t for t in r["tags"]])}</p>
                </div>
            </div>"""
    return html_code

def menu_card(menu_data:list) -> str:
    html_code = ""

    for m in menu_data:
        price_code = f"""
                <h6 style="margin:0px;padding:0px;">{int(m["price"])}원</h6>""" if not math.isnan(m["price"]) else ""
        description_code = f"""
                <p style="color:gray;margin:5px 0px 0px 0px;">{m["description"]}</p>""" if m["description"] is not None else ""

        html_code += f"""
            <div style="width:425px;border-bottom:0.5px solid #e0e0e0;padding:17px 0px 10px 0px;">
                <h6 style="margin:0px;padding:0px;">{m["name"]}</h6>{price_code}{description_code}                
            </div>"""
    return html_code

def restaurant_page(restaurant_data:dict):
    style_center="display:flex;justify-content:center;align-items:center;"
    style_container="width:100%;"
    style_divider="border:none;border-top: 1px solid #e0e0e0;margin:12px 4px;"
    style_main_container="width:430px;"

    html_code = f"""
<div style="{style_main_container}">
    <div style="{style_container+style_center}">
        <img id="profile_img" style="width:300px;height:300px;object-fit:cover;" src="{restaurant_data["img_link"]}">
    </div>
    <div style="{style_container}">
        <h3>{restaurant_data["name"]}</h3>
        <p>{" ".join(["⭐" + c for c in restaurant_data["category"]])}</p>
    </div>
    <div style="{style_divider}"></div>
    <div style="{style_container}">
        <h5>홈</h5>
        <p>📍 <strong>{restaurant_data["region"]}</strong> | {restaurant_data["address"]}</p>
        <p>⏰ {restaurant_data["open_time"]} ~ {restaurant_data["close_time"]}</p>
        <p>☎️ {restaurant_data["tel_no"]}</p>
        <p>🏷️ {" ".join(["#" + t for t in restaurant_data["tags"]])}</p>
    </div>
    <div style="{style_divider}"></div>
    <div style="{style_container}">
        <h5>리뷰 {len(restaurant_data["reviews"])}</h5>
        <div style="{style_container, style_center}">{review_card(restaurant_data["reviews"])}</div>
    </div>
    <div style="{style_divider}"></div>
    <div style="{style_container}">
        <h5>메뉴 {len(restaurant_data["menus"])}</h5>
        <div style-"{style_container}">{menu_card(restaurant_data["menus"])}</div>
    </div>
</div>
"""
    return html_code

st.markdown("""
<style>
.st-key-switch_btn button {
    width: 65px;
    height: 58px;
    font-size: 24px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# 검색창 < > 팝업 버튼 출력 함수
def switch_sidebar():
    st.session_state[open_chat] = not st.session_state[open_chat]

def switch_button(to_chat:bool):
    st.button("💬" if to_chat else "🔎", key="switch_btn", on_click=switch_sidebar)

# 검색창 함수
def print_restaurant_card(rdata:dict):
    #<progress>
    with st.container(height = 180):
        col1, col2 = st.columns([3, 4])
        with col1:
            st.image(rdata["img_link"], width=145)

        with col2:
            st.markdown(f"""
<div style="width:240px; height:98px; margin-left:-20px;">
    <p style="font-size:20px; font-weight:bold; margin-bottom:0;">{rdata["name"]}</p>
    <p style="font-size:18px; margin-bottom:4px;">⭐{restaurant_avg_score(rdata)}</p>
    <p style="font-size:12px; margin-bottom:4px">{", ".join(rdata["category"])}</p>
    <p style="font-size:12px; color: gray;">{rdata["address"]}</p>
</div>
""", unsafe_allow_html=True)

            _, col3, _ = st.columns([8, 1, 2])

            with col3:
                button_key = f"{rdata["restaurant_code"]}_btn"
                st.markdown(f"""
<style>
.st-key-{button_key} button {{
    margin-top:-100px;
    width: 60px;
    height: 10px;
    border-radius: 10px;
}}
</style>
""", unsafe_allow_html=True)
                st.button("➡️", key=button_key, on_click=open_restaurant_page, args=[rdata,])

def print_search():
    for s in st.session_state[search_result]:
        print_restaurant_card(s)
        

# fixed_search 활용
fixed_search_options = ["식당이름", "메뉴", "유저명"]
fixed_search_data_keys = ["restaurant", "menu", "user"]
def add_search(intype:str, instr:str):
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
    for chat in st.session_state[session_chat]:
        role = chat["role"]
        content = chat["content"]

        with st.chat_message(role):
            st.write(content)

# 새 채팅 출력 함수
def add_chat(instr:str):
    st.session_state[session_chat].append({"role":"user", "content":instr})
    
    #<test> 답변 받아오기
    st.session_state[session_chat].append({"role":"assistant", "content":"AI 반응"})

    # update_search_result 호출

# 지도 출력 함수
def render_kakao_map(lat, lon, markers=None):
    """카카오 지도를 렌더링하고 마커를 표시하는 함수"""
    if not KAKAO_KEY:
        st.markdown(
        """
        <div style="
            background-color: lightblue;
            padding: 10px;
            border-radius: 8px;
            width: 800px; height: 615px;">
        🔑 .env 파일에서 KAKAO_MAP_KEY를 확인해주세요.
        </div>""",
        unsafe_allow_html=True)
        return

    if markers is None:
        markers = []

    marker_scripts = []

    for ith_lat, ith_lon in markers:
        marker_scripts.append(f"""
            new kakao.maps.Marker({{
                map: map,
                position: new kakao.maps.LatLng({ith_lat}, {ith_lon})
            }});
        """)

    buffer = "\n".join(marker_scripts)

    html_code = f"""
    <div id="map" style="width:800px;height:615px;border-radius:15px;box-shadow:0 4px 6px rgba(0,0,0,0.1);"></div>
    <script type="text/javascript" src="https://dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_KEY}&autoload=false"></script>
    <script>
        kakao.maps.load(function() {{
            var container = document.getElementById('map');

            // 지도 중심 세팅
            var options = {{
                center: new kakao.maps.LatLng({lat}, {lon}),
                level: 3
            }};

            var map = new kakao.maps.Map(container, options);

            // 마커 생성 및 표시
            {buffer}
        }});
    </script>
    """
    components.html(html_code, height=635)

######################################################################
# 채팅창
######################################################################
if st.session_state[open_chat]:
    with left_sidebar:
        with st.container(height=search_height):
            col1, col2 = st.columns([1.5, 8.5])

            with col1:
                switch_button(to_chat=False)
            with col2:
                user_input = st.chat_input("채팅 입력")

            if user_input is not None:
                add_chat(user_input)
        
        with st.container(height=content_height):
            print_chat()

######################################################################
# 검색창
######################################################################
else:
    with left_sidebar:
        with st.container(height=search_height + selectbox_height):
            col1, col2 = st.columns([1.5, 8.5])

            with col1:
                switch_button(to_chat=True)
            with col2:
                user_input = st.chat_input("검색어")

            user_input_type = st.selectbox("검색 옵션", fixed_search_options, label_visibility="collapsed")

            if user_input is not None:
                add_search(user_input_type, user_input)
        with st.container(height=content_height - selectbox_height):
######################################################################
# 식당 정보 페이지
######################################################################
            if st.session_state[open_restaurant] is not None:
                                    
                    _, col = st.columns([8.7, 1.3])
                    with col:
                        st.button("✖️", on_click=close_restaurant_page)

                    st.markdown(restaurant_page(st.session_state[open_restaurant]), unsafe_allow_html=True)
######################################################################
# 검색 결과 페이지
######################################################################
            else:
                print_search()

######################################################################
# 지도
######################################################################
with map_field:
    tags = st.session_state[search_coordinates] if st.session_state[open_restaurant] is None else [(st.session_state[open_restaurant]["lat"], st.session_state[open_restaurant]["lng"]), ]
    render_kakao_map(st.session_state[lat], st.session_state[lng], tags)
