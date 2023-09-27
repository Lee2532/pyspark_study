"""
DB 연결읗 위한 모듈
"""

import pandas as pd
from sqlalchemy import create_engine

from common.consts import DB_HOST, DB_PW, DB_USER


class DBCONN:
    def __init__(self):
        self.port = 3306  # MySQL 포트
        self.db = "broadcast"  # MySQL 데이터베이스 이름
        self.engine = create_engine(
            f"mysql+pymysql://{DB_USER}:{DB_PW}@{DB_HOST}:{self.port}/{self.db}"
        )

    def insert_df(self, table, df: pd.DataFrame):
        df.to_sql(name=table, con=self.engine, if_exists="append", index=False)
