# NBCF_ItemItem.py

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
import pymysql

class ItemItemRecommender:
    def __init__(self, interaction_df):
        """
        interaction_df: DataFrame với các cột [customer_id, product_id, rating]
        """
        self.interaction_df = interaction_df.copy()
        self.user_item_matrix = None
        self.similarity_matrix = None

    def prepare_user_item_matrix(self):
        self.user_item_matrix = self.interaction_df.pivot_table(index='customer_id', columns='product_id', values='rating').fillna(0)

    def compute_similarity_matrix(self):
        if self.user_item_matrix is None:
            self.prepare_user_item_matrix()
        item_matrix = self.user_item_matrix.T
        self.similarity_matrix = pd.DataFrame(
            cosine_similarity(item_matrix),
            index=item_matrix.index,
            columns=item_matrix.index
        )

    def recommend_items(self, customer_id, top_k=5):
        if self.similarity_matrix is None:
            self.compute_similarity_matrix()
        
        if customer_id not in self.user_item_matrix.index:
            return []

        user_ratings = self.user_item_matrix.loc[customer_id]
        user_scores = self.similarity_matrix.dot(user_ratings)
        user_scores = user_scores / self.similarity_matrix.sum(axis=1)

        interacted_items = user_ratings[user_ratings > 0].index
        recommendations = user_scores.drop(index=interacted_items)

        return recommendations.sort_values(ascending=False).head(top_k).index.tolist()

    def get_similar_items(self, product_id, top_k=5):
        if self.similarity_matrix is None:
            self.compute_similarity_matrix()
        if product_id not in self.similarity_matrix:
            return []
        similar_items = self.similarity_matrix[product_id].sort_values(ascending=False)
        return similar_items.drop(index=product_id).head(top_k).index.tolist()

# --------- Hàm tiện ích ngoài class ---------

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Abcxyz@123",
        database="eCommerce",
        cursorclass=pymysql.cursors.DictCursor
    )

def recommend_items_for_user(user_id: str, top_n: int = 5) -> List[Dict]:
    try:
        conn = get_connection()
        query = """
            SELECT r.customer_id, r.product_id, r.rating,
                p.name, p.image_url, p.price, p.rating AS avg_rating
            FROM Review r
            JOIN Product p ON r.product_id = p.product_id
        """
        df = pd.read_sql(query, conn)
    finally:
        conn.close()

    if df.empty or user_id not in df['customer_id'].unique():
        return []

    rating_matrix = df.pivot_table(index='customer_id', columns='product_id', values='rating')

    item_similarity = pd.DataFrame(
        cosine_similarity(rating_matrix.T.fillna(0)),
        index=rating_matrix.columns,
        columns=rating_matrix.columns
    )

    user_ratings = rating_matrix.loc[user_id]
    unrated_items = user_ratings[user_ratings.isna()].index
    predicted_ratings = {}

    for item in unrated_items:
        sim_items = item_similarity[item]
        rated_items = user_ratings.dropna().index

        numerator = sum(sim_items[r] * user_ratings[r] for r in rated_items if r in sim_items)
        denominator = sum(abs(sim_items[r]) for r in rated_items if r in sim_items)

        if denominator > 0:
            predicted_ratings[item] = numerator / denominator

    top_items = sorted(predicted_ratings.items(), key=lambda x: x[1], reverse=True)[:top_n]
    top_ids = [item_id for item_id, _ in top_items]

    recommended_products = []
    for item_id in top_ids:
        row = df[df['product_id'] == item_id].iloc[0]
        recommended_products.append({
            "product_id": row["product_id"],
            "name": row["name"],
            "image_url": row["image_url"],
            "price": row["price"],
            "rating": row["avg_rating"]
        })

    return recommended_products
