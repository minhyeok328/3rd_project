from bs4 import BeautifulSoup

# 검색 페이지에서 긁어온 100개의 신대방삼거리 음식점 페이지
with open("page_search.txt", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

# 식당 프로필 하나의 구조
"""
<a class="sc-dWZqqJ gTtztl PoiBlock" href="/profile.php?rid=BIZO90QTeYbp" target="_blank" id="blockBIZO90QTeYbp"><div class="RHeader"><div class="Info"><div class="InfoHeader"><h2 id="titleBIZO90QTeYbp"><span class="number-prefix">1. </span><span class="Info__Title__Place">유태우스시 <span>신대방삼거리역</span></span></h2><div class="Rate InfoRate"><p class="Score"><span>75</span>점</p><span class="Poi__Countour"></span><p class="UserScore"><img src="https://dcicons.s3.ap-northeast-1.amazonaws.com/new/images/mobile/react_m_common/icon_star_blue_new.png" width="16px" height="16px" alt="user score star"><span class="score-text">4.6</span><span class="count-text">(8명)</span></p></div></div><div class="CategoryAndHash"><div class="CategoryContainer"><span class="Category"><span>스시</span></span><span class="Category"><span>회전초밥</span></span></div><div class="HashScrollContainer"><div class="HashContainer"><span class="Hash "><span>데이트</span></span><span class="Hash "><span>가성비좋은</span></span><span class="Hash "><span>바테이블</span></span></div></div><p class="OpenStatus before-open">영업 전</p></div></div></div><div class="ImageGallery images-3"><img src="https://d12zq4w4guyljn.cloudfront.net/300_300_20251221075826166_photo_c2f5e0670740.webp" class="gallery-image" loading="eager" alt="유태우스시  스시, 회전초밥 이미지 1" data-primary-image="true"><img src="https://d12zq4w4guyljn.cloudfront.net/300_300_20251010052126998_photo_5401b39a42c4.webp" class="gallery-image" loading="lazy" alt="유태우스시  스시, 회전초밥 이미지 2" data-primary-image="false"><img src="https://d12zq4w4guyljn.cloudfront.net/300_300_20250416110227_photo1_30f0028c76c8.webp" class="gallery-image" loading="lazy" alt="유태우스시  스시, 회전초밥 이미지 3" data-primary-image="false"></div><div class="PoiBody"><div class="ReviewWrap"><div class="Review">"요즘 회전초밥집 정말 비싼데 여긴 가성비 갑이었어요! 위치는 조금 복잡한 곳에 있긴 하지만 가성비를 찾는다면 여기 강추합니다!..."</div></div></div></a>
"""

restaurants = soup.select(".gTtztl.PoiBlock")

print(f"식당 수: {len(restaurants)}")

# export할 텍스트
buff = ""

# 식당 페이지 링크 하나하나 저장
for r in restaurants:
    if buff != "":
        buff += "\n"
    buff += "https://www.diningcode.com"
    buff += r.get("href")

print(f"파싱된 식당 수: {len(buff.split("\n"))}")

# 식당 링크 목록 저장
with open("link_restaurants.txt", "w", encoding="utf-8") as f:
    f.write(buff)