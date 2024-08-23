from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import dbconnect

# make_faq_data() 를 콜해서 사용

def faq_page_data(driver, faq_title_list, faq_content_list):
    print('page call')
    # 전기차 관련 내용이 찾아질때까지 대기
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '전기차')]"))
    )
    bs = BeautifulSoup(driver.page_source, 'lxml')
    # faq title 가져오기
    faq_title_temp = bs.select('span.cmp-accordion__title') 
    faq_title_list.extend( [ title.text.strip() for title in faq_title_temp] ) #함수로 활용하기 위해 기본 리스트 생성후 extend

    # faq content 가저오기
    faq_content_temp = bs.select('div.faqinner__wrap div')
    faq_content_list.extend([ #함수로 활용하기 위해 기본 리스트 생성후 extend
        result.text.strip().replace('\xa0', ' ').replace('\n', '\n\n') 
        for result 
        in faq_content_temp 
        if result.text.strip()
    ])
    return faq_title_list, faq_content_list
        
def make_faq_data(): 
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url="https://www.kia.com/kr/customer-service/center/faq") 
    # faq 사이트로 이동후 '전기차' 를 검색
    search_xpath = '//*[@id="searchName"]'
    searchbar = driver.find_element(By.XPATH, search_xpath)
    searchbar.send_keys('전기차')
    searchbar.send_keys(Keys.ENTER)
    page_info = 1 # 현재 페이지 정보
    faq_title_list = [] # 전기차 faq title 를 list로 저장
    faq_content_list = [] # 전기차 faq title 를 list로 저장
    faq_list = []

    while True: # 예외가 발생할때까지(다음페이지가 없을때까지)
        faq_title_list, faq_content_list = faq_page_data(driver, faq_title_list, faq_content_list)
        page_info += 1
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{page_info}')]"))).click()
        except:
            print('data')
            break

    # faq_title_list 와 faq_content_list 를 활용하여 순서대로 딕셔너리를 작성
    faq_list = ([
        {"faq_title": title, "faq_content": content} 
        for title, content 
        in zip(faq_title_list, faq_content_list)]
    )
    # db연결
    conn = dbconnect.connect_to_postgres()
    cur = conn.cursor()
    # 데이터 삽입
    for faq in faq_list:
        cur.execute(
            "INSERT INTO faq_table (faq_title, faq_content) VALUES (%s, %s)",
            (faq.get('faq_title'), faq.get('faq_content'))
        )
    # 변경사항 저장
    conn.commit()