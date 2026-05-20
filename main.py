from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI 
from routes.recommend import (
    recommend_router
)
import pandas as pd

from database.db import engine

from models.als_models import (
    create_als_model
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
        "message" : "hello candy ai"
    }




@app.on_event("startup")
def startup_event():

    # 최초 학습
    retrain_als_model()

    # 스케줄러 생성
    scheduler = (
        BackgroundScheduler()
    )

    # 매일 새벽 3시 재학습
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