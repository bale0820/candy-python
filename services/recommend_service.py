import pandas as pd

from sklearn.metrics.pairwise import (
    cosine_similarity
)

from models.als_models import (
    create_als_model,
    get_cached_model
)

from database.db import engine



def collaborative_filtering_service(
        user_id: int
):

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

    user_item_matrix = (
        df.pivot_table(
            index="upk",
            columns="ppk",
            values="qty",
            fill_value=0
        )
    )

    similarity = cosine_similarity(
        user_item_matrix
    )

    similarity_df = pd.DataFrame(
        similarity,
        index=user_item_matrix.index,
        columns=user_item_matrix.index
    )

    if user_id not in similarity_df.columns:
        return {
            "message": "유저 없음",
            "recommended_products": []
        }

    similar_users = (
        similarity_df[user_id]
        .sort_values(ascending=False)
    )

    similar_users = (
        similar_users.drop(user_id)
    )

    if similar_users.empty:
        return {
            "message": "추천 유저 없음",
            "recommended_products": []
        }

    most_similar_user = (
        similar_users.index[0]
    )

    similar_user_products = df[
        df["upk"] == most_similar_user
    ]["ppk"]

    my_products = df[
        df["upk"] == user_id
    ]["ppk"]

    recommend_products = (
        similar_user_products[
            similar_user_products.isin(
                my_products
            )
        ]
        .unique()
        .tolist()
    )

    print(type(recommend_products[0]))
   

    return {
        "user_id": user_id,

        "similar_user":
            int(most_similar_user),

        "recommended_products":
            [int(x)
             for x in recommend_products]
    }




def als_recommend_service(
        user_id: int
):

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

    # 유저-상품 매트릭스
    user_item_matrix = (
        df.pivot_table(
            index="upk",
            columns="ppk",
            values="qty",
            fill_value=0
        )
    )

    # 유저 없으면 종료
    if user_id not in user_item_matrix.index:

        return {
            "message": "유저 없음",
            "recommended_products": []
        }

    # ALS 모델 생성
    model, sparse_matrix, cached_matrix = (
        get_cached_model()
    )


    if model is None:
        create_als_model(user_item_matrix)

        model, sparse_matrix, cached_matrix = (get_cached_model())

    # user index
    user_index = (
        user_item_matrix.index
        .tolist()
        .index(user_id)
    )

    # 추천 생성
    recommendations = (
        model.recommend(
            user_index,
            sparse_matrix[user_index],
            N=5
        )
    )

    product_ids = []

    item_ids, scores = recommendations

    for item_id, score in zip(item_ids, scores):

        product_id = (
            user_item_matrix
            .columns[item_id]
        )

        product_ids.append(
            int(product_id)
        )

    return {
        "user_id": user_id,
        "recommended_products":
            product_ids
    }