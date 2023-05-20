
# 국민연금 2020, 2021 종목 자료 읽기
import pandas as pd
import matplotlib.pyplot as plt

df_2021 = pd.read_csv('2021.csv')
df_2020 = pd.read_csv('2020.csv')
#

# 
df_krx = pd.read_csv('code.csv')                      # code.csv 파일은 한국 전체 주식종목 정보
df_krx = df_krx[['한글 종목약명', '단축코드']]          
df_krx.rename(columns={'한글 종목약명':'name','단축코드':'code'},inplace=True) # rename 하기 

df_krx['code'] = df_krx['code'].astype(str).str.zfill(6) # zfill은 6자리로 구간을 넓히는것 빈자리는 0으로 채움 # , # astype(str) string 형식으로 변경 #
df_krx = pd.DataFrame(df_krx)                            #  DataFrame으로~       
df_code = df_krx.query(f"name in {df_national_pension}") # df_code에 df_krx에 df_national_pension의 name을 query함수 사용해서, 교집합을 찾아서 df_code 만든다.
df_code = pd.DataFrame(df_code)                          # DataFrame으로 만들기
#

# 다운로드
pip install lxml
pip install html5lib
pip install requests
#

# 웹 크롤링 
import requests

def get_url(item_name, df_code):                        # item_name과 df_code*name
    code = df_code.query("name=='{}'".format(item_name))['code'].to_string(index=False)
    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)    # 웹 크롤링하기
    
    print("요청 URL = {}".format(url))
    return url
   
df_2021_price = pd.DataFrame()
df_2020_price = pd.DataFrame()
p = [59,84]
for name in df_national_pension:
    url = get_url(name, df_code)

    header = {"User-Agent" : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}
    # 일자 데이터를 담을 df라는 DataFrame 정의
    df_price = pd.DataFrame() 
    
    # 1페이지에서 100페이지의 데이터만 가져오기
    for page in p:
        pg_url = '{url}&page={page}'.format(url=url, page=page)
        res = requests.get(pg_url, headers=header)
        df_price = pd.concat([df_price,pd.read_html(res.text, header=0,encoding='euc-kr')[0]], ignore_index=True)
    
    
    # df.dropna()를 이용해 결측값 있는 행 제거
    df_price = df_price.dropna()
    
    data = df_price[df_price['날짜'] == '2021.01.04']
    data.insert(0,'name',name)
    df_2021_price = pd.concat([df_2021_price,data[['name','종가']]],ignore_index=True)
    print(data)
    data = df_price[df_price['날짜'] == '2020.01.02']
    data.insert(0,'name',name)
    df_2020_price = pd.concat([df_2020_price,data[['name','종가']]],ignore_index=True)


pd.set_option('display.max_rows',100)
df_result = pd.DataFrame()
# df_result['result'] = df_2021_price['종가'] > df_2020_price['종가']

