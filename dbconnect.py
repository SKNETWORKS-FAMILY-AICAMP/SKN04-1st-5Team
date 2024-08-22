import psycopg2

# PostgreSQL 연결 설정
def connect_to_postgres():
    try:
        conn = psycopg2.connect(
            # aws 와 연동하여 db연걸
            host="postgresdb.cf6o4ug4a4vh.ap-northeast-2.rds.amazonaws.com",  # RDS 엔드포인트
            port="5432",                             # 기본 포트는 5432입니다.
            database="skai1stpj",           # 데이터베이스 이름
            user="postgres",                    # 사용자 이름
            password="12341234"                 # 비밀번호
        )
        print("Connected to the database successfully")
        return conn
    except Exception as e:
        print(f"Unable to connect to the database: {e}")
        return None