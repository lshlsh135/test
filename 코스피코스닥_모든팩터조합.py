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

from factor3_midmom_삼전시총_동일가중_adout2_일별 import factor_3_mid_adoutlier

from result_calculator import result_calculator


#이거 두개 반드시 선언!
cx0=cx_Oracle.makedsn("localhost",1521,"xe")
connection = cx_Oracle.connect("lshlsh135","2tkdgns2",cx0) #이게 실행이 안될때가 있는데
#그때는 services에 들어가서 oracle listner를 실행시켜줘야함

kospi_day = pd.read_sql("""select * from kospi_day_prc""",con=connection) # 코스피 일별 종가
kospi_day.set_index('TRD_DATE',inplace=True)
kospi_quarter = pd.read_sql("""select * from kospi_quarter_return""",con=connection)
kospi_month = pd.read_sql("""select * from kospi_month_return""",con=connection)
#DATA를 가져온다!!
kospi = pd.read_sql("""select * from kospi""",con=connection)
kosdaq = pd.read_sql("""select * from kosdaq""",con=connection)
kospi_temp = pd.read_sql("""select * from kospi_temp""",con=connection)
kosdaq_temp = pd.read_sql("""select * from kosdaq_temp""",con=connection)
kospi = pd.merge(kospi,kospi_temp,on=['TRD_DATE','GICODE'])
kosdaq = pd.merge(kosdaq,kosdaq_temp,on=['TRD_DATE','GICODE'])

rebalancing_date = pd.read_sql("""select * from rebalancing_date""",con=connection)
month_date = pd.read_sql("""select * from month_date""",con=connection)
wics_mid = pd.read_sql("""select * from wics_mid""",con=connection)


#kospi_daily_return = pd.read_sql("""select * from kospi_daily_stock """,con=connection)
#kosdaq_daily_return = pd.read_sql("""select * from kosdaq_daily_stock """,con=connection)
daily_return = pd.concat([pd.read_sql("""select * from kospi_daily_stock """,con=connection),pd.read_sql("""select * from kosdaq_daily_stock """,con=connection)],axis=0,ignore_index=True).drop_duplicates()

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
raw_data = raw_data[raw_data['JIJU']!='지주']
raw_data = raw_data[raw_data['EQUITY'].notnull()] #equity가 null인건 망한기업 혹은 기업이 아님
raw_data['size_FIF_wisefn'] = raw_data['JISU_STOCK']*raw_data['FIF_RATIO']*raw_data['ADJ_PRC'] # 예전에는 코드에서 만들었으나 이제는 한번에 미리 만들자



first_column = len(raw_data.columns)  # 1/pbr 의 loc
raw_data['EBIT_YOY'] = raw_data['OPER_PROFIT_YOY']
#raw_data['EBIT_YOY_2yav'] =  (raw_data['EBIT_YOY'] + raw_data.groupby('GICODE')['EBIT_YOY'].shift(3))/2
raw_data['1/EV_EBIT_TTM'] = 1/raw_data['EV_EBIT_TTM'] # EV/EBIT은 작을수록 좋은거기 때문에 역수
#raw_data['1/EV_EBIT_TTM_2yav'] =  (raw_data['1/EV_EBIT_TTM'] + raw_data.groupby('GICODE')['1/EV_EBIT_TTM'].shift(3))/2
raw_data['1/EV_EBITDA_TTM'] = 1/raw_data['EV_EBITDA_TTM']
#raw_data['1/EV_EBITDA_TTM_2yav'] =  (raw_data['1/EV_EBITDA_TTM'] + raw_data.groupby('GICODE')['1/EV_EBITDA_TTM'].shift(3))/2
#raw_data['gp/a'] = raw_data['GROSS_PROFIT'] / raw_data['ASSET']    # gross profit을 ttm으로..
raw_data['profit_margin_ratio'] = raw_data['NI'] / raw_data['SALES_TTM']
raw_data['asset_turnover'] = raw_data['SALES_TTM'] / raw_data['ASSET'] 
raw_data['1/pbr']=raw_data['EQUITY']/raw_data['MARKET_CAP']
#raw_data['1/pbr_2yav'] =  (raw_data['1/pbr'] + raw_data.groupby('GICODE')['1/pbr'].shift(3))/2
raw_data['1/per']=raw_data['ADJ_NI_12M_FWD']/raw_data['MARKET_CAP']
#raw_data['1/per_2yav'] =  (raw_data['1/per'] + raw_data.groupby('GICODE')['1/per'].shift(3))/2
raw_data['div_yield']=raw_data['CASH_DIV_COM']/raw_data['MARKET_CAP']
#raw_data['div_yield_2yav'] =  (raw_data['div_yield'] + raw_data.groupby('GICODE')['div_yield'].shift(3))/2
raw_data['roe']=raw_data['NI']/raw_data['EQUITY']
#raw_data['roe_2yav'] =  (raw_data['roe'] + raw_data.groupby('GICODE')['roe'].shift(3))/2
raw_data['roa']=raw_data['NI']/raw_data['ASSET']
#raw_data['roa_2yav'] =  (raw_data['roa'] + raw_data.groupby('GICODE')['roa'].shift(3))/2
raw_data['sales_cap_ttm']=raw_data['SALES_TTM']/raw_data['MARKET_CAP']
#raw_data['sales_cap_ttm_2yav'] =  (raw_data['sales_cap_ttm'] + raw_data.groupby('GICODE')['sales_cap_ttm'].shift(3))/2
raw_data['opro_cap_ttm']=raw_data['OPE_PROFIT_TTM']/raw_data['MARKET_CAP']
#raw_data['opro_cap_ttm_2yav'] =  (raw_data['opro_cap_ttm'] + raw_data.groupby('GICODE')['opro_cap_ttm'].shift(3))/2
raw_data['sales_ttm/a']=raw_data['SALES_TTM']/raw_data['ASSET']
#raw_data['sales_ttm/a_2yav'] =  (raw_data['sales_ttm/a'] + raw_data.groupby('GICODE')['sales_ttm/a'].shift(3))/2
raw_data['opro_ttm/a']=raw_data['OPE_PROFIT_TTM']/raw_data['ASSET']
#raw_data['opro_ttm/a_2yav'] =  (raw_data['opro_ttm/a'] + raw_data.groupby('GICODE')['opro_ttm/a'].shift(3))/2
raw_data['1/trd_value']=raw_data['MARKET_CAP'] /raw_data['TRD_VALUE_60D_MEAN']
raw_data['1/vol'] = 1/raw_data['STD_52WEEK']
raw_data['1/beta'] = 1/raw_data['BEDA_52WEEK_D']


raw_data = raw_data.rename(columns={'CO_NM_x':'CO_NM'}) # column 이름 변경

final_column = len(raw_data.columns)-1 # roa 의 loc

ir_data = pd.DataFrame(np.zeros((final_column-first_column+1,30)))
factor_num = 1
row_num = 0

factors=raw_data.head().T.reset_index().loc[first_column:,'index'].reset_index(drop=True)

#
#i = '1/pbr'
#j = '1/per'
#z = 'div_yield'


for i in factor:
    for j in factors:
        for z in factors:
            if factors[factors==i].index[0]<factors[factors==j].index[0]<factors[factors==z].index[0]:
                a=factor_3_mid_adoutlier(50,raw_data,rebalancing_date,month_date,wics_mid,daily_return,i,j,z)
                locals()['aaa_{}{}{}'.format(i,j,z)] =a.factor_3_mid_adoutlier()
                b=result_calculator(locals()['aaa_{}{}{}'.format(i,j,z)][0],kospi_day)
                b.rolling_12month_return_3factor(i,j,z)
        
    
    
    
    
    