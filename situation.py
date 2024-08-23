import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dbconnect import connect_to_postgres
 

def crawl_ev_situation():
    url = 'https://chargeinfo.ksga.org/front/statistics/evCar'
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)

    bs4 = BeautifulSoup(driver.page_source, 'lxml')

    thead = bs4.select('table.datatable thead th')
    locations = [column.text for column in thead]
    tr = bs4.select('table.datatable tbody tr')

    conn = connect_to_postgres()
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

                    try:    
                        cur = conn.cursor()
                        # cur.execute(f"INSERT INTO situation_table (situation_city, situation_year, situation_amount) VALUES ('{locations[idx]}', '{year}', '{split_data}');")
                        conn.commit() # CREATE    
                    except Exception as e:
                        print(f"Cannot insert values into the database: {e}")
                        pass