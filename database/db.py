from sqlalchemy import create_engine

DATABASE_URL = (
    "mysql+pymysql://root:mysql1234@localhost:3306/candy"
)

engine = create_engine(
    DATABASE_URL
)