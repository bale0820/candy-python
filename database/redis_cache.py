import json

from database.redis_client import (
    redis_client
)


def save_recommend_result(
        user_id,
        products
):

    redis_client.set(
        f"user:{user_id}:recommend",
        json.dumps(products),
        ex=3600
    )


def get_recommend_result(
        user_id
):

    data = redis_client.get(
        f"user:{user_id}:recommend"
    )

    if data:
        return json.loads(data)

    return None