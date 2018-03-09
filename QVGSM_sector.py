# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 08:57:15 2018

@author: SH-NoteBook
"""

"""
Created on Tue Oct 17 13:27:31 2017


29개의 wics 섹터 중에서 1년 - 1개월 누적수익률 상위 15섹터를 고른 후에, 
그 섹터에 포함되는 종목중에서 factor들의 outlier들을 winsorize 해주고
섹터별로 z_score을 구한다음 +-3 보정해준다.

주식가격에서 직접 수익률을 구해서 쓰는것과 일별수익률을 받아서 쓰는것에는 오차가 있다...


@author: SH-NoteBook
"""
import numpy as np
import pandas as pd
from drawdown import drawdown
import copy

class QVGSM_sector:
 
    def __init__(self,stock_num,raw_data,rebalancing_date,month_date,wics_mid,daily_return,gross_col_loc,profit_col_loc,value_col_loc,cpi_data,oscore,momentum):
        self.stock_num = stock_num
        self.raw_data = raw_data
        self.rebalancing_date = rebalancing_date
        self.month_date = month_date
        self.wics_mid = wics_mid
        self.daily_return = daily_return
        self.cpi_data = cpi_data
        self.oscore = oscore
        self.momentum = momentum
        
        self.gross_col_loc = gross_col_loc
#        self.gross_z_col_loc = ['z_'+gross_col_loc  for gross_col_loc in gross_col_loc]
        self.profit_col_loc = profit_col_loc
#        self.profit_z_col_loc = ['z_'+self.profit_col_loc  for self.profit_col_loc in self.profit_col_loc]
        self.value_col_loc = value_col_loc
#        self.value_z_col_loc = ['z_'+self.value_col_loc  for self.value_col_loc in self.value_col_loc]

        
        self.end_wealth = 1 # 포트폴리오의 시작 wealth = 1
        self.turno = 0 # 가장 처음 리밸런싱을 잡기 위한 변수
        self.wealth = list() # 매 리밸런싱때의 wealth 변화를 list로 저장
        self.wealth_num=0 # 리밸런싱 할때마다 wealth의 리스트 row가 증가하기 때문에 같이 늘려주는 변수
        self.daily_date=pd.DataFrame(daily_return.groupby('TRD_DATE').count().reset_index()['TRD_DATE'])
        self.turnover_day = pd.DataFrame(np.zeros(shape = (self.daily_date.shape[0], self.daily_date.shape[1])),index = self.daily_date['TRD_DATE'])
    def QVGSM_sector(self):
        col_length = len(self.rebalancing_date)-1 #rebalancing_date의 길이는 66이다. range로 이렇게 하면 0부터 65까지 66개의 i 가 만들어진다. -1을 해준건 실제 수익률은 -1개가 생성되기 때문.
        
       
#        return_data = return_data.iloc[:,4:] # column index는 2001년2월부터 있지만 실제 백테스트 결과는 2002년 2월부터임
        
        return_month_data = pd.DataFrame(np.zeros((1,3*col_length)))
#        return_month_data = return_month_data.iloc[:,12:] # column index는 2001년2월부터 있지만 실제 백테스트 결과는 2002년 2월부터임
        turnover = pd.DataFrame(np.zeros((1,1)))
        turnover_quarter = pd.DataFrame(np.zeros((1,col_length)))
        data_name = pd.DataFrame(np.zeros((200,col_length)))
        quarter_data = pd.DataFrame(np.zeros((200,3*col_length)))
        sector = self.wics_mid.groupby('CO_NM').count().reset_index()
        for n in range(35,col_length): 
            
    
            first_data_1 = self.raw_data[self.raw_data['TRD_DATE']==self.rebalancing_date.iloc[n,0]] # rebalanging할 날짜에 들어있는 모든 db data를 받아온다.
            target_data = self.raw_data[self.raw_data['TRD_DATE']==self.rebalancing_date.iloc[n+1,0]]
            target_data = target_data.loc[:,['TRD_DATE','GICODE','ADJ_PRC']]
            first_data_1 = first_data_1[(first_data_1['CAP_SIZE']==1)|(first_data_1['CAP_SIZE']==2)|(first_data_1['CAP_SIZE']==3)|(first_data_1['ISKOSDAQ']=='KOSDAQ')]
            first_data_1['INTWO'] = (first_data_1.loc[:,['NI','NI_1Y']].max(axis=1,skipna=False)<0)*1 # 전년도 데이타가 없을때 어떻게 처리를 할것인가 ?
            first_data_1 = first_data_1[first_data_1['MARKET_CAP']>100000000000]
            #            first_data_1 = first_data_1[first_data_1['EQUITY'].notnull()] ################################################
            #            first_data_1['size_FIF_wisefn'] = first_data_1['JISU_STOCK']*first_data_1['FIF_RATIO']*first_data_1['ADJ_PRC'] # f_score을 body에서 column index로 주기 위해서는 순서가 중요하다. 따라서 매번 선언해주지 않고 raw_data선에서 한번에 선언해주어서 column index 순서를 앞쪽으로 .. => 팩터들끼리 모아둘 수 있게
            cpi = self.cpi_data[self.cpi_data['TRD_DATE']==self.rebalancing_date.iloc[n,0]].iloc[0,1]
            first_data_1['O_SCORE'] = -(-1.32 - 0.407*np.log(first_data_1['ADJASSET']/cpi) + 6.03 * first_data_1['TLTA'] \
            -1.43 * first_data_1['WCTA'] + 0.076 * first_data_1['CLCA'] - 1.72 * first_data_1['OENEG'] - 2.37 * first_data_1['NITA'] \
            -1.83 * first_data_1['FUTL'] + 0.285 * first_data_1['INTWO'] - 0.521 * first_data_1['CHIN'])
            
#            first_data = first_data.replace([np.inf, -np.inf],np.nan)  
#            first_data = first_data[first_data['O_SCORE'].notnull()]
            for sec in range(len(sector)):
                first_data = first_data_1[first_data_1.loc[:,'WICS_MID']==sector.iloc[sec,0]]
                try :
                    gross_col_loc2 = copy.deepcopy(self.gross_col_loc)
                    for i in gross_col_loc2:
                        locals()['data_{}'.format(i)] = first_data[first_data.loc[:,i].notnull()]
        #                    locals()['data_{}_{}_cap'.format(i,j)] = np.sum(locals()['data_{}_{}'.format(i,j)]['size_FIF_wisefn'])
        #                    locals()['data_{}_{}'.format(i,j)] = locals()['data_{}_{}'.format(i,j)].assign(market_weight=locals()['data_{}_{}'.format(i,j)]['size_FIF_wisefn']/locals()['data_{}_{}_cap'.format(i,j)])
        #                    locals()['data_{}_{}_mu'.format(i,j)] = np.sum(locals()['data_{}_{}'.format(i,j)].loc[:,j]*locals()['data_{}_{}'.format(i,j)]['market_weight'])
        #                    locals()['data_{}_{}_std'.format(i,j)] = np.sqrt(np.sum(np.square(locals()['data_{}_{}'.format(i,j)].loc[:,j]-locals()['data_{}_{}_mu'.format(i,j)])*locals()['data_{}_{}'.format(i,j)]['market_weight']))
                        locals()['data_{}_rnk'.format(i)] = locals()['data_{}'.format(i)].loc[:,i].rank(method='first',ascending = True) # 클수록 높은등수 -> z값이 큰 양수
                        b = pd.DataFrame(data=(locals()['data_{}_rnk'.format(i)] - locals()['data_{}_rnk'.format(i)].mean()) / locals()['data_{}_rnk'.format(i)].std(ddof=1)) # 자유도 1
                        first_data = pd.merge(first_data,b,left_index=True,right_index=True)
        
                    first_data = first_data.assign(gross_z_score=np.nansum(first_data.loc[:,[gross_col_loc2+'_y'  for gross_col_loc2 in gross_col_loc2]],axis=1))
                    b = pd.DataFrame(data=(first_data.loc[:,'gross_z_score'] - first_data.loc[:,'gross_z_score'].mean()) / first_data.loc[:,'gross_z_score'].std(ddof=1)) # 자유도 1
                    first_data = pd.merge(first_data,b,left_index=True,right_index=True)
         
                   
                    profit_col_loc2 = copy.deepcopy(self.profit_col_loc)
                    for q in profit_col_loc2:
        
                        locals()['data_{}'.format(q)] = first_data[first_data.loc[:,q].notnull()]
        #                    locals()['data_{}_{}_cap'.format(i,j)] = np.sum(locals()['data_{}_{}'.format(i,j)]['size_FIF_wisefn'])
        #                    locals()['data_{}_{}'.format(i,j)] = locals()['data_{}_{}'.format(i,j)].assign(market_weight=locals()['data_{}_{}'.format(i,j)]['size_FIF_wisefn']/locals()['data_{}_{}_cap'.format(i,j)])
        #                    locals()['data_{}_{}_mu'.format(i,j)] = np.sum(locals()['data_{}_{}'.format(i,j)].loc[:,j]*locals()['data_{}_{}'.format(i,j)]['market_weight'])
        #                    locals()['data_{}_{}_std'.format(i,j)] = np.sqrt(np.sum(np.square(locals()['data_{}_{}'.format(i,j)].loc[:,j]-locals()['data_{}_{}_mu'.format(i,j)])*locals()['data_{}_{}'.format(i,j)]['market_weight']))
                        locals()['data_{}_rnk'.format(q)] = locals()['data_{}'.format(q)].loc[:,q].rank(method='first',ascending = True) # 클수록 높은등수 -> z값이 큰 양수
                        b = pd.DataFrame(data=(locals()['data_{}_rnk'.format(q)] - locals()['data_{}_rnk'.format(q)].mean()) / locals()['data_{}_rnk'.format(q)].std(ddof=1)) # 자유도 1
                        first_data = pd.merge(first_data,b,left_index=True,right_index=True)
                    
                    first_data = first_data.assign(profit_z_score=np.nansum(first_data.loc[:,[profit_col_loc2+'_y'  for profit_col_loc2 in profit_col_loc2]],axis=1))
                    b = pd.DataFrame(data=(first_data.loc[:,'profit_z_score'] - first_data.loc[:,'profit_z_score'].mean()) / first_data.loc[:,'profit_z_score'].std(ddof=1)) # 자유도 1
                    first_data = pd.merge(first_data,b,left_index=True,right_index=True)
                    
                    value_col_loc2 = copy.deepcopy(self.value_col_loc)
                    for w in value_col_loc2:
                        locals()['data_{}'.format(w)] = first_data[first_data.loc[:,w].notnull()]
        #                    locals()['data_{}_{}_cap'.format(i,j)] = np.sum(locals()['data_{}_{}'.format(i,j)]['size_FIF_wisefn'])
        #                    locals()['data_{}_{}'.format(i,j)] = locals()['data_{}_{}'.format(i,j)].assign(market_weight=locals()['data_{}_{}'.format(i,j)]['size_FIF_wisefn']/locals()['data_{}_{}_cap'.format(i,j)])
        #                    locals()['data_{}_{}_mu'.format(i,j)] = np.sum(locals()['data_{}_{}'.format(i,j)].loc[:,j]*locals()['data_{}_{}'.format(i,j)]['market_weight'])
        #                    locals()['data_{}_{}_std'.format(i,j)] = np.sqrt(np.sum(np.square(locals()['data_{}_{}'.format(i,j)].loc[:,j]-locals()['data_{}_{}_mu'.format(i,j)])*locals()['data_{}_{}'.format(i,j)]['market_weight']))
                        locals()['data_{}_rnk'.format(w)] = locals()['data_{}'.format(w)].loc[:,w].rank(method='first',ascending = True) # 클수록 높은등수 -> z값이 큰 양수
                        b = pd.DataFrame(data=(locals()['data_{}_rnk'.format(w)] - locals()['data_{}_rnk'.format(w)].mean()) / locals()['data_{}_rnk'.format(w)].std(ddof=1)) # 자유도 1
                        first_data = pd.merge(first_data,b,left_index=True,right_index=True)
                    
                    first_data = first_data.assign(value_z_score=np.nansum(first_data.loc[:,[value_col_loc2+'_y'  for value_col_loc2 in value_col_loc2]],axis=1))
                    b = pd.DataFrame(data=(first_data.loc[:,'value_z_score'] - first_data.loc[:,'value_z_score'].mean()) / first_data.loc[:,'value_z_score'].std(ddof=1)) # 자유도 1
                    first_data = pd.merge(first_data,b,left_index=True,right_index=True)
                   
                    if self.oscore ==1:
                        first_data = first_data[first_data['O_SCORE'].notnull()]
                        data_OSCORE_rnk = first_data['O_SCORE'].rank(method='first',ascending = True)           
                        b = pd.DataFrame(data=(data_OSCORE_rnk - data_OSCORE_rnk.mean()) / data_OSCORE_rnk.std(ddof=1)) # 자유도 1
                        first_data = pd.merge(first_data,b,left_index=True,right_index=True)
                    if self.oscore ==0:
                        first_data['O_SCORE_y'] = 0
                        
                    if self.momentum == 1:
                        first_data = first_data[first_data['RTN_12M'].notnull()]
                        data_RTN_12M_rnk = first_data['RTN_12M'].rank(method='first',ascending = True)           
                        b = pd.DataFrame(data=(data_RTN_12M_rnk - data_RTN_12M_rnk.mean()) / data_RTN_12M_rnk.std(ddof=1)) # 자유도 1
                        first_data = pd.merge(first_data,b,left_index=True,right_index=True)            
                    
                    if self.momentum ==0:
                        first_data['RTN_12M_y'] = 0  
                        
                    first_data = first_data.assign(z_score_sum=first_data['gross_z_score_y']+first_data['profit_z_score_y']+first_data['O_SCORE_y']+first_data['value_z_score_y']+first_data['RTN_12M_y'])
                    locals()['first_data_result_{}'.format(sec)] = first_data
                except:
                    continue            

            for h in range(len(sector)):
                locals()['first_data_result_{}'.format(0)] = pd.concat([locals()['first_data_result_{}'.format(0)],locals()['first_data_result_{}'.format(h)]],axis=0,join='inner')
            
            first_data  = locals()['first_data_result_{}'.format(0)]
            first_data = first_data.assign(rnk=first_data['z_score_sum'].rank(method='first',ascending=False))
            
            
            
            samsung = pd.DataFrame(data = np.zeros((1,first_data.shape[1])),index = first_data[first_data['CO_NM']=='삼성전자'].index, columns = first_data.columns)
            samsung.loc[:,'TRD_DATE'] = self.rebalancing_date.iloc[n,0]
            samsung.loc[:,'GICODE'] = 'A005930'
            samsung.loc[:,'CO_NM'] = '삼성전자'
                
            result_sam = pd.concat([first_data,samsung],axis=0)
            result_sam = result_sam.drop_duplicates(subset='GICODE', keep='last') # subset을 CO_NM으로 하면 왠지 모르게 쓸데없는게 지워짐 한글 못읽나봄
            data_size= len(result_sam)     # Row count
            

            result_sam = result_sam[result_sam['rnk']<self.stock_num]
            if len(result_sam) != self.stock_num:
                result_sam = pd.concat([first_data,samsung],axis=0)
                result_sam = result_sam.drop_duplicates(subset='GICODE', keep='last')
                result_sam = result_sam[result_sam['rnk']<self.stock_num+1]
            
            result = result_sam      
            data_name[n]=result['CO_NM'].reset_index(drop=True)   
            result = result.loc[:,['TRD_DATE','GICODE']].reset_index(drop=True)
            
            first_data = self.raw_data[self.raw_data['TRD_DATE']==self.rebalancing_date.iloc[n,0]]
            samsung_weight = first_data[(first_data['CAP_SIZE']==1)|(first_data['CAP_SIZE']==2)|(first_data['CAP_SIZE']==3)]
            samsung_weight = pd.merge(target_data,samsung_weight,on='GICODE') # 3개월치 수익률을 구하기 위해 3개월 후 존재하는 data에 현재 data를 붙임
            samsung_weight['3M_RETURN'] = samsung_weight['ADJ_PRC_x']/samsung_weight['ADJ_PRC_y'] # 3개월동안의 종목 수익률
            samsung_weight=samsung_weight[samsung_weight['3M_RETURN']!=0]
            samsung_weight=samsung_weight[samsung_weight.notnull()]
            
            samsung_weight = samsung_weight[samsung_weight['CO_NM']=='삼성전자']['MARKET_CAP'].reset_index(drop=True) / np.sum(samsung_weight['MARKET_CAP']) # 삼성전자 시가총액 비중
            rest_weight = 1 - samsung_weight # 나머지 종목들의 시총비중
            
            
            
            rtn_d_need=self.daily_return[(self.daily_return['TRD_DATE']<=self.rebalancing_date.iloc[n+1,0])&(self.daily_return['TRD_DATE']>=self.rebalancing_date.iloc[n,0])] # 리밸런싱날부터 다음 리밸런싱날까지의 일별 데이타
            rst_rtn_d=pd.merge(result,rtn_d_need,how='inner',on='GICODE') # 선택된 주식과 일별데이타 merge
            rst_rtn_d['RTN_D'] = rst_rtn_d.groupby('GICODE')['ADJ_PRC_D'].pct_change() + 1 # gross return으로 바꿔줌
            rst_rtn_d.loc[(rst_rtn_d['TRD_DATE_y']==self.rebalancing_date.iloc[n,0])&(rst_rtn_d['GICODE']=='A005930'),'RTN_D'] = self.end_wealth * samsung_weight[0] # 리밸런싱 당일날의 각 주식의 가치
            rst_rtn_d.loc[(rst_rtn_d['TRD_DATE_y']==self.rebalancing_date.iloc[n,0])&(rst_rtn_d['GICODE']!='A005930'),'RTN_D'] = self.end_wealth * rest_weight[0] / (self.stock_num-1)
            rst_rtn_d['RTN_D_CUM']=rst_rtn_d.groupby('GICODE')['RTN_D'].cumprod() # 각 주식별 누적수익률
           
            self.wealth.append(rst_rtn_d.groupby('TRD_DATE_y').sum()['RTN_D_CUM']) # list로 쭈욱 받고
            
            self.end_wealth = self.wealth[self.wealth_num][-1]
            self.wealth_num+=1
            
            
            
            if self.turno == 0:
                self.turnover_day.loc[self.rebalancing_date.iloc[n,0]] = 1
                self.turno+= 1
            else:
                turnover_data_sum=pd.merge(rst_rtn_d[rst_rtn_d['TRD_DATE_y']==self.rebalancing_date.iloc[n,0]],rst_rtn_d_past[rst_rtn_d_past['TRD_DATE_y']==self.rebalancing_date.iloc[n,0]],how='outer',on='GICODE')
                turnover_data_sum = turnover_data_sum.replace(np.nan,0)  
                self.turnover_day.loc[self.rebalancing_date.iloc[n,0]] = np.sum(abs(turnover_data_sum['RTN_D_CUM_x']/np.sum(turnover_data_sum['RTN_D_CUM_x'])-turnover_data_sum['RTN_D_CUM_y']/np.sum(turnover_data_sum['RTN_D_CUM_y'])))
            
            
#            rst_rtn_d_past = rst_rtn_d[rst_rtn_d['TRD_DATE_y']==rebalancing_date.iloc[n+1,0]]
            rst_rtn_d_past = rst_rtn_d

    
        self.wealth = pd.concat(self.wealth) # 맨 마지막에 리스트를 풀어서 시리즈로 만들어줌
        self.wealth=self.wealth[~self.wealth.index.duplicated(keep='first')] #중복제거 
        daily_gross_rtn=pd.DataFrame(self.wealth.pct_change()+1) # wealth의 누적에서 일별 gross 수익률을 구함.
        daily_gross_rtn[np.isnan(daily_gross_rtn)] = 0             # 첫번째 수익률이 nan이기 떄문에 바꿔준다.
        self.turnover_day = self.turnover_day.shift(1) * 0.005 # turnover 구한거를 리밸런싱 다음날에 반영해준다.
        sub = pd.merge(daily_gross_rtn,self.turnover_day,left_index=True,right_index=True)
        net_daily_gross_rtn=sub.iloc[:,0]-sub.iloc[:,1]
        net_daily_gross_rtn[0] = 1 # 누적 wealth를 구하기 위해 첫날 수익률을 1이라고 가정.
        net_wealth=net_daily_gross_rtn.cumprod()
        
        dd_port = drawdown(pd.DataFrame(net_wealth.pct_change(1)))
        mdd_port = dd_port.min() # Maximum drawdown
        return [net_wealth, net_daily_gross_rtn, data_name, mdd_port]  # 이렇게 return 하면 list로 받아짐
        

        