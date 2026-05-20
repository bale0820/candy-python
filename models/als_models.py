import implicit

from scipy.sparse import (
    csr_matrix
)

cached_model = None
cached_sparse_matrix = None
cached_user_item_matrix = None


def create_als_model(
        user_item_matrix
):

    global cached_model
    global cached_sparse_matrix
    global cached_user_item_matrix

    # sparse matrix 변환
    sparse_matrix = csr_matrix(
        user_item_matrix.values
    )

    # ALS 모델 생성
    model = (
        implicit.als
        .AlternatingLeastSquares(

            factors=20,

            regularization=0.1,

            iterations=20
        )
    )

    # 학습
    model.fit(
        sparse_matrix
    )

    # 캐시 저장
    cached_model = model
    cached_sparse_matrix = sparse_matrix
    cached_user_item_matrix = user_item_matrix

def get_cached_model():

    return (
        cached_model,
        cached_sparse_matrix,
        cached_user_item_matrix
    )