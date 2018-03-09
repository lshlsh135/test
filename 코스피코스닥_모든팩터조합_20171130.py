# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 15:50:36 2017

@author: SH-NoteBook
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 13:27:10 2017

raw_data['sales_cap']=raw_data['SALES']/raw_data['MARKET_CAP']
raw_data['gpro_cap']=raw_data['GROSS_PROFIT']/raw_data['MARKET_CAP']
raw_data['opro_cap']=raw_data['OPE_PROFIT']/raw_data['MARKET_CAP'] # 이놈 시총제한 있고 없고 차이 심한데 
얘네는 계절성때문에 제외

@author: SH-NoteBook
"""


import pandas as pd
import numpy as np
import cx_Oracle
#from result_calculator import result_calculator
from result_calculator import result_calculator
from QVGSM import QVGSM
from QVGSM_sector import QVGSM_sector
import itertools

#이거 두개 반드시 선언!
cx0=cx_Oracle.makedsn("localhost",1521,"xe")
connection = cx_Oracle.connect("lshlsh135","2tkdgns2",cx0) #이게 실행이 안될때가 있는데
#그때는 services에 들어가서 oracle listner를 실행시켜줘야함
cpi_data = pd.read_sql("""select * from cpi""",con=connection)
kospi_day = pd.read_sql("""select * from kospi_day_prc_20171130""",con=connection) # 코스피 일별 종가
kospi_day.set_index('TRD_DATE',inplace=True)
kospi_quarter = pd.read_sql("""select * from kospi_quarter_return_20171130""",con=connection)
kospi_month = pd.read_sql("""select * from kospi_month_return_20171130""",con=connection)
#DATA를 가져온다!!
kospi = pd.read_sql("""select trd_date, gicode, co_nm,iskosdaq, wics_mid,cap_size,EQUITY,CFO_TTM,cash_div_com,SALES_TTM,ADJ_NI_12M_FWD,market_cap,adj_prc, asset,asset + 0.1*(market_cap/1000 -equity) as adjasset,asset - equity as liab,ni,liq_equity,liq_debt,(NI-lag(ni,3) over(partition by gicode order by trd_date))/ (ABS(ni) + abs(lag(ni,3) over(partition by gicode order by trd_date))) as chin,lag(ni,12) over(partition by gicode order by trd_date) as ni_1y, gross_profit_ttm ,
                    (gross_profit_ttm-lag(gross_profit_ttm,60) over(partition by gicode order by trd_date))/lag(asset,60) over(partition by gicode order by trd_date) as D5GPOA,
                    (ni-lag(ni,60) over(partition by gicode order by trd_date))/lag(equity,60) over(partition by gicode order by trd_date) as D5ROE,
                    (ni-lag(ni,60) over(partition by gicode order by trd_date))/lag(asset,60) over(partition by gicode order by trd_date) as D5ROA,
                    (cfo_ttm-lag(cfo_ttm,60) over(partition by gicode order by trd_date))/lag(asset,60) over(partition by gicode order by trd_date) as D5CFOA,
                    (gross_profit_ttm-lag(gross_profit_ttm,60) over(partition by gicode order by trd_date))/lag(sales_ttm,60) over(partition by gicode order by trd_date) as D5GMAR,
                    (ni -lag(ni,60) over(partition by gicode order by trd_date)- cfo_ttm+ lag(cfo_ttm,60) over(partition by gicode order by trd_date))/lag(asset,60) over(partition by gicode order by trd_date) as D5ACC,
                    adj_prc/lag(adj_prc,12) over(partition by gicode order by trd_date) rtn_12m
                    from kospi_20171130""",con=connection)
kosdaq = pd.read_sql("""select trd_date, gicode, co_nm,iskosdaq, wics_mid,cap_size,EQUITY,CFO_TTM,cash_div_com,SALES_TTM,ADJ_NI_12M_FWD,market_cap,adj_prc, asset,asset + 0.1*(market_cap/1000 -equity) as adjasset,asset - equity as liab,ni,liq_equity,liq_debt,(NI-lag(ni,3) over(partition by gicode order by trd_date))/ (ABS(ni) + abs(lag(ni,3) over(partition by gicode order by trd_date))) as chin,lag(ni,12) over(partition by gicode order by trd_date) as ni_1y, gross_profit_ttm,
                     (gross_profit_ttm-lag(gross_profit_ttm,60) over(partition by gicode order by trd_date))/lag(asset,60) over(partition by gicode order by trd_date) as D5GPOA,
                     (ni-lag(ni,60) over(partition by gicode order by trd_date))/lag(equity,60) over(partition by gicode order by trd_date) as D5ROE,
                     (ni-lag(ni,60) over(partition by gicode order by trd_date))/lag(asset,60) over(partition by gicode order by trd_date) as D5ROA,
                     (cfo_ttm-lag(cfo_ttm,60) over(partition by gicode order by trd_date))/lag(asset,60) over(partition by gicode order by trd_date) as D5CFOA,
                     (gross_profit_ttm-lag(gross_profit_ttm,60) over(partition by gicode order by trd_date))/lag(sales_ttm,60) over(partition by gicode order by trd_date) as D5GMAR,
                     (ni -lag(ni,60) over(partition by gicode order by trd_date)- cfo_ttm+ lag(cfo_ttm,60) over(partition by gicode order by trd_date))/lag(asset,60) over(partition by gicode order by trd_date) as D5ACC,
                     adj_prc/lag(adj_prc,12) over(partition by gicode order by trd_date) rtn_12m
                     from kosdaq_20171130""",con=connection)
kospi_temp = pd.read_sql("""select trd_date, gicode, co_nm, pretax_ni + lag(pretax_ni,3) over(partition by gicode order by trd_date)+ lag(pretax_ni,6) over(partition by gicode order by trd_date)  + lag(pretax_ni,9) over(partition by gicode order by trd_date) pretax_ni_ttm from kospi_20171130_temp""",con=connection)
kosdaq_temp = pd.read_sql("""select trd_date, gicode, co_nm, pretax_ni + lag(pretax_ni,3) over(partition by gicode order by trd_date)+ lag(pretax_ni,6) over(partition by gicode order by trd_date)  + lag(pretax_ni,9) over(partition by gicode order by trd_date) pretax_ni_ttm from kosdaq_20171130_temp""",con=connection)
kospi = pd.merge(kospi,kospi_temp,on=['TRD_DATE','GICODE'])
kosdaq = pd.merge(kosdaq,kosdaq_temp,on=['TRD_DATE','GICODE'])

rebalancing_date = pd.read_sql("""select * from rebalancing_date_20171130""",con=connection)
month_date = pd.read_sql("""select * from month_date_20171130""",con=connection)
wics_mid = pd.read_sql("""select * from wics_mid_20171130""",con=connection)


#kospi_daily_return = pd.read_sql("""select * from kospi_daily_stock """,con=connection)
#kosdaq_daily_return = pd.read_sql("""select * from kosdaq_daily_stock """,con=connection)
daily_return = pd.concat([pd.read_sql("""select * from kospi_daily_stock_20171130 """,con=connection),pd.read_sql("""select * from kosdaq_daily_stock_20171130 """,con=connection)],axis=0,ignore_index=True).drop_duplicates()
daily_return = daily_return[daily_return['ADJ_PRC_D'].notnull()] # 메모리 사용량을 줄이기 위해서 실행
#daily_date=pd.DataFrame(daily_return.groupby('TRD_DATE').count().reset_index()['TRD_DATE'])
#wealth = pd.DataFrame(np.zeros(shape = (daily_date.shape[0], daily_date.shape[1])),index = daily_date['TRD_DATE'], columns = ['RTN_D_CUM'])
#turnover_day = pd.DataFrame(np.zeros(shape = (daily_date.shape[0], daily_date.shape[1])),index = daily_date['TRD_DATE'])
raw_data = pd.concat([kospi,kosdaq],axis=0,ignore_index=True).drop_duplicates()   #왜인지 모르겠는데 db에 중복된 정보가 들어가있네 ..? 
col_length = len(rebalancing_date)-1 #rebalancing_date의 길이는 66이다. range로 이렇게 하면 0부터 65까지 66개의 i 가 만들어진다. -1을 해준건 실제 수익률은 -1개가 생성되기 때문.

return_data = pd.DataFrame(np.zeros((1,col_length)))
data_name = pd.DataFrame(np.zeros((200,col_length)))
return_month_data = pd.DataFrame(np.zeros((1,3*col_length)))
quarter_data = pd.DataFrame(np.zeros((200,3*col_length)))
return_final = pd.DataFrame(np.zeros((1,1)))
return_month_data = pd.DataFrame(np.zeros((1,3*col_length)))

#raw_data = raw_data[raw_data['WICS_BIG']!='금융']
#raw_data = raw_data[raw_data['JIJU']!='지주']
#raw_data = raw_data[(raw_data['EQUITY'].notnull())&(raw_data['EQUITY']>0)] #equity가 null인건 망한기업 혹은 기업이 아님
#raw_data['size_FIF_wisefn'] = raw_data['JISU_STOCK']*raw_data['FIF_RATIO']*raw_data['ADJ_PRC'] # 예전에는 코드에서 만들었으나 이제는 한번에 미리 만들자

#raw_data['CO_NM_y'] = raw_data['CO_NM'] # temp 데이타가 추가되게 되면 이게 필요한데 지금은 없어서 그냥 강제로 만들었다.


first_column = len(raw_data.columns)  # 1/pbr 의 loc
#raw_data['gp/a'] = raw_data['GROSS_PROFIT'] / raw_data['ASSET']    # gross profit을 ttm으로..
#raw_data['EBIT_YOY'] = raw_data['OPER_PROFIT_YOY']
# value
raw_data['TLTA'] = raw_data['LIAB']/raw_data['ADJASSET']
raw_data['WCTA'] = (raw_data['LIQ_EQUITY']-raw_data['LIQ_DEBT'])/raw_data['ADJASSET']
raw_data['CLCA'] = raw_data['LIQ_DEBT']/raw_data['LIQ_EQUITY']
raw_data['OENEG'] = (raw_data['LIAB']>raw_data['ASSET'])*1
raw_data['NITA'] = raw_data['NI']/raw_data['ASSET']
raw_data['FUTL'] = raw_data['PRETAX_NI_TTM']/raw_data['LIAB']
raw_data['1/per']= raw_data['ADJ_NI_12M_FWD']/raw_data['MARKET_CAP']
raw_data['1/pbr'] = raw_data['EQUITY']/raw_data['MARKET_CAP']
raw_data['GPOA'] = raw_data['GROSS_PROFIT_TTM']/raw_data['ASSET']
raw_data['ROE'] = raw_data['NI']/raw_data['EQUITY']
raw_data['ROA'] = raw_data['NI']/raw_data['ASSET']
raw_data['CFOA'] = raw_data['CFO_TTM']/raw_data['ASSET']
raw_data['GMAR'] = raw_data['GROSS_PROFIT_TTM']/raw_data['SALES_TTM']
raw_data['ACC'] = (raw_data['NI']-raw_data['CFO_TTM'])/raw_data['ASSET']
raw_data['div_yield']=raw_data['CASH_DIV_COM']/raw_data['MARKET_CAP']

#raw_data['INTWO'] = np.max(raw_data['NI'],raw_data['NI_1Y']) 마지막에 해야겠는걸
raw_data = raw_data.rename(columns={'CO_NM_x':'CO_NM'}) # column 이름 변경

final_column = len(raw_data.columns)-1 # roa 의 loc



ir_data = pd.DataFrame(np.zeros((final_column-first_column+1,30)))
factor_num = 1
row_num = 0

factors=raw_data.head().T.reset_index().loc[first_column:,'index'].reset_index(drop=True)
#raw_data = raw_data.loc[:,['TRD_DATE','CO_NM_y','size_FIF_wisefn','ISKOSDAQ','WICS_MID','GICODE','ADJ_PRC','CAP_SIZE','MARKET_CAP','CO_NM']+list(factors)]


profit_col_loc = ['GPOA','ROE','ROA','CFOA','GMAR','ACC']
value_col_loc = ['1/per','1/pbr','div_yield']


#a=QVGSM(50,raw_data,rebalancing_date,month_date,wics_mid,daily_return,gross_col_loc,profit_col_loc,value_col_loc,cpi_data)
#b =a.QVGSM()



gross_col_loc = ['D5GPOA','D5ROE','D5ROA','D5CFOA','D5GMAR','D5ACC']
col1 = []

for i in range(1, len(gross_col_loc)+1):
    els = [list(x) for x in itertools.combinations(gross_col_loc, i)]
    col1.extend(els)

profit_col_loc = ['GPOA','ROE','ROA','CFOA','GMAR','ACC']
col2 = []

for i in range(1, len(profit_col_loc)+1):
    els = [list(x) for x in itertools.combinations(profit_col_loc, i)]
    col2.extend(els)

value_col_loc = ['1/per','1/pbr','div_yield']
col3 = []

for i in range(1, len(value_col_loc)+1):
    els = [list(x) for x in itertools.combinations(value_col_loc, i)]
    col3.extend(els)


for o in range(2):  
    for m in range(2): 
        for i in range(len(col1)):
            for j in range(len(col3)):
                a=QVGSM(50,raw_data,rebalancing_date,month_date,wics_mid,daily_return,col1[i],col2[i],col3[j],cpi_data,o,m)
                locals()['aaa_{}{}{}{}{}'.format(i,i,j,o,m)] =a.QVGSM()
                b=result_calculator(locals()['aaa_{}{}{}{}{}'.format(i,i,j,o,m)][0],kospi_day)
                b.rolling_12month_return_5factor(i,i,j,o,m)
                        
    
m=0
o=1
j=1
i=9
for o in range(2):  
    for m in range(2): 
        for i in range(len(col1)):
            for j in range(len(col3)):
                a=QVGSM_sector(50,raw_data,rebalancing_date,month_date,wics_mid,daily_return,col1[i],col2[i],col3[j],cpi_data,o,m)
                locals()['aaa_{}{}{}{}{}'.format(i,i,j,o,m)] =a.QVGSM_sector()
                b=result_calculator(locals()['aaa_{}{}{}{}{}'.format(i,i,j,o,m)][0],kospi_day)
                b.rolling_12month_return_5factor(i,i,j,o,m)

