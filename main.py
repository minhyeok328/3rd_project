import streamlit as st
import streamlit.components.v1 as components

import database.sql.utils as dbconnector

######################################################################
# 변수 설정
######################################################################

st.set_page_config(layout="wide")

KAKAO_KEY = None

content_height = 500
search_height = 100
selectbox_height = 50
left_sidebar, map_field = st.columns([3.5, 6.5])

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
    st.session_state[lat] = 37.4997
    st.session_state[lng] = 126.9281

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
    st.session_state[lat] = sum([c[0] for c in st.session_state[search_coordinates]]) / coord_cnt
    st.session_state[lng] = sum([c[1] for c in st.session_state[search_coordinates]]) / coord_cnt

    # 지도 갱신
    st.rerun()

# 레스토랑 표기 함수
def open_restaurant_page(restaurant_data:dict):
    st.session_state[open_restaurant] = restaurant_data

# 레스토랑 페이지 닫기
def close_restaurant_page():
    st.session_state[open_restaurant] = None

# 레스토랑 메뉴 표기 html
def menu_card(menu_data:dict) -> str:
    html_code = f"""<div class="menu_card">
    <p style="margin: 0">{menu_data["name"]}</p>
    <p style="margin: 0">{menu_data["price"]}</p>
    <p style="margin: 0">{menu_data["description"]}</p>
</div>"""
    return html_code

# 레스토랑 메뉴 표기 html
def review_card(review_data:dict) -> str:
    html_code = f"""<div class="review_card">
    <p style="margin: 0">{review_data["name"]}</p>
    <p style="margin: 0">{review_data["score"]}</p>
    <p style="margin: 0">{review_data["avg_score"]}</p>
    <p style="margin: 0">{review_data["taste_level"]}</p>
    <p style="margin: 0">{review_data["price_level"]}</p>
    <p style="margin: 0">{review_data["service_level"]}</p>
    <p style="margin: 0">{", ".join(review_data["tags"])}</p>
    <p style="margin: 0">{review_data["content"]}</p>
    <p style="margin: 0">{review_data["menu"]}</p>
</div>"""
    return html_code

# 레스토랑 페이지 html
def restaurant_page(restaurant_data:dict):
    html_code = f"""
<style>
* {{
    box-sizing: border-box;
    padding: 0px;
    margin: 0px;
}}

.center_aligned {{
    display: flex;
    justify-content: center;
    align-items: center;
}}

.container {{
    width: 100%;
}}

.divider {{
    border: none;
    border-top: 1px solid #e0e0e0;
    margin: 12px 12px;
}}

.menu_card {{
    margin: 5px 0px;
    border: 1px solid black;
    border-radius: 5px;
}}

.review_card {{
    margin: 5px 0px;
    border: 1px solid black;
    border-radius: 5px;
}}

#main_container {{
    width: 430px;
}}

</style>
<div id="main_container">
    <div class="container center_aligned">
        <img id="profile_img" src="{restaurant_data["img_link"]}"/>
    </div>
    <div class="container">
        <h3>{restaurant_data["name"]}</h3>
        <p>
            <strong>{restaurant_data["region"]}</strong> | {restaurant_data["address"]}<br>
            <p>⏰: {restaurant_data["open_time"]} ~ {restaurant_data["close_time"]} ☎️: {restaurant_data["tel_no"]}</p>
            <p>{" ".join(["⭐" + c for c in restaurant_data["category"]])}</p>
            <p>{" ".join(["#" + t for t in restaurant_data["tags"]])}</p>
        </p>
    </div>
    <div class="divider"></div>
    <div class="container">
        {
            "\n\t\t".join([menu_card(m) for m in restaurant_data["menus"]])
        }
    </div>
    <div class="divider"></div>
    <div class="container">
        {
            "\n\t\t".join([review_card(r) for r in restaurant_data["reviews"]])
        }
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
def print_search():
    for s in st.session_state[search_result]:
        #<test> 식당 카드 출력
        st.button(f"{s["name"]}", on_click=open_restaurant_page, args=[s,])

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

    update_search_result(dbconnector.fixed_search(indict))

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
    sample_markers = [(37.5000, 126.9277), (37.5003, 126.9267), (37.4994, 126.9278), (37.4989, 126.9251)]
    render_kakao_map(37.5003, 126.9267, sample_markers)
