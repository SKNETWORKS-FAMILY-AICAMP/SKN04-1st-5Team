import streamlit as st
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import numpy as np
import platform

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


def st_situation():
    # 데이터베이스 연결 설정
    engine = create_engine(
        'postgresql+psycopg2://postgres:12341234@postgresdb.cf6o4ug4a4vh.ap-northeast-2.rds.amazonaws.com:5432/skai1stpj',
        connect_args={'options': '-c client_encoding=UTF8'}
    )

    # SQL 쿼리를 통해 데이터 불러오기
    with engine.connect() as conn:
        query = """
        SELECT b.city_name, a.situation_city, a.situation_year, a.situation_amount
        FROM situation_table a
        JOIN city_table b ON a.situation_city = b.city_code
        """
        df = pd.read_sql_query(query, conn)

    # Streamlit 제목
    st.title("전기차 등록 현황")

    # 도시별로 데이터 그룹화
    cities_grouped = df.groupby('city_name')

    # 그래프 설정
    fig, ax = plt.subplots(figsize=(12, 8))

    # 색상 팔레트 선택 (tab20 사용: 20개의 고유 색상 제공)
    colors = plt.cm.tab20.colors

    # 도시별로 색상을 지정하며 그래프 그리기
    for i, (city, group) in enumerate(cities_grouped):
        color = colors[i % len(colors)]  # 색상이 반복되지 않도록 설정
        ax.plot(group['situation_year'], group['situation_amount'], marker='o', label=city, color=color)

    # 그래프 라벨 및 타이틀 설정
    ax.set_xlabel('연도')
    ax.set_ylabel('전기차 수량')
    #ax.set_title('Situation Amounts by City Over the Years')
    ax.legend(title="City", bbox_to_anchor=(1.05, 1), loc='upper left')  # 범례를 그래프 외부에 배치

    # Streamlit에 그래프 표시
    st.pyplot(fig)

    # 최종 데이터프레임 출력 (선택사항)
    st.write("전체 데이터", df)


def st_charger():
    # 한글 폰트 설정
    if platform.system() == 'Windows':
        font_path = 'C:/Windows/Fonts/malgun.ttf'  # Windows에서 사용하는 한글 폰트 경로
        font_name = font_manager.FontProperties(fname=font_path).get_name()
        rc('font', family=font_name)
    elif platform.system() == 'Darwin':  # macOS
        rc('font', family='AppleGothic')
    else:  # Linux (예: Ubuntu)
        rc('font', family='NanumGothic')

    plt.rcParams['axes.unicode_minus'] = False  # 한글 폰트 사용 시 마이너스(-) 기호 깨짐 방지

    # PostgreSQL 연결 설정
    engine = create_engine('postgresql+psycopg2://postgres:12341234@postgresdb.cf6o4ug4a4vh.ap-northeast-2.rds.amazonaws.com:5432/skai1stpj')

    # 데이터 로드
    query = "SELECT charger_city AS 도시, COUNT(*) as 충전소수 FROM charger_info GROUP BY charger_city ORDER BY 충전소수 DESC;"
    df = pd.read_sql(query, engine)

    # 인덱스를 1부터 시작하도록 설정
    df.index = df.index + 1

    # Streamlit 앱 작성
    st.title('도시별 충전소 보급 현황')

    # 시도별 데이터 막대 그래프 (COUNT 순으로 정렬)
    df_sorted = df.set_index('도시').sort_values('충전소수', ascending=False)

    # 색상 설정: 상위 7개 도시는 지정된 색상, 나머지는 회색 계열 (흰색 제외)
    top_colors = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#4B0082', '#8B00FF']  # 빨, 주, 노, 초, 파, 남, 보
    gray_grad = [plt.cm.Greys(i / (len(df_sorted) - 7 + 1)) for i in range(1, len(df_sorted) - 7 + 1)]  # 흰색 제외

    # 모든 도시의 색상 리스트 생성
    colors = top_colors + gray_grad

    # matplotlib을 사용하여 그래프 생성
    fig, ax = plt.subplots()
    bars = ax.bar(df_sorted.index, df_sorted['충전소수'], color=colors)
    ax.set_xlabel('도시')
    ax.set_ylabel('충전소 수')
    ax.set_title('광역시/도별 전기차 충전소 설치 현황')

    # 레이블 위치 조정 (간격 조정)
    ax.set_xticks(range(len(df_sorted.index)))
    ax.set_xticklabels(df_sorted.index, rotation=0, ha='center', fontsize=10)

    # 막대와 레이블 사이 간격 조정
    ax.margins(y=0.1)  # y축(막대와 레이블) 간의 간격을 조정

    st.pyplot(fig)

    # 테이블을 Expander로 감싸서 fold 기능 제공
    with st.expander("시도별 충전소 수 (내림차순으로 정렬)"):
        st.write("### 시도별 충전소 수 (내림차순으로 정렬)")
        st.table(df)


def st_news():
    try:
        conn = connect_to_postgres()
        query = """
                SELECT news_index, news_title, news_content, DATE(news_date) AS news_date, news_image 
                FROM public.news_table
                ORDER BY news_date DESC
                LIMIT 10
                """
        df = pd.read_sql(query, conn)
        conn.close()
        data = df
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        data = pd.DataFrame()

    # Streamlit 인터페이스 구성
    st.title("최신 EV 뉴스")

    for index, row in data.iterrows():
        cols = st.columns([1, 3])  # 첫 번째 컬럼은 이미지, 두 번째 컬럼은 텍스트
        
        with cols[0]:
            if row['news_image']:
                st.image(row['news_image'], width=150)  # 이미지 너비 조절
        
        with cols[1]:
            st.subheader(row['news_title'])
            st.text(row['news_date'])
            st.write(row['news_content'])
        
        st.markdown("---")


def st_faq():
    conn = connect_to_postgres()
    cur = conn.cursor()
    cur.execute("SELECT * FROM faq_table;")
    conn.commit() # CREATE
    rows = cur.fetchall()

    st.title(f"자주 하는 질문 FAQ")

    # FAQ 크롤링 데이터를 출력
    for row in rows:
        index = row[0]
        title = row[1]
        content = row[2]
        with st.expander(f"**{title}**"):
            st.write(f"{content}")


def show_streamlit():
    # 한글 폰트 깨짐 방지용 코드
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False  # 마이너스 폰트 깨짐 방지

    # 페이지 상태를 세션 상태로 관리
    if 'page' not in st.session_state:
        st.session_state.page = "situation"  # 기본값: Home 페이지

    # 사이드바에 링크 목록 표시
    st.sidebar.markdown("<h1 style='font-size: 20px;'>전기차 보급 대비 인프라 구축</h1>", unsafe_allow_html=True)

    if st.sidebar.button("전기차 등록 현황"):
        st.session_state.page = "situation"
    if st.sidebar.button("전기차 충전소 현황"):
        st.session_state.page = "charger"
    if st.sidebar.button("전기차 관련 최신 뉴스"):
        st.session_state.page = "news"
    if st.sidebar.button("전기차 관련 기업 FAQ"):
        st.session_state.page = "faq"

    # 선택된 페이지에 따른 콘텐츠 표시
    if st.session_state.page == "situation":
        st_situation()
    elif st.session_state.page == "charger":
        st_charger()
    elif st.session_state.page == "news":
        st_news()
    elif st.session_state.page == "faq":
        st_faq()