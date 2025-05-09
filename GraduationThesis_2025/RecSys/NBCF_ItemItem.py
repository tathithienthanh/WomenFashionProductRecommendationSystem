import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
import pymysql
from functools import lru_cache
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ItemItemRecommender:
    def __init__(self, interaction_df: pd.DataFrame):
        self.interaction_df = interaction_df.copy()
        self._validate_data()
        self.user_item_matrix = None
        self.similarity_matrix = None

    def _validate_data(self):
        required_cols = {'customer_id', 'product_id', 'rating'}
        if not required_cols.issubset(self.interaction_df.columns):
            raise ValueError(f"Thiếu cột: {required_cols}")
        if self.interaction_df.empty:
            logger.warning("Dữ liệu tương tác trống.")

    def prepare_matrices(self):
        self._create_user_item_matrix()
        self._compute_similarity_matrix()

    def _create_user_item_matrix(self):
        self.interaction_df['rating'] = pd.to_numeric(self.interaction_df['rating'], errors='coerce')
        self.user_item_matrix = self.interaction_df.pivot_table(
            index='customer_id', columns='product_id', values='rating', aggfunc='mean'
        ).fillna(0)
        logger.info(f"Ma trận người dùng-sản phẩm: {self.user_item_matrix.shape}")

    def _compute_similarity_matrix(self):
        item_matrix = self.user_item_matrix.T
        self.similarity_matrix = pd.DataFrame(
            cosine_similarity(item_matrix),
            index=item_matrix.index,
            columns=item_matrix.index
        )
        logger.info("Tính toán ma trận tương đồng xong.")

    def recommend_items(self, customer_id: str, top_k: int = 5) -> List[str]:
        if self.similarity_matrix is None:
            self.prepare_matrices()
        if customer_id not in self.user_item_matrix.index:
            logger.warning(f"Không tìm thấy người dùng {customer_id}")
            return []

        user_ratings = self.user_item_matrix.loc[customer_id]
        user_scores = self.similarity_matrix.dot(user_ratings)
        sum_sim = self.similarity_matrix.sum(axis=1).replace(0, 1)
        user_scores /= sum_sim

        interacted_items = user_ratings[user_ratings > 0].index
        recommendations = user_scores.drop(index=interacted_items, errors='ignore')

        return recommendations.nlargest(top_k).index.tolist()

    def get_similar_items(self, product_id: str, top_k: int = 5) -> List[str]:
        if self.similarity_matrix is None:
            self.prepare_matrices()
        if product_id not in self.similarity_matrix:
            logger.warning(f"Không tìm thấy sản phẩm {product_id}")
            return []

        similar_items = self.similarity_matrix[product_id].sort_values(ascending=False)
        return similar_items.drop(index=product_id, errors='ignore').head(top_k).index.tolist()

@lru_cache(maxsize=1)
def get_connection():
    try:
        return pymysql.connect(
            host="localhost",
            user="root",
            password="Abcxyz@123",
            database="eCommerce",
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.Error as e:
        logger.error(f"Lỗi kết nối DB: {e}")
        raise

def load_interaction_data() -> pd.DataFrame:
    query = """
        SELECT r.customer_id, r.product_id, r.rating,
               p.name, p.image_url, p.price, p.discount,
               p.sold, p.quantity, p.rating AS avg_rating,
               c.category_id, c.description AS category_description
        FROM Review r
        JOIN Product p ON r.product_id = p.product_id
        LEFT JOIN ProductHasCategories phc ON p.product_id = phc.product_id
        LEFT JOIN Category c ON phc.category_id = c.category_id
    """
    try:
        conn = get_connection()
        df = pd.read_sql(query, conn)
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0)
        df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)
        df['discount'] = pd.to_numeric(df['discount'], errors='coerce').fillna(0)
        logger.info(f"Tải {len(df)} tương tác từ DB.")
        return df
    except Exception as e:
        logger.error(f"Lỗi khi tải dữ liệu: {e}")
        return pd.DataFrame()
    finally:
        if conn and conn.open:
            conn.close()

def recommend_items_for_user(user_id: str, top_n: int = 5) -> List[Dict]:
    df = load_interaction_data()
    if df.empty:
        logger.warning("Không có dữ liệu.")
        return []

    model = ItemItemRecommender(df[['customer_id', 'product_id', 'rating']])
    model.prepare_matrices()
    recommended_ids = model.recommend_items(user_id, top_n)

    results = []
    for pid in recommended_ids:
        row = df[df['product_id'] == pid].iloc[0].to_dict()
        price = row.get('price', 0)
        discount = row.get('discount', 0)
        final_price = price * (1 - discount / 100) if discount else price
        results.append({
            "product_id": pid,
            "name": row.get('name', ''),
            "image_url": row.get('image_url', ''),
            "price": price,
            "discounted_price": final_price,
            "discount": discount,
            "sold": row.get('sold', 0),
            "quantity": row.get('quantity', 0),
            "rating": row.get('avg_rating', 0),
            "category": {
                "id": row.get('category_id'),
                "description": row.get('category_description', '')
            }
        })
    return results