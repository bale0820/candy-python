from fastapi import APIRouter

from services.recommend_service import (
    collaborative_filtering_service
)

import pandas as pd

from sklearn.metrics.pairwise import (
    cosine_similarity
)

from database.db import engine

from services.recommend_service import (
    als_recommend_service
)


recommend_router = APIRouter()


@recommend_router.get("/collab/{user_id}")
def collaborative_filtering(
        user_id: int
):

    return collaborative_filtering_service(
        user_id
    )


@recommend_router.get("/als/{user_id}")
def als_recommend(
        user_id: int
):

    return als_recommend_service(
        user_id
    )



@recommend_router.get("/recommend")
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


@recommend_router.get("/related/{product_id}")
def related_products(product_id: int):

        query = """
        SELECT
            ppk,
            upk
        FROM user_view_log
        """

        df = pd.read_sql(
            query,
            engine
        )

        # 현재 상품 본 유저들
        users = df[
            df["ppk"] == product_id
        ]["upk"]

        # 그 유저들이 본 다른 상품
        related = df[
            df["upk"].isin(users)
        ]

        # 자기 자신 상품 제외
        related = related[
            related["ppk"] != product_id
        ]

        # 많이 본 순 정렬
        related_counts = (
            related["ppk"]
            .value_counts()
        )

        top_related = (
            related_counts
            .head(5)
            .index
            .tolist()
        )

        return {
            "product_id": product_id,
            "related_products":
                top_related
        }


@recommend_router.get("/item-based/{product_id}")
def item_based_recommend(product_id: int):

    query = """
    SELECT
        upk,
        ppk,
        qty
    FROM user_view_log
    """

    df = pd.read_sql(
        query,
        engine
    )

    # 상품-유저 매트릭스 생성
    item_user_matrix = (
        df.pivot_table(
            index="ppk",
            columns="upk",
            values="qty",
            fill_value=0
        )
    )

    # 상품 간 유사도 계산
    similarity = cosine_similarity(
        item_user_matrix
    )

    similarity_df = pd.DataFrame(
        similarity,
        index=item_user_matrix.index,
        columns=item_user_matrix.index
    )

    # 현재 상품과 유사한 상품
    similar_products = (
        similarity_df[product_id]
        .sort_values(ascending=False)
    )

    # 자기 자신 제외
    similar_products = (
        similar_products.drop(product_id)
    )

    # 상위 추천 상품
    top_products = (
        similar_products
        .head(5)
        .index
        .tolist()
    )

    return {
        "product_id":
            int(product_id),

        "similar_products":
            [int(x) for x in top_products]
    }




@recommend_router.get("/user-recommend/{user_id}")
def user_recommend(user_id: int):

    query = """
    SELECT
        ppk,
        upk,
        qty,
        sub_category_id
    FROM user_view_log
    """

    df = pd.read_sql(
        query,
        engine
    )

    # 현재 유저 데이터
    user_df = df[
        df["upk"] == user_id
    ]

    # 유저가 많이 본 카테고리
    favorite_categories = (
        user_df
        .groupby("sub_category_id")["qty"]
        .sum()
        .sort_values(ascending=False)
    )

    # 가장 많이 본 카테고리
    top_category = (
        favorite_categories
        .index[0]
    )

    # 같은 카테고리 상품
    category_products = df[
        df["sub_category_id"] == top_category
    ]

    # 인기 상품 계산
    product_counts = (
        category_products
        .groupby("ppk")["qty"]
        .sum()
        .sort_values(ascending=False)
    )

    # 추천 상품
    top_products = (
        product_counts
        .head(5)
        .index
        .tolist()
    )

    return {
        "user_id": user_id,
        "favorite_category":
            int(top_category),
        "recommended_products":
            top_products
    }
