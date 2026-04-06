## DB연결

import pymysql
import os
from dotenv import load_dotenv

# .env 파일에 적어둔 DB 접속 정보를 가져옵니다.
load_dotenv()

def get_db_connection():
    try:
        conn = pymysql.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "my123456"), # ✅ 환경변수 없으면 기본값 사용
            db=os.getenv("DB_NAME", "AutoTrading"),       # ✅ DB 이름도 기본값 주면 편해요
            port=int(os.getenv("DB_PORT", 3306)),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Exception as e:
        print(f"❌ DB 연결 실패: {e}")
        return None

def insert_market_data(ticker, price):
    """업비트에서 가져온 시세를 market_data 테이블에 저장합니다."""
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                # SQL 실행: market_data 테이블에 종목명과 가격을 넣습니다.
                sql = "INSERT INTO market_data (ticker, price) VALUES (%s, %s)"
                cursor.execute(sql, (ticker, price))
            connection.commit() # 데이터 확정
            # print(f"💾 DB 저장 완료: {ticker} - {price:,}원") # 확인용 (나중에 주석처리)
        except Exception as e:
            print(f"❌ 데이터 저장 중 에러 발생: {e}")
        finally:
            connection.close()

if __name__ == "__main__":
    # 이 파일만 단독으로 실행했을 때 연결이 잘 되는지 테스트합니다.
    conn = get_db_connection()
    if conn:
        print("✅ MySQL 연결 성공! 이제 데이터를 넣을 준비가 되었습니다.")
        conn.close()
