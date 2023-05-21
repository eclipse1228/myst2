import pandas as pd
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import requests
import time
import concurrent.futures
import streamlit as st

# 폰트
font_location = 'NanumBarunGothicLight.ttf'
font_name = fm.FontProperties(fname=font_location).get_name()
plt.rc('font', family=font_name)
# 읽기
df_2021 = pd.read_csv('2021.csv')
df_2020 = pd.read_csv('2020.csv')
#
df_national_pension = list(sorted(set(df_2021['종목명']).intersection(set(df_2020['종목명']))))

# code.csv 파일
df_krx = pd.read_csv('code.csv')
df_krx = df_krx[['한글 종목약명', '단축코드']]
df_krx.rename(columns={'한글 종목약명': 'name', '단축코드': 'code'}, inplace=True)
df_krx['code'] = df_krx['code'].apply(lambda x: '{0:0>6}'.format(x))
df_krx = pd.DataFrame(df_krx)
df_code = df_krx.query(f"name in {df_national_pension}")
df_code = pd.DataFrame(df_code)
df_code = df_code.reset_index(drop=True)

## 수정된곳 ~ 74
# 0,1 웹크롤링
import requests


def get_url(item_name, df_code):
    code = df_code.query("name=='{}'".format(item_name))['code'].to_string(index=False)
    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)

    print("요청 URL = {}".format(url))
    return url


df_2021_price = pd.DataFrame()
df_2020_price = pd.DataFrame()
p = [59, 84]
for name in df_national_pension:
    url = get_url(name, df_code)

    header = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}
    # 일자 데이터를 담을 df라는 DataFrame 정의
    df_price = pd.DataFrame()

    # 1페이지에서 100페이지의 데이터만 가져오기
    for page in p:
        pg_url = '{url}&page={page}'.format(url=url, page=page)
        res = requests.get(pg_url, headers=header)
        df_price = pd.concat([df_price, pd.read_html(res.text, header=0, encoding='euc-kr')[0]], ignore_index=True)

    # df.dropna()를 이용해 결측값 있는 행 제거
    df_price = df_price.dropna()

    data = df_price[df_price['날짜'] == '2021.01.04']
    data.insert(0, 'name', name)
    df_2021_price = pd.concat([df_2021_price, data[['name', '종가']]], ignore_index=True)
    data = df_price[df_price['날짜'] == '2020.01.02']
    data.insert(0, 'name', name)
    df_2020_price = pd.concat([df_2020_price, data[['name', '종가']]], ignore_index=True)

pd.set_option('display.max_rows', 100)
df_result = pd.DataFrame()

# df_result['result'] = df_2021_price['종가'] > df_2020_price['종가']
#필요없는것 제거하기 ~ 77
df_2021_price = df_2021_price.drop(df_2021_price.index[df_2021_price['name']=='SK바이오팜'],axis=0)
df_2021_price = df_2021_price.reset_index(drop=True)

#streamlit - 국민연금 vs 코스피 1년 종가기준 수익률
# Plotting the bar graph
# 데이터 프레임 생성
df = pd.DataFrame({
    '지표': ['국민연금', '코스피'],
    '수익률': [45, 35]
})

# 그래프 그리기
plt.title('1년간 수익률 비교')
plt.bar(df['지표'], df['수익률'],color=['red','blue'])

# 축 레이블 설정
plt.xlabel('지표')
plt.ylabel('수익률')

# 그래프 출력
plt.show()

#streamlit
st.header("국민연금 비교 ")

# o,1 그래프 그리기 ~ 91
df_result = pd.DataFrame()
df_result['result'] = (df_2021_price['종가'] > df_2020_price['종가']).astype(int)

result_counts = df_result['result'].value_counts()

# Plotting the bar graph
plt.bar(result_counts.index, result_counts.values,color=['red', 'blue'])
plt.xlabel('Result')
plt.ylabel('Count')
plt.xticks([0, 1], ['Down', 'Up'])
plt.title('국민연금 1년 종가 기준')
plt.show()
#

def get_url(item_name, df_code):
    code = df_code.query("name=='{}'".format(item_name))['code'].to_string(index=False)
    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)
    return url


header = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}

###
st.title("국민연금투자 2020, 2021”)
st.header("국민연금 vs 코스피")


st.caption("국민연금의 투자종목은 투자금 비중이 높은 상위 10 % 종목으로 선별하였습니다.")

###


# Create a Session instance to keep connections open between requests
session = requests.Session()
session.headers = header


# This function will be run concurrently
def fetch_kospi(page):
    pg_url = f'https://finance.naver.com/sise/sise_index_day.naver?code=KOSPI&page={page}'
    res = session.get(pg_url)
    df_page = pd.read_html(res.text, header=0, encoding='euc-kr')[0]
    return df_page


def fetch_item(page, url):
    pg_url = f'{url}&page={page}'
    res = session.get(pg_url)
    df_page = pd.read_html(res.text, header=0, encoding='euc-kr')[0]
    return df_page


# 쓰레드 방식 data
df_kospi_price = pd.DataFrame()
with concurrent.futures.ThreadPoolExecutor() as executor:
    # fetch all pages concurrently
    futures = [executor.submit(fetch_kospi, page) for page in range(99, 141)]
    # as the results come in, append them to the DataFrame
    for future in concurrent.futures.as_completed(futures):
        df_page = future.result()
        df_kospi_price = pd.concat([df_kospi_price, df_page], ignore_index=True)

df_kospi_price = df_kospi_price.dropna()

for i in range(1, 31):
    df_kospi_price.drop(df_kospi_price[df_kospi_price['날짜'] == "2019.12.{0:0>2}".format(i)].index, inplace=True)
for i in range(5, 31):
    df_kospi_price.drop(df_kospi_price[df_kospi_price['날짜'] == '2021.01.{0:0>2}'.format(i)].index, inplace=True)

df_kospi_2021 = df_kospi_price[df_kospi_price['날짜'] == '2021.01.04']
df_kospi_2020 = df_kospi_price[df_kospi_price['날짜'] == '2020.01.02']

# Data 정렬 , 초기화
df_kospi_price = df_kospi_price.sort_index(ascending=False)
df_kospi_price = df_kospi_price.reset_index(drop=True)

########### streamlit ########
name = st.selectbox('종목선택', list(df_code['name']))
url = get_url(name, df_code)
df_price_item = pd.DataFrame()
###########  #################

with concurrent.futures.ThreadPoolExecutor() as executor:
    # fetch all pages concurrently
    futures = [executor.submit(fetch_item, page, url) for page in range(59, 85)]
    # as the results come in, append them to the DataFrame
    for future in concurrent.futures.as_completed(futures):
        df_page = future.result()
        df_price_item = pd.concat([df_price_item, df_page], ignore_index=True)

df_price_item = df_price_item.dropna()

##  여기까지 Data

for i in range(1, 31):
    df_price_item.drop(df_price_item[df_price_item['날짜'] == "2019.12.{0:0>2}".format(i)].index, inplace=True)
for i in range(5, 31):
    df_price_item.drop(df_price_item[df_price_item['날짜'] == '2021.01.{0:0>2}'.format(i)].index, inplace=True)

df_price_item = df_price_item.sort_index(ascending=False)
df_price_item = df_price_item.reset_index(drop=True)
df_kospi_price = df_kospi_price.sort_values('날짜')
df_price_item = df_price_item.sort_values('날짜')
df_kospi_price['price_normalization'] = df_kospi_price['체결가'] / abs(df_kospi_price['체결가'].max())
df_price_item['close_normalization'] = df_price_item['종가'] / abs(df_price_item['종가'].max())



# graph
plt.figure(figsize=(10, 4))
plt.plot(df_kospi_price['날짜'], df_kospi_price['price_normalization'], color='dodgerblue')
plt.xlabel('날짜')
plt.ylabel('close price')
plt.tick_params(
    axis='x',
    which='both',
    bottom=False,
    top=False,
    labelbottom=False)
plt.plot(df_price_item['날짜'], df_price_item['close_normalization'], color='orange')
plt.tick_params(
    axis='x',
    which='both',
    bottom=False,
    top=False,
    labelbottom=False)
variable_x = mpatches.Patch(color='dodgerblue', label='KOSPI')
variable_y = mpatches.Patch(color='orange', label=name)
plt.legend(handles=[variable_x, variable_y], loc='lower left')
plt.title(f'KOSPI/{name} Graph')

st.pyplot(plt)
