from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI 
from routes.recommend import (
    recommend_router
)
import pandas as pd

from database.db import engine

from models.als_models import (
    create_als_model, load_als_model
)


from apscheduler.schedulers.background import (
    BackgroundScheduler
)




app= FastAPI()
app.include_router(recommend_router)

# DATABASE_URL = "mysql+pymysql://root:mysql1234@localhost:3306/candy"
# engine =create_engine(DATABASE_URL)


@app.get("/")
def home():

    return {
        "message" : "hello candy ai!"
    }

@app.get("/health")
def health():
    return {"status": "ok"}



@app.on_event("startup")
def startup_event():

    # 저장 모델 로드 시도
    loaded = load_als_model()

    # 저장 모델 없을 때만 최초 학습
    if not loaded:

        retrain_als_model()

    scheduler = (
        BackgroundScheduler()
    )

    scheduler.add_job(
        retrain_als_model,
        "cron",
        hour=3,
        minute=0
    )

    scheduler.start()

    print("스케줄러 시작")




def retrain_als_model():

    print("ALS 재학습 시작")

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

    create_als_model(
        user_item_matrix
    )

    print("ALS 재학습 완료")