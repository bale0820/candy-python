from fastapi import FastAPI 
import pandas as pd
from sqlalchemy import create_engine


app= FastAPI()

DATABASE_URL = "mysql+pymysql://root:mysql1234@localhost:3306/candy"
engine =create_engine(DATABASE_URL)


@app.get("/")
def home():

    return {
        "message" : "hello candy ai"
    }


@app.get("/recommend")
def recommend():

    query = """
    SELECT
        ppk,
        upk,
        qty
    FROM user_view_log
    """

    # MySQL 읽기
    df = pd.read_sql(
        query,
        engine
    )

    # 상품별 총 조회수 계산
    product_counts = (
        df.groupby("ppk")["qty"]
        .sum()
        .sort_values(ascending=False)
    )

    # 상위 추천 상품
    top_products = (
        product_counts
        .head(5)
        .index
        .tolist()
    )

    return {
        "recommended_products":
            top_products
    }