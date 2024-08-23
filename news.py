import pandas as pd
import json
import requests
import psycopg2
from datetime import datetime
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from tqdm import tqdm
from dbconnect import connect_to_postgres

# 전기차 관련 뉴스 크롤링
def crawl_ev_news():
    url = f"https://www.evpost.co.kr/wp/category/%eb%89%b4%ec%8a%a4/"
    response = requests.get(url, headers={'user-agent':'Mozilla 5.0'})

    # URL이 유효하다면, 성공
    if response.status_code == 200:
        bs4 = BeautifulSoup(response.text, 'lxml')
        
        #이미지 주소/제목/날짜/내용 크롤링
        image = bs4.select('div#tdi_18 div div div.td-image-container div.td-module-thumb a span')
        titles = bs4.select('div#tdi_18 div div div h3')
        dates = bs4.select('div#tdi_18 div div div div.td-editor-date')    
        contents = bs4.select('div#tdi_18 div div div div.td-excerpt')

        #이미지 주소/제목/날짜/내용 리스트에 저장
        images = [img.get('style').replace('background-image: url(','').replace(')','') for img in image if img.get('style') != None]
        titles = [title.text.replace('\'',"\"") for title in titles]
        dates = [datetime.strptime(date.text.strip(), "%Y.%m.%d").strftime("%Y-%m-%d %H:%M:%S") for date in dates]
        contents = [content.text.strip().replace('\'',"\"") for content in contents]

        #뉴스 개수 만큼 DB에 INSERT문 실행
        length = len(image)
        for idx in range(length):
            #print(images[idx][0:10], titles[idx][0:10], dates[idx], contents[idx][0:10], sep='\t')
            try:
                conn = connect_to_postgres()
                cur = conn.cursor()
                cur.execute(f"INSERT INTO news_table (news_image, news_title, news_date, news_content) VALUES ('{images[idx]}', '{titles[idx]}', '{dates[idx]}', '{contents[idx]}');")
                conn.commit() # CREATE
                pass
            except Exception as e:
                print(f"Cannot insert values into the database: {e}")
                pass
   