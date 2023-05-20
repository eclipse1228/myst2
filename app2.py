import pandas as pd
import matplotlib.pyplot as plt


df_2021 = pd.read_csv('2021.csv')
df_2020 = pd.read_csv('2020.csv')

df_national_pension = list(sorted(set(df_2021['종목명']).intersection(set(df_2020['종목명']))))
print(df_national_pension)

df_krx = pd.read_csv('code.csv')
df_krx = df_krx[['한글 종목약명', '단축코드']]
df_krx.rename(columns={'한글 종목약명':'name','단축코드':'code'},inplace=True)

df_krx['code'] = df_krx['code'].astype(str).str.zfill(6)

df_krx = pd.DataFrame(df_krx)
df_code = df_krx.query(f"name in {df_national_pension}")
df_code = pd.DataFrame(df_code)

pip install lxml
pip install html5lib
pip install requests

import requests

def get_url(item_name, df_code):
    code = df_code.query("name=='{}'".format(item_name))['code'].to_string(index=False)
    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)
    
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
    data = df_price[df_price['날짜'] == '2020.01.02']
    data.insert(0,'name',name)
    df_2020_price = pd.concat([df_2020_price,data[['name','종가']]],ignore_index=True)


pd.set_option('display.max_rows',100)
df_result = pd.DataFrame()
# df_result['result'] = df_2021_price['종가'] > df_2020_price['종가']

df_2021_price = df_2021_price.drop(df_2021_price.index[df_2021_price['name']=='SK바이오팜'],axis=0)
df_2021_price = df_2021_price.reset_index(drop=True)



df_result = pd.DataFrame()
df_result['result'] = (df_2021_price['종가'] > df_2020_price['종가']).astype(int)

result_counts = df_result['result'].value_counts()

# Plotting the bar graph
plt.bar(result_counts.index, result_counts.values,color=['red', 'blue'])
plt.xlabel('Result')
plt.ylabel('Count')
plt.xticks([0, 1], ['Down', 'Up'])
plt.title('Comparison Result')
plt.show()
