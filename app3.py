import pandas as pd
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import requests
import streamlit as st
from io import BytesIO
from pathlib import Path


font_location = 'NanumBarunGothicLight.ttf'
font_name = fm.FontProperties(fname=font_location).get_name()
plt.rc('font', family=font_name)
df_2021 = pd.read_csv('2021.csv')
df_2020 = pd.read_csv('2020.csv')

df_national_pension = list(sorted(set(df_2021['종목명']).intersection(set(df_2020['종목명']))))

df_krx = pd.read_csv('code.csv')
df_krx = df_krx[['한글 종목약명', '단축코드']]
df_krx.rename(columns={'한글 종목약명':'name','단축코드':'code'},inplace=True)
df_krx['code'] = df_krx['code'].apply(lambda x : '{0:0>6}'.format(x))
df_krx = pd.DataFrame(df_krx)
df_code = df_krx.query(f"name in {df_national_pension}")
df_code = pd.DataFrame(df_code)
df_code = df_code.reset_index(drop=True)


def get_url(item_name, df_code):
    code = df_code.query("name=='{}'".format(item_name))['code'].to_string(index=False)
    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)
    return url
   
header = {"User-Agent" : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}


#  1. 코스피 데이터 크롤링
# 데이터 크롤링해서 데이터프레임 만들기 df_kospi_price
import pandas as pd

# 빈 DataFrame인 df_kospi_price 생성
df_kospi_price = pd.DataFrame()

# 99부터 140까지의 페이지에 접속하여 데이터를 가져옴
for page in range(99, 141):
    # 페이지 URL 생성
    pg_url = 'https://finance.naver.com/sise/sise_index_day.naver?code=KOSPI&page={page}'.format(page=page)
    # GET 요청 보내고 HTML 데이터 받음
    res = requests.get(pg_url, headers=header)
    # HTML 데이터에서 가격 데이터 추출하여 DataFrame에 추가
    df_kospi_price = pd.concat([df_kospi_price, pd.read_html(res.text, header=0, encoding='euc-kr')[0]], ignore_index=True)
    # 빈 값이 있는 행 제거
    df_kospi_price = df_kospi_price.dropna()

# 1부터 30까지의 일자에 해당하는 행 제거 (2019년 12월 1일부터 30일까지, 2021년 1월 5일부터 30일까지)
for i in range(1, 31):
    df_kospi_price.drop(df_kospi_price[df_kospi_price['날짜'] == "2019.12.{0:0>2}".format(i)].index, inplace=True)
for i in range(5, 31):
    df_kospi_price.drop(df_kospi_price[df_kospi_price['날짜'] == '2021.01.{0:0>2}'.format(i)].index, inplace=True)

# '2021.01.04'와 '2020.01.02' 날짜에 해당하는 행 추출하여 df_kospi_2021과 df_kospi_2020에 저장
df_kospi_2021 = df_kospi_price[df_kospi_price['날짜'] == '2021.01.04']
df_kospi_2020 = df_kospi_price[df_kospi_price['날짜'] == '2020.01.02']


# DataFrame 정렬 및 초기화 ~70
# DataFrame을 날짜를 기준으로 내림차순으로 정렬
df_kospi_price = df_kospi_price.sort_index(ascending=False)
# DataFrame의 인덱스를 재설정
df_kospi_price = df_kospi_price.reset_index(drop=True)



# 빈 DataFrame인 df_2021_price_item과 df_2020_price_item 생성
df_2021_price_item = pd.DataFrame()
df_2020_price_item = pd.DataFrame()

# 사용자가 선택한 종목명을 가져옴
name = st.selectbox('종목선택', list(df_code['name']))
# 해당 종목의 URL을 가져옴
url = get_url(name, df_code)
df_price_item = pd.DataFrame()

# fetch_data 함수 정의
def fetch_data(page):
    pg_url = '{url}&page={page}'.format(url=url, page=page)
    return get_data(pg_url)

# 멀티프로세스를 사용하여 데이터 가져오기
with concurrent.futures.ProcessPoolExecutor() as executor:
    pages = range(59, 85)
    results = executor.map(fetch_data, pages)

# 가져온 데이터 병합
for result in results:
    df_price_item = pd.concat([df_price_item, result], ignore_index=True)


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    #드롭
df_price_item = df_price_item.dropna()




# 1부터 30까지의 일자에 해당하는 행 제거 (2019년 12월 1일부터 30일까지, 2021년 1월 5일부터 30일까지)
for i in range(1, 31):
    df_price_item.drop(df_price_item[df_price_item['날짜'] == "2019.12.{0:0>2}".format(i)].index, inplace=True)
for i in range(5, 31):
    df_price_item.drop(df_price_item[df_price_item['날짜'] == '2021.01.{0:0>2}'.format(i)].index, inplace=True)

    
    
    
    
    
    
    
    
    
    
    
# DataFrame을 날짜를 기준으로 내림차순으로 정렬
df_price_item = df_price_item.sort_index(ascending=False)
# DataFrame의 인덱스를 재설정
df_price_item = df_price_item.reset_index(drop=True)

# df_kospi_price의 '체결가' 값을 최댓값으로 나누어 '체결가_normalization' 열 생성
df_kospi_price['체결가_normalization'] = df_kospi_price['체결가'] / abs(df_kospi_price['체결가'].max())
# df_price_item의 '종가' 값을 최댓값으로 나누어 '종가_normalization' 열 생성
df_price_item['종가_normalization'] = df_price_item['종가'] / abs(df_price_item['종가'].max())


# 그래프 그리기 ~132
plt.figure(figsize=(10,4))
plt.plot(df_kospi_price['날짜'], df_kospi_price['체결가_normalization'],color='dodgerblue')
plt.xlabel('날짜')
plt.ylabel('종가')
plt.tick_params(
    axis='x',
    which='both',
    bottom=False,
    top=False,
    labelbottom=False)

plt.plot(df_price_item['날짜'], df_price_item['종가_normalization'],color='orange')
plt.tick_params(
    axis='x',
    which='both',
    bottom=False,
    top=False,
    labelbottom=False)

variable_x = mpatches.Patch(color='dodgerblue',label='KOSPI')
variable_y = mpatches.Patch(color='orange',label=name)
plt.legend(handles=[variable_x, variable_y],loc='lower left')
plt.title(f'KOSPI/{name} 그래프')
st.pyplot(plt)
