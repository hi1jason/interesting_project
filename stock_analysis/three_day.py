from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, Table, Column, MetaData, Integer, String, DATE, FLOAT, INT
import tushare as ts
import math

DAY_NEM = 5

def get_data():
    # 连接数据库
    engine = create_engine('mysql+pymysql://root:wxj555@127.0.0.1/my_db?charset=utf8')
    metadata = MetaData()
    # 定义表
    p_change = Table('p_change', metadata,
                     Column('index', Integer, nullable=False),
                     Column('date', DATE, nullable=False),
                     Column('volume', FLOAT, nullable=True),
                     Column('p_change', FLOAT, nullable=True),
                     Column('turnover', FLOAT, nullable=True),
                     Column('code', String(10), nullable=True)
                     )
    # 初始化数据库
    metadata.create_all(engine)
    # 获取数据库连接
    conn = engine.connect()
    conn.execute("delete from p_change")
    r1 = conn.execute('select * from stock_basics where timeToMarket!=0000-00-00')
    res = r1.fetchall()
    for x in res:
        code = x[0]
        print(code)
        date_str = str(x[3])
        date_to_market = datetime.strptime(date_str, "%Y-%m-%d")
        date_rule = datetime.strptime("2017-02-27", "%Y-%m-%d")
        if (date_to_market < date_rule):
            df = ts.get_hist_data(code, start='2015-10-01', end='2017-03-10')
            df = df[['p_change', 'volume', 'turnover']]
            df.reset_index(level=0, inplace=True)
            df.reset_index(level=0, inplace=True)
            df['code'] = code
            dict = df.to_dict(orient='records')
            # conn.execute("delete from p_change")
            r = conn.execute(p_change.insert(), dict)

def analysis():

    engine = create_engine('mysql+pymysql://root:wxj555@127.0.0.1/my_db?charset=utf8')
    conn = engine.connect()
    r1 = conn.execute('select * from stock_basics where timeToMarket!=0000-00-00')
    res = r1.fetchall()

    for x in res:
        code=x[0]
        a_list = []
        r2 = conn.execute('select * from p_change where code='+code)
        res1 = r2.fetchall()
        if (len(res1)==0):
            continue
        for y in res1:
            dict = {'date': y[1], 'p_change': y[3],'index':y[0]}
            a_list.append(dict)
        df = pd.DataFrame(a_list)
        df.sort_values(by='index', inplace=True)
        r_list = []
        for i in range(0, 10000):
            index = -1 * i
            df_shift = df.shift(index).head(DAY_NEM)
            if (math.isnan(df_shift.ix[DAY_NEM - 1, 1])):
                break
            else:
                sum = df_shift.sum()
                dict = {'date': str(df_shift.ix[0,0]), 'p_change': sum.p_change}
                r_list.append(dict)
        df = pd.DataFrame(r_list)
        df['code']=code
        df.sort_values(by='p_change', ascending=False, inplace=True)
        print(df)

if __name__ == '__main__':
    analysis()

