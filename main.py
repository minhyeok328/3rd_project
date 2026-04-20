import streamlit as st

st.set_page_config(layout="wide")

content_height = 500
search_height = 100
selectbox_height = 50
left_sidebar, map_field = st.columns([3.5, 6.5])

# session_state 초기화
open_restaurant = "open_restaurant"
if open_restaurant not in st.session_state:
    st.session_state[open_restaurant] = None

open_chat = "open_chat"
if open_chat not in st.session_state:
    st.session_state[open_chat] = False

session_chat = "session_chat"
if session_chat not in st.session_state:
    st.session_state[session_chat] = []

search_result = "search_result"
if search_result not in st.session_state:
    st.session_state[search_result] = []

######################################################################
# 함수 선언
######################################################################

# 레스토랑 표기 함수
def open_restaurant_page(restaurant_data:dict):
    st.session_state[open_restaurant] = restaurant_data

def close_restaurant_page():
    st.session_state[open_restaurant] = None

def restaurant_page(restaurant_data:dict):
    html_code = f"""
<style>
#main_container {{
    width: 430px;
    height: 800px;
    background-color: lightgreen;
}}
</style>
<div id="main_container">
레스토랑 이름: {restaurant_data["name"]}<br>
레스토랑 내용 들어가는 곳
</div>
"""
    return html_code

# 검색창 < > 팝업 버튼 함수
def switch_sidebar():
    st.session_state[open_chat] = not st.session_state[open_chat]

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

def switch_button(to_chat:bool):
    st.button("💬" if to_chat else "🔎", key="switch_btn", on_click=switch_sidebar)

# 검색창 함수
def print_search():
    for s in st.session_state[search_result]:
        st.button(f"{s["name"]}", on_click=open_restaurant_page, args=[s,])

def add_search(intype:str, instr:str):
    # 검색 함수
    st.session_state[search_result].append({"name":instr})

# 채팅창 함수
def print_chat():
    for chat in st.session_state[session_chat]:
        role = chat["role"]
        content = chat["content"]

        with st.chat_message(role):
            st.write(content)

def add_chat(instr:str):
    st.session_state[session_chat].append({"role":"user", "content":instr})
    
    # 답변 받아오기
    st.session_state[session_chat].append({"role":"assistant", "content":"AI 반응"})

######################################################################
# 식당 정보 페이지
######################################################################
if st.session_state[open_restaurant] is not None:
    with left_sidebar:
        with st.container(height=search_height + content_height + 16):
            _, col = st.columns([8.7, 1.3])

            with col:
                st.button("✖️", on_click=close_restaurant_page)

            st.markdown(restaurant_page(st.session_state[open_restaurant]), unsafe_allow_html=True)

######################################################################
# 채팅창
######################################################################
elif st.session_state[open_chat]:
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

            user_input_type = st.selectbox("검색 옵션", ["식당이름", "메뉴", "유저명"], label_visibility="collapsed")

            if user_input is not None:
                add_search(user_input_type, user_input)

        with st.container(height=content_height - selectbox_height):
            print_search()

######################################################################
# 지도
######################################################################
with map_field:
    st.markdown(
        """
        <div style="
            background-color: lightblue;
            padding: 10px;
            border-radius: 8px;
            width: 800px; height: 615px;">
        지도 들어갈 자리
        </div>""",
        unsafe_allow_html=True)
