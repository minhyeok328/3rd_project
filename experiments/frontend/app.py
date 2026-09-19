import streamlit as st
import os
import streamlit.components.v1 as components
from dotenv import load_dotenv
import utils

# 1. 환경 설정 로드
load_dotenv()
KAKAO_KEY = os.getenv("KAKAO_MAP_KEY")
DB_PATH = "restaurant.db"

# --- 지도 렌더링 함수 ---

def render_kakao_map(lat, lon):
    """카카오 지도를 렌더링하고 마커를 표시하는 함수"""
    if not KAKAO_KEY:
        st.error("🔑 .env 파일에서 KAKAO_MAP_KEY를 확인해주세요.")
        return

    html_code = f"""
    <div id="map" style="width:100%;height:450px;border-radius:15px;box-shadow: 0 4px 6px rgba(0,0,0,0.1);"></div>
    <script type="text/javascript" src="https://dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_KEY}&autoload=false"></script>
    <script>
        kakao.maps.load(function() {{
            var container = document.getElementById('map');
            var options = {{
                center: new kakao.maps.LatLng({lat}, {lon}),
                level: 3
            }};
            var map = new kakao.maps.Map(container, options);
            
            // 마커 생성 및 표시
            var marker = new kakao.maps.Marker({{
                position: new kakao.maps.LatLng({lat}, {lon})
            }});
            marker.setMap(map);
        }});
    </script>
    """
    components.html(html_code, height=470)

# --- 메인 UI 구성 ---

st.set_page_config(page_title="PICKLE 맛집 검색", page_icon="🥒")
st.title("🥒 PICKLE")
st.markdown("### 맛집 검색 서비스")

# 검색창
query = st.text_input("어떤 맛집을 찾으시나요?", placeholder="예: 분위기 좋은 파스타 맛집")

if query:
    with st.spinner(f"🔍 '{query}' 분석 중..."):
        try:
            # 1) 가장 유사한 리뷰를 가진 식당 코드를 가져옴
            codes = utils.search_embedding(DB_PATH, "review", query, top_n=3) # top_n을 늘려보세요

            if codes:
                # 2) 찾은 리뷰 코드들과 연결된 식당 정보를 가져오는 쿼리
                # 리뷰 테이블에 restaurant_code 외래키가 있다고 가정합니다.
                code_list = "', '".join(codes)
                sql = f"""
                SELECT r.lat, r.lng, r.name 
                FROM restaurant r
                JOIN review rev ON r.restaurant_code = rev.restaurant_code
                WHERE rev.review_code IN ('{code_list}')
                LIMIT 1
                """
                db_result = utils.query_sender(DB_PATH, sql)

                if db_result:
                    res_lat, res_lon, res_name = db_result[0]
                    st.success(f"🍴 추천 맛집: **'{res_name}'**")
                    render_kakao_map(res_lat, res_lon)
                else:
                    st.warning("식당 정보를 매칭할 수 없습니다.")
                
        except Exception as e:
            st.error(f"검색 과정에서 오류가 발생했습니다: {e}")
            render_kakao_map(37.5665, 126.9780)

else:
    # 검색 전 기본 화면 (서울시청 등)
    st.info("검색어를 입력하시면 추천 맛집 위치로 지도가 이동합니다.")
    render_kakao_map(37.5665, 126.9780)