import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dbconnect import connect_to_postgres
 

def crawl_ev_situation():

    # 도시 코드 매핑 딕셔너리
    code_mapping = {
        '서울': 1,
        '부산': 2,
        '대구': 3,
        '인천': 4,
        '광주': 5,
        '대전': 6,
        '울산': 7,
        '세종': 8,
        '경기': 9,
        '강원': 10,
        '충북': 11,
        '충남': 12,
        '전북': 13,
        '전남': 14,
        '경북': 15,
        '경남': 16,
        '제주': 17
    }

    url = 'https://chargeinfo.ksga.org/front/statistics/evCar'
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)

    bs4 = BeautifulSoup(driver.page_source, 'lxml')

    thead = bs4.select('table.datatable thead th')
    locations = [column.text for column in thead]
    print(locations[1:-1])
    tr = bs4.select('table.datatable tbody tr')
    
    conn = connect_to_postgres()
    if conn != None:
        for city in locations[1:-1]:
            city_name = city
            mapped_code = code_mapping.get(city_name, city_name)

            try:    
                cur = conn.cursor()
                cur.execute(f"INSERT INTO city_table (city_code, city_name) VALUES ('{mapped_code}', '{city}');")
                conn.commit() # CREATE    
            except Exception as e:
                print(f"{mapped_code}', '{city}: {e}")
                pass

    if conn != None:
        for row in tr:
            data = row.select('td')
            for idx in range(len(data)):
                # 첫번째 칼럼은 연도
                if idx == 0:
                    year = data[0].text[0:4]
                    continue
                # 마지막 칼럼(합계)은 필요없으므로 제외
                elif idx == 18:
                    continue
                # 그 외의 값 INSERT 하기
                else:
                    # 데이터에서 (???) 붙어있는 거 제거하기
                    if data[idx].text.__contains__('('):
                        split_data = data[idx].text.split('(')[0]
                    else:
                        split_data = data[idx].text

                    # 데이터에서 ,제거하기
                    split_data = split_data.replace(',','')
                    #print(locations[idx], year, split_data)
                    city_name = locations[idx]
                    mapped_code = code_mapping.get(city_name, city_name)

                    try:    
                        cur = conn.cursor()
                        cur.execute(f"INSERT INTO situation_table (situation_city, situation_year, situation_amount) VALUES ('{mapped_code}', '{year}', '{split_data}');")
                        conn.commit() # CREATE
                    except Exception as e:
                        print(f"{mapped_code}, {year}, {split_data}: {e}")
                        pass

                    