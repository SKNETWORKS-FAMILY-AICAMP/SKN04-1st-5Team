import requests
import pandas as pd
from sqlalchemy import create_engine, text

def crawl_ev_charging():
    # PostgreSQL 연결 설정
    engine = create_engine('postgresql+psycopg2://postgres:12341234@postgresdb.cf6o4ug4a4vh.ap-northeast-2.rds.amazonaws.com:5432/skai1stpj')

    # API 엔드포인트 및 요청 URL
    api_url = "https://api.odcloud.kr/api/15122175/v1/uddi:94d1c01d-6d2b-4247-9b3e-d40da405ba44"

    # 서비스키 설정
    service_key = "dhh9rG0Obg6GF/8NtLMoZn1RFRn96Cksyj5kq5FtkxNKrQN262Z4rztwOf/7qkLpsLawIkfzAbOFvI+lcStE3A=="

    # 도시 이름 매핑 딕셔너리
    city_mapping = {
        '서울특별시': '서울',
        '부산광역시': '부산',
        '대구광역시': '대구',
        '인천광역시': '인천',
        '광주광역시': '광주',
        '대전광역시': '대전',
        '울산광역시': '울산',
        '세종특별자치시': '세종',
        '경기도': '경기',
        '강원도': '강원',
        '충청북도': '충북',
        '충청남도': '충남',
        '전라북도': '전북',
        '전라남도': '전남',
        '경상북도': '경북',
        '경상남도': '경남',
        '제주특별자치도': '제주'
    }

    # 첫 번째 페이지부터 시작
    page = 1
    per_page = 100
    all_data = []

    while True:
        # 요청 파라미터 설정
        params = {
            'serviceKey': service_key,
            'page': page,
            'perPage': per_page,
            'returnType': 'JSON'
        }

        # API 호출
        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            data = response.json()
            new_data = data['data']
            if not new_data:
                break

            for record in new_data:
                # 도시 이름 변환
                original_city = record['시도']
                mapped_city = city_mapping.get(original_city, original_city)

                # 데이터 삽입 전 중복 검사
                with engine.connect() as conn:
                    query = text("SELECT 1 FROM charger_info WHERE charger_name = :charger_name")
                    result = conn.execute(query, {'charger_name': record['충전소명']}).fetchone()

                    if not result:
                        insert_query = text("""
                            INSERT INTO charger_info (charger_city, charger_name) 
                            VALUES (:charger_city, :charger_name)
                        """)
                        conn.execute(insert_query, {
                            'charger_city': mapped_city,
                            'charger_name': record['충전소명']
                        })
                        conn.commit()
                        print(f"Inserted: {record['충전소명']}")

            print(f"Page {page} loaded and processed.")

            # 중간에 데이터베이스에 저장된 데이터 확인
            with engine.connect() as conn:
                check_query = text("SELECT * FROM charger_info LIMIT 5;")
                result_df = pd.read_sql(check_query, conn)
                print("Database check (first 5 rows):")
                print(result_df)

            page += 1

        else:
            print(f"Error: {response.status_code} - {response.text}")
            break

    print("Data loading completed.")
