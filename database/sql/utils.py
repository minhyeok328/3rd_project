import os
import base64
import sqlite3
import numpy as np
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from typing import Union, List
from sklearn.metrics.pairwise import cosine_similarity

# 1. 초기화 및 설정
load_dotenv()
client = OpenAI()
UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(UTILS_DIR, "restaurant.db") 

# 2. 유틸리티 함수
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

def query_sender(query: str, db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    try:
        return pd.read_sql(query, conn)
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()

# 3. 핵심 검색 로직
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

# 4. 상세 정보 조회
def get_detailed_restaurants(code_list: Union[str, list]) -> list:
    if isinstance(code_list, str):
        code_list = [code_list]
    if not code_list:
        return []

    results = []
    codes_str = ", ".join([f"'{code}'" for code in code_list])
    res_df = query_sender(f"SELECT * FROM restaurant WHERE restaurant_code IN ({codes_str})")

    for _, row in res_df.iterrows():
        res_code = row["restaurant_code"]
        
        cat_df = query_sender(f"SELECT c.name FROM category c JOIN rel_restaurant_category rel ON c.category_code = rel.category_code WHERE rel.restaurant_code = '{res_code}'")
        tag_df = query_sender(f"SELECT t.name FROM tag t JOIN rel_restaurant_tag rel ON t.tag_code = rel.tag_code WHERE rel.restaurant_code = '{res_code}'")
        menu_df = query_sender(f"SELECT name, price, description FROM menu WHERE restaurant_code = '{res_code}'")
        # 리뷰 작성자 조회(user 정보와 조인)
        review_query = f"""
            SELECT 
                u.name, u.avg_score, u.review_cnt, u.follower_cnt,
                r.review_code, r.score, r.taste_level, r.price_level, r.service_level, r.content, r.menu
            FROM review r
            JOIN users u ON r.user_code = u.user_code
            WHERE r.restaurant_code = '{res_code}'
        """
        review_df = query_sender(review_query)

        processed_reviews = []
        if not review_df.empty:
            for _, rev_row in review_df.iterrows():
                rev_code = rev_row["review_code"]

                # 각 리뷰에 달린 태그 조회(rel_rev_tag와 조인)
                rev_tag_query = f"""
                    SELECT t.name
                    FROM tag t
                    JOIN rel_review_tag rel ON t.tag_code = rel.tag_code
                    WHERE rel.review_code = '{rev_code}'
                    """
                rev_tags_df = query_sender(rev_tag_query)
                rev_tags = rev_tags_df["name"].tolist() if not rev_tags_df.empty else []
                
                # 리뷰 딕셔너리 구조
                processed_reviews.append({
                    "name": rev_row["name"],
                    "avg_score": rev_row["avg_score"],
                    "review_cnt": rev_row["review_cnt"],
                    "follower_cnt": rev_row["follower_cnt"],
                    "score": rev_row["score"],
                    "taste_level": rev_row["taste_level"],
                    "price_level": rev_row["price_level"],
                    "service_level": rev_row["service_level"],
                    "tags": rev_tags,
                    "content": rev_row["content"],
                    "menu": rev_row["menu"]

                })
        # 결과 값 반환 딕셔너리 구조
        results.append({
            "restaurant_code": res_code,
            "name": row["name"],
            "img_link": row.get("img_link", ""),
            "region": row.get("region", ""),
            "address": row.get("address", ""),
            "tel_no": row.get("tel_no", ""),
            "lat": row["lat"],
            "lng": row["lng"],
            "open_time": row.get("open_time", ""),
            "close_time": row.get("close_time", ""),
            "category": cat_df["name"].tolist() if not cat_df.empty else [],  
            "tags": tag_df["name"].tolist() if not tag_df.empty else [],            
            "menus": menu_df.to_dict('records') if not menu_df.empty else [],
            "reviews": processed_reviews
        })
    return results