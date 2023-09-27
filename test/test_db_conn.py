"""
DB 연결 테스트 코드
"""

import pandas as pd
from sqlalchemy import create_engine

from common.consts import DB_HOST, DB_PW, DB_USER

# MySQL 연결 정보
port = 3306  # MySQL 포트
db = "broadcast"  # MySQL 데이터베이스 이름


class TestDataBaseConn:
    def setup_class(self):
        # MySQL 연결 설정
        self.engine = create_engine(
            f"mysql+pymysql://{DB_USER}:{DB_PW}@{DB_HOST}:{port}/{db}"
        )

    def test_conn(self):
        sample_data = [
            {
                "user_id": "test",
                "nickname": "테스트",
                "message": "테스트 입니다",
                "channel": "테스트채널",
                "create_time": "now",
            }
        ]
        df = pd.DataFrame(sample_data)

        df.to_sql(name="twitch", con=self.engine, if_exists="append", index=False)

        # 데이터 조회 (Read)
        select_sql = """SELECT * FROM twitch"""
        df = pd.read_sql(select_sql, con=self.engine)
        print("Data from MySQL:")
        print(df)

        delete_sql = """delete from twitch
                            where nickname = '테스트' """
        pd.read_sql(delete_sql, con=self.engine)
        print("삭제완료")
