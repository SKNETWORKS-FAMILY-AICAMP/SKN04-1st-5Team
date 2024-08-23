# 모든 모듈들과 연결할 메인 코드

from dbconnect import *
from faq_module import make_faq_data
from situation import crawl_ev_situation
from news import crawl_ev_news
from ev_charging_crawling import crawl_ev_charging
from lit import show_streamlit


# 테이블 데이터 모두 삭제하는 코드
#delete_table()

# 페이지 구성에 필요한 데이터들을 크롤링한 다음,
# 데이터베이스의 각 테이블에 데이터들을 연동시키기
#crawl_ev_situation()
#######crawl_ev_charging()

#make_faq_data()
#crawl_ev_news()

# 데이터베이스에서 데이터들을 불러와서 streamlit을 이용해 페이지 출력
show_streamlit()


