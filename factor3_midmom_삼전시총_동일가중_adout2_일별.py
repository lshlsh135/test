
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
class factor_3_mid_adoutlier:
 
    def __init__(self,stock_num,raw_data,rebalancing_date,month_date,wics_mid,daily_return,col_num,col_num2,col_num3):
        self.stock_num = stock_num
        self.raw_data = raw_data
        self.rebalancing_date = rebalancing_date
        self.month_date = month_date
        self.daily_return = daily_return
        self.col_num = col_num
        self.col_num2 = col_num2
        self.col_num3 = col_num3
        self.col_loc = [self.col_num,self.col_num2,self.col_num3]
        self.z_col_loc = ['z_'+self.col_num,'z_'+self.col_num2,'z_'+self.col_num3]
        self.wics_mid = wics_mid
        self.end_wealth = 1 # 포트폴리오의 시작 wealth = 1
        self.turno = 0 # 가장 처음 리밸런싱을 잡기 위한 변수
        self.wealth = list() # 매 리밸런싱때의 wealth 변화를 list로 저장
        self.wealth_num=0 # 리밸런싱 할때마다 wealth의 리스트 row가 증가하기 때문에 같이 늘려주는 변수
        self.daily_date=pd.DataFrame(self.daily_return.groupby('TRD_DATE').count().reset_index()['TRD_DATE'])
        self.turnover_day = pd.DataFrame(np.zeros(shape = (self.daily_date.shape[0], self.daily_date.shape[1])),index = self.daily_date['TRD_DATE'])
    def factor_3_mid_adoutlier(self):
        col_length = len(self.rebalancing_date)-1 #rebalancing_date의 길이는 66이다. range로 이렇게 하면 0부터 65까지 66개의 i 가 만들어진다. -1을 해준건 실제 수익률은 -1개가 생성되기 때문.
        
        return_data = pd.DataFrame(np.zeros((1,col_length)))
#        return_data = return_data.iloc[:,4:] # column index는 2001년2월부터 있지만 실제 백테스트 결과는 2002년 2월부터임
        return_final = pd.DataFrame(np.zeros((1,1)))
        return_month_data = pd.DataFrame(np.zeros((1,3*col_length)))
#        return_month_data = return_month_data.iloc[:,12:] # column index는 2001년2월부터 있지만 실제 백테스트 결과는 2002년 2월부터임
        turnover = pd.DataFrame(np.zeros((1,1)))
        turnover_quarter = pd.DataFrame(np.zeros((1,col_length)))
        data_name = pd.DataFrame(np.zeros((200,col_length)))
        quarter_data = pd.DataFrame(np.zeros((200,3*col_length)))
        
        for n in range(4,col_length): 
            first_mom = self.wics_mid[self.wics_mid['TRD_DATE']==self.rebalancing_date.iloc[n,0]] #12-1 개월 모멘텀을 구하기 위해서 리밸런싱날짜에 맞게 모멘텀 데이터 받음
            cur_mom_row=self.month_date.loc[self.month_date['MONTH_DATE']==self.rebalancing_date.iloc[n,0]].index[0]
            
            #cur_month=month_date.loc[month_date['MONTH_DATE']==rebalancing_date.iloc[n+1,0]].index[0]
            
            mom_return_data_1 = self.wics_mid[self.wics_mid['TRD_DATE']==self.month_date.iloc[cur_mom_row-1,0]] #t-2 data
            mom_return_data_2 = self.wics_mid[self.wics_mid['TRD_DATE']==self.month_date.iloc[cur_mom_row-12,0]] #t-12 data
            mom_return_data_1 = pd.merge(mom_return_data_1,mom_return_data_2,on='GICODE') # 따로따로 계산하려고 했더니 index가 안맞아서 gicode로 merge 했다.
            mom_return_data_1['11M_GROSS_RETURN'] = mom_return_data_1['END_PRICE_x'] / mom_return_data_1['END_PRICE_y'] # 머지하면 index가 필요 없어져서 수익률 계산이 쉬워짐
            
            mom_return_data_1=mom_return_data_1.assign(rnk=np.floor(mom_return_data_1['11M_GROSS_RETURN'].rank(method='first',ascending=False))) # 누적수익률이 높은 섹터별로 ranking
            sector_mom = mom_return_data_1.query('rnk<16') #상위 15 섹터 선택 완료
    
            first_data = self.raw_data[self.raw_data['TRD_DATE']==self.rebalancing_date.iloc[n,0]] # rebalanging할 날짜에 들어있는 모든 db data를 받아온다.
            target_data = self.raw_data[self.raw_data['TRD_DATE']==self.rebalancing_date.iloc[n+1,0]]
            target_data = target_data.loc[:,['TRD_DATE','GICODE','ADJ_PRC']]
            first_data = first_data[(first_data['CAP_SIZE']==1)|(first_data['CAP_SIZE']==2)|(first_data['CAP_SIZE']==3)|(first_data['ISKOSDAQ']=='KOSDAQ')]
            first_data = first_data[first_data['MARKET_CAP']>100000000000]
#            first_data = first_data[first_data['EQUITY'].notnull()] ################################################
#            first_data['size_FIF_wisefn'] = first_data['JISU_STOCK']*first_data['FIF_RATIO']*first_data['ADJ_PRC'] # f_score을 body에서 column index로 주기 위해서는 순서가 중요하다. 따라서 매번 선언해주지 않고 raw_data선에서 한번에 선언해주어서 column index 순서를 앞쪽으로 .. => 팩터들끼리 모아둘 수 있게
            samsung = first_data[first_data['CO_NM']=='삼성전자']
            
            sector_mom = sector_mom.rename(columns={'CO_NM_x':'WICS_MID'}) # column 이름 변경
            sector_mom.drop('TRD_DATE_y', axis=1, inplace=True)
            sector_mom.drop('TRD_DATE_x', axis=1, inplace=True)
            sector_mom.drop('CO_NM_y', axis=1, inplace=True)
            sector_mom.drop('GICODE', axis=1, inplace=True)
            
            first_data=pd.merge(sector_mom,first_data,on='WICS_MID') # 모멘텀 상위 15개 섹터에 존재하는 주식들 모임 <<<첫번째 팩터가 47번째..>
                      
            data_length = len(first_data) # 몇개의 종목이 rebalanging_date때 존재했는지 본다.
            
            first_data.loc[:,'size_FIF_wisefn']=first_data.loc[:,'size_FIF_wisefn']/1000  
            first_data = first_data.replace([np.inf, -np.inf],np.nan)  
            
            
            
            #팩터들 중에서 nan 값 제거 
            for i in self.col_loc:
                first_data = first_data[first_data.loc[:,i].notnull()]
            
            # 팩터들 중에서 아웃라이어 제거
            for i in self.col_loc:  #섹터에 남는주식수가 너무 적어짐.. 5% 너무 많나??
                first_data = first_data[(first_data.loc[:,i]>np.percentile(first_data.loc[:,i],1))&(first_data.loc[:,i]<np.percentile(first_data.loc[:,i],99))]
#                
            
            #이제 섹터별로 z_score의 평균 빼줘서 표준화 
            
            for i in range(len(sector_mom)):
                locals()['data_{}'.format(i)] = first_data[first_data['WICS_MID']==sector_mom.iloc[i,0]]
                for j in self.col_loc:
                    locals()['data_{}_{}'.format(i,j)] = locals()['data_{}'.format(i)][locals()['data_{}'.format(i)].loc[:,j].notnull()]
                    locals()['data_{}_{}_cap'.format(i,j)] = np.sum(locals()['data_{}_{}'.format(i,j)]['size_FIF_wisefn'])
                    locals()['data_{}_{}'.format(i,j)] = locals()['data_{}_{}'.format(i,j)].assign(market_weight=locals()['data_{}_{}'.format(i,j)]['size_FIF_wisefn']/locals()['data_{}_{}_cap'.format(i,j)])
                    locals()['data_{}_{}_mu'.format(i,j)] = np.sum(locals()['data_{}_{}'.format(i,j)].loc[:,j]*locals()['data_{}_{}'.format(i,j)]['market_weight'])
                    locals()['data_{}_{}_std'.format(i,j)] = np.sqrt(np.sum(np.square(locals()['data_{}_{}'.format(i,j)].loc[:,j]-locals()['data_{}_{}_mu'.format(i,j)])*locals()['data_{}_{}'.format(i,j)]['market_weight']))
                    locals()['data_{}'.format(i)]['z_'+j] = (locals()['data_{}_{}'.format(i,j)].loc[:,j]-locals()['data_{}_{}_mu'.format(i,j)])/locals()['data_{}_{}_std'.format(i,j)]
                    
                    
                    
#                     locals()['data_{}'.format(i)][j] = locals()['data_{}'.format(i)][j] - np.mean(locals()['data_{}'.format(i)][j])
            
            for y in range(1,len(sector_mom)):    
                 locals()['data_{}'.format(0)] = pd.concat([locals()['data_{}'.format(0)],locals()['data_{}'.format(y)]],axis=0,join='inner')

#            for i in self.z_col_loc:                  
#                locals()['data_{}'.format(0)].loc[locals()['data_{}'.format(0)][i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
#                locals()['data_{}'.format(0)].loc[locals()['data_{}'.format(0)][i]<-3,i] = -3
#                
            locals()['data_{}'.format(0)] = locals()['data_{}'.format(0)].assign(z_score=np.nanmean(locals()['data_{}'.format(0)].loc[:,self.z_col_loc],axis=1))
            
            
            result = locals()['data_{}'.format(0)]
            result=result.assign(rnk=result['z_score'].rank(method='first',ascending=False)) 
            
            for i in self.col_loc:
                samsung[i]=0
                samsung['z_score'] = 0
                samsung['rnk'] = 0                                       
            

            
            samsung.drop('CO_NM_y', axis=1, inplace=True)
            
            #삼성전자가 두번 포함되는 경우 한번 제거하고 나면 rnk가 비기 때문에 if 문으로 25종목을 고르도록 해준다.
            result_sam = pd.concat([result,samsung],axis=0)
            result_sam = result_sam.drop_duplicates(subset='GICODE', keep='last') # subset을 CO_NM으로 하면 왠지 모르게 쓸데없는게 지워짐 한글 못읽나봄
            result_sam = result_sam[result_sam['rnk']<self.stock_num]
            if len(result_sam) != self.stock_num:
                result_sam = pd.concat([result,samsung],axis=0)
                result_sam = result_sam.drop_duplicates(subset='GICODE', keep='last')
                result_sam = result_sam[result_sam['rnk']<self.stock_num+1]
            
            result = result_sam 
            data_name[n]=result['CO_NM'].reset_index(drop=True)     
#            if ki == 0:
#                a = result
#                ki+=1
#            else:
#                a=pd.concat([a,result],axis=0)
#                ki+=1
                
            result = result.loc[:,['TRD_DATE','GICODE']].reset_index(drop=True)
            
            first_data = self.raw_data[self.raw_data['TRD_DATE']==self.rebalancing_date.iloc[n,0]]
            samsung_weight = first_data[(first_data['CAP_SIZE']==1)|(first_data['CAP_SIZE']==2)|(first_data['CAP_SIZE']==3)]
            samsung_weight = pd.merge(target_data,samsung_weight,on='GICODE') # 3개월치 수익률을 구하기 위해 3개월 후 존재하는 data에 현재 data를 붙임
            samsung_weight['3M_RETURN'] = samsung_weight['ADJ_PRC_x']/samsung_weight['ADJ_PRC_y'] # 3개월동안의 종목 수익률
            samsung_weight=samsung_weight[samsung_weight['3M_RETURN']!=0]
            samsung_weight=samsung_weight[samsung_weight.notnull()]
            
            samsung_weight = samsung_weight[samsung_weight['CO_NM']=='삼성전자']['MARKET_CAP'].reset_index(drop=True) / np.sum(samsung_weight['MARKET_CAP']) # 삼성전자 시가총액 비중
            rest_weight = 1 - samsung_weight # 나머지 종목들의 시총비중
            
          
#            result.loc[result['GICODE']=='A005930','wts'] = samsung_weight[0]
#            result.loc[result['GICODE']!='A005930','wts'] = rest_weight[0] / 24
#            
#            first_daily_d = daily_date.loc[daily_date['TRD_DATE']==rebalancing_date.iloc[n,0]].index[0] #일별데이터에서 첫번째 리밸런싱 날짜가 몇번째 row에 있는가
#            last_daily_d = daily_date.loc[daily_date['TRD_DATE']==rebalancing_date.iloc[n+1,0]].index[0]
#            
           
            
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
        return [net_wealth, net_daily_gross_rtn, data_name]  # 이렇게 return 하면 list로 받아짐
                
        