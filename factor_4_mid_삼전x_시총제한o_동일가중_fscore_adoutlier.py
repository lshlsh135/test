# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 14:43:02 2017

@author: SH-NoteBook
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 13:27:31 2017


f_score가 7이 넘는 종목들을 먼저 뽑아낸 다음, 12개월 (-1) 섹터 모멘텀으로 29개 섹터중에서
15개의 섹터를 고른다음 각 섹터별로 팩터 표준화를 해서 종목을 뽑는다.





@author: SH-NoteBook
"""
import numpy as np
import pandas as pd
class factor_4_mid_adoutlier:
 
    def __init__(self,raw_data,rebalancing_date,month_date,wics_mid,col_num,col_num2,col_num3,col_num4):
        self.raw_data = raw_data
        self.rebalancing_date = rebalancing_date
        self.month_date = month_date
        self.col_num = col_num
        self.col_num2 = col_num2
        self.col_num3 = col_num3
        self.col_num4 = col_num4
        self.col_loc = [col_num,col_num2,col_num3,col_num4] 
        self.wics_mid = wics_mid
       
        

    def factor_4_mid_adoutlier(self):
        col_length = len(self.rebalancing_date)-1 #rebalancing_date의 길이는 66이다. range로 이렇게 하면 0부터 65까지 66개의 i 가 만들어진다. -1을 해준건 실제 수익률은 -1개가 생성되기 때문.
        
        return_data = pd.DataFrame(np.zeros((1,col_length)))
        return_data = return_data.iloc[:,4:] # column index는 2001년2월부터 있지만 실제 백테스트 결과는 2002년 2월부터임
        return_final = pd.DataFrame(np.zeros((1,1)))
        return_month_data = pd.DataFrame(np.zeros((1,3*col_length)))
        return_month_data = return_month_data.iloc[:,12:] # column index는 2001년2월부터 있지만 실제 백테스트 결과는 2002년 2월부터임
        turnover = pd.DataFrame(np.zeros((1,1)))
        turnover_quarter = pd.DataFrame(np.zeros((1,col_length)))
        data_name = pd.DataFrame(np.zeros((200,col_length)))
        quarter_data = pd.DataFrame(np.zeros((200,3*col_length)))
        
        for n in range(4, col_length): 
            first_mom = self.wics_mid[self.wics_mid['TRD_DATE']==self.rebalancing_date.iloc[n,0]] 
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
            
            past_data = self.raw_data[self.raw_data['TRD_DATE']==self.rebalancing_date.iloc[n-4,0]] # 전년도와 비교하기 위해서 받아온다
            past_data = past_data.loc[:,['TRD_DATE','GICODE','roa','LIQ_RATIO','CUR_RATIO','JISU_STOCK','profit_margin_ratio','asset_turnover']] # 필요한 데이터만 뽑아낸다
            
            factor_data = pd.merge(first_data,past_data,on='GICODE')
            
            factor_data['F1'] = factor_data['NI']>0
            factor_data['F2'] = factor_data['CFO_TTM']>0
            factor_data['F3'] = factor_data['roa_x']>factor_data['roa_y']
            factor_data['F4'] = factor_data['CFO_TTM']>factor_data['NI']
            factor_data['F5'] = factor_data['LIQ_RATIO_x']<factor_data['LIQ_RATIO_y']
            factor_data['F6'] = factor_data['CUR_RATIO_x']>factor_data['CUR_RATIO_y']
            factor_data['F7'] = factor_data['JISU_STOCK_x']<=factor_data['JISU_STOCK_y']
            factor_data['F8'] = factor_data['profit_margin_ratio_x']>factor_data['profit_margin_ratio_y']
            factor_data['F9'] = factor_data['asset_turnover_x']>factor_data['asset_turnover_y']
            
            factor_data['f_score'] = np.sum(factor_data.loc[:,['F1','F2','F3','F4','F5','F6','F7','F8','F9']],axis=1)
            factor_data = factor_data.loc[:,['GICODE','f_score']] # first_data에 붙이기 위해 간단히 나타낸다. 간단하게 하지 않으면 trd_date_y이런식으로 column명이 이상해진다.
            
            first_data = pd.merge(first_data,factor_data,on='GICODE') # f_score 합치기
            
            
            
            data_length = len(first_data) # 몇개의 종목이 rebalanging_date때 존재했는지 본다.
           
            a=1
            #에너지 섹터
            if (np.sum(first_data['WICS_MID']=='에너지')>0)&(np.sum(sector_mom['CO_NM_x']=='에너지')==1):
                data_에너지 = first_data[first_data['WICS_MID']=='에너지']
                # 시총비중 구할떄는 free-float
                #        data_에너지['size_FIF_wisefn']=data_에너지['size_FIF_wisefn']/1000    #size 단위 thousand
                data_에너지.loc[:,'size_FIF_wisefn']=data_에너지.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_에너지 = data_에너지.replace([np.inf, -np.inf],np.nan)  
               
                for i in self.col_loc:
                    locals()['data_에너지_{}'.format(i)] = data_에너지[data_에너지.iloc[:,i].notnull()]
                    locals()['data_에너지_cap_{}'.format(i)] = np.sum(locals()['data_에너지_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_에너지_{}'.format(i)] = locals()['data_에너지_{}'.format(i)].assign(market_weight=locals()['data_에너지_{}'.format(i)]['size_FIF_wisefn']/locals()['data_에너지_cap_{}'.format(i)])
                    locals()['data_에너지_mu_{}'.format(i)] = np.sum(locals()['data_에너지_{}'.format(i)].iloc[:,i]*locals()['data_에너지_{}'.format(i)]['market_weight'])
                    locals()['data_에너지_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_에너지_{}'.format(i)].iloc[:,i]-locals()['data_에너지_mu_{}'.format(i)])*locals()['data_에너지_{}'.format(i)]['market_weight']))
                    data_에너지[i] = (locals()['data_에너지_{}'.format(i)].iloc[:,i]-locals()['data_에너지_mu_{}'.format(i)])/locals()['data_에너지_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_에너지.loc[data_에너지[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_에너지.loc[data_에너지[i]<-3,i] = -3
                      
                result_에너지 = data_에너지    
                result_에너지 = result_에너지.assign(z_score=np.nanmean(result_에너지.loc[:,self.col_loc],axis=1))
            #    result_temp = result
            
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_에너지[result_에너지['z_score'].notnull()]
                a=a+1
                
            if (np.sum(first_data['WICS_MID']=='소재')>0)&(np.sum(sector_mom['CO_NM_x']=='소재')==1):
                data_소재 = first_data[first_data['WICS_MID']=='소재']
                # 시총비중 구할떄는 free-float
                #        data_소재['size_FIF_wisefn']=data_소재['size_FIF_wisefn']/1000    #size 단위 thousand
                data_소재.loc[:,'size_FIF_wisefn']=data_소재.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_소재 = data_소재.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_소재_{}'.format(i)] = data_소재[data_소재.iloc[:,i].notnull()]
                    locals()['data_소재_cap_{}'.format(i)] = np.sum(locals()['data_소재_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_소재_{}'.format(i)] = locals()['data_소재_{}'.format(i)].assign(market_weight=locals()['data_소재_{}'.format(i)]['size_FIF_wisefn']/locals()['data_소재_cap_{}'.format(i)])
                    locals()['data_소재_mu_{}'.format(i)] = np.sum(locals()['data_소재_{}'.format(i)].iloc[:,i]*locals()['data_소재_{}'.format(i)]['market_weight'])
                    locals()['data_소재_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_소재_{}'.format(i)].iloc[:,i]-locals()['data_소재_mu_{}'.format(i)])*locals()['data_소재_{}'.format(i)]['market_weight']))
                    data_소재[i] = (locals()['data_소재_{}'.format(i)].iloc[:,i]-locals()['data_소재_mu_{}'.format(i)])/locals()['data_소재_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_소재.loc[data_소재[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_소재.loc[data_소재[i]<-3,i] = -3                
                      
                result_소재 = data_소재    
                result_소재 = result_소재.assign(z_score=np.nanmean(result_소재.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_소재[result_소재['z_score'].notnull()]
                a=a+1
                
            if (np.sum(first_data['WICS_MID']=='자본재')>0)&(np.sum(sector_mom['CO_NM_x']=='자본재')==1):
                data_자본재 = first_data[first_data['WICS_MID']=='자본재']
                # 시총비중 구할떄는 free-float
                #        data_자본재['size_FIF_wisefn']=data_자본재['size_FIF_wisefn']/1000    #size 단위 thousand
                data_자본재.loc[:,'size_FIF_wisefn']=data_자본재.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_자본재 = data_자본재.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_자본재_{}'.format(i)] = data_자본재[data_자본재.iloc[:,i].notnull()]
                    locals()['data_자본재_cap_{}'.format(i)] = np.sum(locals()['data_자본재_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_자본재_{}'.format(i)] = locals()['data_자본재_{}'.format(i)].assign(market_weight=locals()['data_자본재_{}'.format(i)]['size_FIF_wisefn']/locals()['data_자본재_cap_{}'.format(i)])
                    locals()['data_자본재_mu_{}'.format(i)] = np.sum(locals()['data_자본재_{}'.format(i)].iloc[:,i]*locals()['data_자본재_{}'.format(i)]['market_weight'])
                    locals()['data_자본재_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_자본재_{}'.format(i)].iloc[:,i]-locals()['data_자본재_mu_{}'.format(i)])*locals()['data_자본재_{}'.format(i)]['market_weight']))
                    data_자본재[i] = (locals()['data_자본재_{}'.format(i)].iloc[:,i]-locals()['data_자본재_mu_{}'.format(i)])/locals()['data_자본재_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_자본재.loc[data_자본재[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_자본재.loc[data_자본재[i]<-3,i] = -3                
                      
                result_자본재 = data_자본재    
                result_자본재 = result_자본재.assign(z_score=np.nanmean(result_자본재.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_자본재[result_자본재['z_score'].notnull()]
                a=a+1
                
            if (np.sum(first_data['WICS_MID']=='상업서비스와공급품')>0)&(np.sum(sector_mom['CO_NM_x']=='상업서비스와공급품')==1):
                data_상업서비스와공급품 = first_data[first_data['WICS_MID']=='상업서비스와공급품']
                # 시총비중 구할떄는 free-float
                #        data_상업서비스와공급품['size_FIF_wisefn']=data_상업서비스와공급품['size_FIF_wisefn']/1000    #size 단위 thousand
                data_상업서비스와공급품.loc[:,'size_FIF_wisefn']=data_상업서비스와공급품.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_상업서비스와공급품 = data_상업서비스와공급품.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_상업서비스와공급품_{}'.format(i)] = data_상업서비스와공급품[data_상업서비스와공급품.iloc[:,i].notnull()]
                    locals()['data_상업서비스와공급품_cap_{}'.format(i)] = np.sum(locals()['data_상업서비스와공급품_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_상업서비스와공급품_{}'.format(i)] = locals()['data_상업서비스와공급품_{}'.format(i)].assign(market_weight=locals()['data_상업서비스와공급품_{}'.format(i)]['size_FIF_wisefn']/locals()['data_상업서비스와공급품_cap_{}'.format(i)])
                    locals()['data_상업서비스와공급품_mu_{}'.format(i)] = np.sum(locals()['data_상업서비스와공급품_{}'.format(i)].iloc[:,i]*locals()['data_상업서비스와공급품_{}'.format(i)]['market_weight'])
                    locals()['data_상업서비스와공급품_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_상업서비스와공급품_{}'.format(i)].iloc[:,i]-locals()['data_상업서비스와공급품_mu_{}'.format(i)])*locals()['data_상업서비스와공급품_{}'.format(i)]['market_weight']))
                    data_상업서비스와공급품[i] = (locals()['data_상업서비스와공급품_{}'.format(i)].iloc[:,i]-locals()['data_상업서비스와공급품_mu_{}'.format(i)])/locals()['data_상업서비스와공급품_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_상업서비스와공급품.loc[data_상업서비스와공급품[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_상업서비스와공급품.loc[data_상업서비스와공급품[i]<-3,i] = -3                
                      
                result_상업서비스와공급품 = data_상업서비스와공급품    
                result_상업서비스와공급품 = result_상업서비스와공급품.assign(z_score=np.nanmean(result_상업서비스와공급품.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_상업서비스와공급품[result_상업서비스와공급품['z_score'].notnull()]
                a=a+1
            
            if (np.sum(first_data['WICS_MID']=='운송')>0)&(np.sum(sector_mom['CO_NM_x']=='운송')==1):
                data_운송 = first_data[first_data['WICS_MID']=='운송']
                # 시총비중 구할떄는 free-float
                #        data_운송['size_FIF_wisefn']=data_운송['size_FIF_wisefn']/1000    #size 단위 thousand
                data_운송.loc[:,'size_FIF_wisefn']=data_운송.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_운송 = data_운송.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_운송_{}'.format(i)] = data_운송[data_운송.iloc[:,i].notnull()]
                    locals()['data_운송_cap_{}'.format(i)] = np.sum(locals()['data_운송_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_운송_{}'.format(i)] = locals()['data_운송_{}'.format(i)].assign(market_weight=locals()['data_운송_{}'.format(i)]['size_FIF_wisefn']/locals()['data_운송_cap_{}'.format(i)])
                    locals()['data_운송_mu_{}'.format(i)] = np.sum(locals()['data_운송_{}'.format(i)].iloc[:,i]*locals()['data_운송_{}'.format(i)]['market_weight'])
                    locals()['data_운송_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_운송_{}'.format(i)].iloc[:,i]-locals()['data_운송_mu_{}'.format(i)])*locals()['data_운송_{}'.format(i)]['market_weight']))
                    data_운송[i] = (locals()['data_운송_{}'.format(i)].iloc[:,i]-locals()['data_운송_mu_{}'.format(i)])/locals()['data_운송_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_운송.loc[data_운송[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_운송.loc[data_운송[i]<-3,i] = -3                
                      
                result_운송 = data_운송    
                result_운송 = result_운송.assign(z_score=np.nanmean(result_운송.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_운송[result_운송['z_score'].notnull()]
                a=a+1
                            
            if (np.sum(first_data['WICS_MID']=='자동차와부품')>0)&(np.sum(sector_mom['CO_NM_x']=='자동차와부품')==1):
                data_자동차와부품 = first_data[first_data['WICS_MID']=='자동차와부품']
                # 시총비중 구할떄는 free-float
                #        data_자동차와부품['size_FIF_wisefn']=data_자동차와부품['size_FIF_wisefn']/1000    #size 단위 thousand
                data_자동차와부품.loc[:,'size_FIF_wisefn']=data_자동차와부품.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_자동차와부품 = data_자동차와부품.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_자동차와부품_{}'.format(i)] = data_자동차와부품[data_자동차와부품.iloc[:,i].notnull()]
                    locals()['data_자동차와부품_cap_{}'.format(i)] = np.sum(locals()['data_자동차와부품_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_자동차와부품_{}'.format(i)] = locals()['data_자동차와부품_{}'.format(i)].assign(market_weight=locals()['data_자동차와부품_{}'.format(i)]['size_FIF_wisefn']/locals()['data_자동차와부품_cap_{}'.format(i)])
                    locals()['data_자동차와부품_mu_{}'.format(i)] = np.sum(locals()['data_자동차와부품_{}'.format(i)].iloc[:,i]*locals()['data_자동차와부품_{}'.format(i)]['market_weight'])
                    locals()['data_자동차와부품_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_자동차와부품_{}'.format(i)].iloc[:,i]-locals()['data_자동차와부품_mu_{}'.format(i)])*locals()['data_자동차와부품_{}'.format(i)]['market_weight']))
                    data_자동차와부품[i] = (locals()['data_자동차와부품_{}'.format(i)].iloc[:,i]-locals()['data_자동차와부품_mu_{}'.format(i)])/locals()['data_자동차와부품_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_자동차와부품.loc[data_자동차와부품[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_자동차와부품.loc[data_자동차와부품[i]<-3,i] = -3                
                      
                result_자동차와부품 = data_자동차와부품    
                result_자동차와부품 = result_자동차와부품.assign(z_score=np.nanmean(result_자동차와부품.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_자동차와부품[result_자동차와부품['z_score'].notnull()]
                a=a+1
            
            if (np.sum(first_data['WICS_MID']=='내구소비재와의류')>0)&(np.sum(sector_mom['CO_NM_x']=='내구소비재와의류')==1):
                data_내구소비재와의류 = first_data[first_data['WICS_MID']=='내구소비재와의류']
                # 시총비중 구할떄는 free-float
                #        data_내구소비재와의류['size_FIF_wisefn']=data_내구소비재와의류['size_FIF_wisefn']/1000    #size 단위 thousand
                data_내구소비재와의류.loc[:,'size_FIF_wisefn']=data_내구소비재와의류.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_내구소비재와의류 = data_내구소비재와의류.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_내구소비재와의류_{}'.format(i)] = data_내구소비재와의류[data_내구소비재와의류.iloc[:,i].notnull()]
                    locals()['data_내구소비재와의류_cap_{}'.format(i)] = np.sum(locals()['data_내구소비재와의류_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_내구소비재와의류_{}'.format(i)] = locals()['data_내구소비재와의류_{}'.format(i)].assign(market_weight=locals()['data_내구소비재와의류_{}'.format(i)]['size_FIF_wisefn']/locals()['data_내구소비재와의류_cap_{}'.format(i)])
                    locals()['data_내구소비재와의류_mu_{}'.format(i)] = np.sum(locals()['data_내구소비재와의류_{}'.format(i)].iloc[:,i]*locals()['data_내구소비재와의류_{}'.format(i)]['market_weight'])
                    locals()['data_내구소비재와의류_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_내구소비재와의류_{}'.format(i)].iloc[:,i]-locals()['data_내구소비재와의류_mu_{}'.format(i)])*locals()['data_내구소비재와의류_{}'.format(i)]['market_weight']))
                    data_내구소비재와의류[i] = (locals()['data_내구소비재와의류_{}'.format(i)].iloc[:,i]-locals()['data_내구소비재와의류_mu_{}'.format(i)])/locals()['data_내구소비재와의류_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_내구소비재와의류.loc[data_내구소비재와의류[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_내구소비재와의류.loc[data_내구소비재와의류[i]<-3,i] = -3                
                      
                result_내구소비재와의류 = data_내구소비재와의류    
                result_내구소비재와의류 = result_내구소비재와의류.assign(z_score=np.nanmean(result_내구소비재와의류.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_내구소비재와의류[result_내구소비재와의류['z_score'].notnull()]
                a=a+1
                
            if (np.sum(first_data['WICS_MID']=='호텔_레스토랑_레저')>0)&(np.sum(sector_mom['CO_NM_x']=='호텔_레스토랑_레저')==1):
                data_호텔_레스토랑_레저 = first_data[first_data['WICS_MID']=='호텔_레스토랑_레저']
                # 시총비중 구할떄는 free-float
                #        data_호텔_레스토랑_레저['size_FIF_wisefn']=data_호텔_레스토랑_레저['size_FIF_wisefn']/1000    #size 단위 thousand
                data_호텔_레스토랑_레저.loc[:,'size_FIF_wisefn']=data_호텔_레스토랑_레저.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_호텔_레스토랑_레저 = data_호텔_레스토랑_레저.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_호텔_레스토랑_레저_{}'.format(i)] = data_호텔_레스토랑_레저[data_호텔_레스토랑_레저.iloc[:,i].notnull()]
                    locals()['data_호텔_레스토랑_레저_cap_{}'.format(i)] = np.sum(locals()['data_호텔_레스토랑_레저_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_호텔_레스토랑_레저_{}'.format(i)] = locals()['data_호텔_레스토랑_레저_{}'.format(i)].assign(market_weight=locals()['data_호텔_레스토랑_레저_{}'.format(i)]['size_FIF_wisefn']/locals()['data_호텔_레스토랑_레저_cap_{}'.format(i)])
                    locals()['data_호텔_레스토랑_레저_mu_{}'.format(i)] = np.sum(locals()['data_호텔_레스토랑_레저_{}'.format(i)].iloc[:,i]*locals()['data_호텔_레스토랑_레저_{}'.format(i)]['market_weight'])
                    locals()['data_호텔_레스토랑_레저_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_호텔_레스토랑_레저_{}'.format(i)].iloc[:,i]-locals()['data_호텔_레스토랑_레저_mu_{}'.format(i)])*locals()['data_호텔_레스토랑_레저_{}'.format(i)]['market_weight']))
                    data_호텔_레스토랑_레저[i] = (locals()['data_호텔_레스토랑_레저_{}'.format(i)].iloc[:,i]-locals()['data_호텔_레스토랑_레저_mu_{}'.format(i)])/locals()['data_호텔_레스토랑_레저_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_호텔_레스토랑_레저.loc[data_호텔_레스토랑_레저[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_호텔_레스토랑_레저.loc[data_호텔_레스토랑_레저[i]<-3,i] = -3                
                      
                result_호텔_레스토랑_레저 = data_호텔_레스토랑_레저    
                result_호텔_레스토랑_레저 = result_호텔_레스토랑_레저.assign(z_score=np.nanmean(result_호텔_레스토랑_레저.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_호텔_레스토랑_레저[result_호텔_레스토랑_레저['z_score'].notnull()]
                a=a+1
                
            if (np.sum(first_data['WICS_MID']=='미디어')>0)&(np.sum(sector_mom['CO_NM_x']=='미디어')==1):
                data_미디어 = first_data[first_data['WICS_MID']=='미디어']
                # 시총비중 구할떄는 free-float
                #        data_미디어['size_FIF_wisefn']=data_미디어['size_FIF_wisefn']/1000    #size 단위 thousand
                data_미디어.loc[:,'size_FIF_wisefn']=data_미디어.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_미디어 = data_미디어.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_미디어_{}'.format(i)] = data_미디어[data_미디어.iloc[:,i].notnull()]
                    locals()['data_미디어_cap_{}'.format(i)] = np.sum(locals()['data_미디어_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_미디어_{}'.format(i)] = locals()['data_미디어_{}'.format(i)].assign(market_weight=locals()['data_미디어_{}'.format(i)]['size_FIF_wisefn']/locals()['data_미디어_cap_{}'.format(i)])
                    locals()['data_미디어_mu_{}'.format(i)] = np.sum(locals()['data_미디어_{}'.format(i)].iloc[:,i]*locals()['data_미디어_{}'.format(i)]['market_weight'])
                    locals()['data_미디어_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_미디어_{}'.format(i)].iloc[:,i]-locals()['data_미디어_mu_{}'.format(i)])*locals()['data_미디어_{}'.format(i)]['market_weight']))
                    data_미디어[i] = (locals()['data_미디어_{}'.format(i)].iloc[:,i]-locals()['data_미디어_mu_{}'.format(i)])/locals()['data_미디어_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_미디어.loc[data_미디어[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_미디어.loc[data_미디어[i]<-3,i] = -3                
                      
                result_미디어 = data_미디어    
                result_미디어 = result_미디어.assign(z_score=np.nanmean(result_미디어.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_미디어[result_미디어['z_score'].notnull()]
                a=a+1
                
            if (np.sum(first_data['WICS_MID']=='소매_유통')>0)&(np.sum(sector_mom['CO_NM_x']=='소매_유통')==1):
                data_소매_유통 = first_data[first_data['WICS_MID']=='소매_유통']
                # 시총비중 구할떄는 free-float
                #        data_소매_유통['size_FIF_wisefn']=data_소매_유통['size_FIF_wisefn']/1000    #size 단위 thousand
                data_소매_유통.loc[:,'size_FIF_wisefn']=data_소매_유통.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_소매_유통 = data_소매_유통.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_소매_유통_{}'.format(i)] = data_소매_유통[data_소매_유통.iloc[:,i].notnull()]
                    locals()['data_소매_유통_cap_{}'.format(i)] = np.sum(locals()['data_소매_유통_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_소매_유통_{}'.format(i)] = locals()['data_소매_유통_{}'.format(i)].assign(market_weight=locals()['data_소매_유통_{}'.format(i)]['size_FIF_wisefn']/locals()['data_소매_유통_cap_{}'.format(i)])
                    locals()['data_소매_유통_mu_{}'.format(i)] = np.sum(locals()['data_소매_유통_{}'.format(i)].iloc[:,i]*locals()['data_소매_유통_{}'.format(i)]['market_weight'])
                    locals()['data_소매_유통_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_소매_유통_{}'.format(i)].iloc[:,i]-locals()['data_소매_유통_mu_{}'.format(i)])*locals()['data_소매_유통_{}'.format(i)]['market_weight']))
                    data_소매_유통[i] = (locals()['data_소매_유통_{}'.format(i)].iloc[:,i]-locals()['data_소매_유통_mu_{}'.format(i)])/locals()['data_소매_유통_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_소매_유통.loc[data_소매_유통[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_소매_유통.loc[data_소매_유통[i]<-3,i] = -3                
                      
                result_소매_유통 = data_소매_유통    
                result_소매_유통 = result_소매_유통.assign(z_score=np.nanmean(result_소매_유통.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_소매_유통[result_소매_유통['z_score'].notnull()]
                a=a+1
                
            if (np.sum(first_data['WICS_MID']=='교육서비스')>0)&(np.sum(sector_mom['CO_NM_x']=='교육서비스')==1):
                data_교육서비스 = first_data[first_data['WICS_MID']=='교육서비스']
                # 시총비중 구할떄는 free-float
                #        data_교육서비스['size_FIF_wisefn']=data_교육서비스['size_FIF_wisefn']/1000    #size 단위 thousand
                data_교육서비스.loc[:,'size_FIF_wisefn']=data_교육서비스.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_교육서비스 = data_교육서비스.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_교육서비스_{}'.format(i)] = data_교육서비스[data_교육서비스.iloc[:,i].notnull()]
                    locals()['data_교육서비스_cap_{}'.format(i)] = np.sum(locals()['data_교육서비스_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_교육서비스_{}'.format(i)] = locals()['data_교육서비스_{}'.format(i)].assign(market_weight=locals()['data_교육서비스_{}'.format(i)]['size_FIF_wisefn']/locals()['data_교육서비스_cap_{}'.format(i)])
                    locals()['data_교육서비스_mu_{}'.format(i)] = np.sum(locals()['data_교육서비스_{}'.format(i)].iloc[:,i]*locals()['data_교육서비스_{}'.format(i)]['market_weight'])
                    locals()['data_교육서비스_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_교육서비스_{}'.format(i)].iloc[:,i]-locals()['data_교육서비스_mu_{}'.format(i)])*locals()['data_교육서비스_{}'.format(i)]['market_weight']))
                    data_교육서비스[i] = (locals()['data_교육서비스_{}'.format(i)].iloc[:,i]-locals()['data_교육서비스_mu_{}'.format(i)])/locals()['data_교육서비스_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_교육서비스.loc[data_교육서비스[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_교육서비스.loc[data_교육서비스[i]<-3,i] = -3                
                      
                result_교육서비스 = data_교육서비스    
                result_교육서비스 = result_교육서비스.assign(z_score=np.nanmean(result_교육서비스.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_교육서비스[result_교육서비스['z_score'].notnull()]
                a=a+1
                
            if (np.sum(first_data['WICS_MID']=='식품과기본식료품소매')>0)&(np.sum(sector_mom['CO_NM_x']=='식품과기본식료품소매')==1):
                data_식품과기본식료품소매 = first_data[first_data['WICS_MID']=='식품과기본식료품소매']
                # 시총비중 구할떄는 free-float
                #        data_식품과기본식료품소매['size_FIF_wisefn']=data_식품과기본식료품소매['size_FIF_wisefn']/1000    #size 단위 thousand
                data_식품과기본식료품소매.loc[:,'size_FIF_wisefn']=data_식품과기본식료품소매.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_식품과기본식료품소매 = data_식품과기본식료품소매.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_식품과기본식료품소매_{}'.format(i)] = data_식품과기본식료품소매[data_식품과기본식료품소매.iloc[:,i].notnull()]
                    locals()['data_식품과기본식료품소매_cap_{}'.format(i)] = np.sum(locals()['data_식품과기본식료품소매_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_식품과기본식료품소매_{}'.format(i)] = locals()['data_식품과기본식료품소매_{}'.format(i)].assign(market_weight=locals()['data_식품과기본식료품소매_{}'.format(i)]['size_FIF_wisefn']/locals()['data_식품과기본식료품소매_cap_{}'.format(i)])
                    locals()['data_식품과기본식료품소매_mu_{}'.format(i)] = np.sum(locals()['data_식품과기본식료품소매_{}'.format(i)].iloc[:,i]*locals()['data_식품과기본식료품소매_{}'.format(i)]['market_weight'])
                    locals()['data_식품과기본식료품소매_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_식품과기본식료품소매_{}'.format(i)].iloc[:,i]-locals()['data_식품과기본식료품소매_mu_{}'.format(i)])*locals()['data_식품과기본식료품소매_{}'.format(i)]['market_weight']))
                    data_식품과기본식료품소매[i] = (locals()['data_식품과기본식료품소매_{}'.format(i)].iloc[:,i]-locals()['data_식품과기본식료품소매_mu_{}'.format(i)])/locals()['data_식품과기본식료품소매_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_식품과기본식료품소매.loc[data_식품과기본식료품소매[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_식품과기본식료품소매.loc[data_식품과기본식료품소매[i]<-3,i] = -3                
                      
                result_식품과기본식료품소매 = data_식품과기본식료품소매    
                result_식품과기본식료품소매 = result_식품과기본식료품소매.assign(z_score=np.nanmean(result_식품과기본식료품소매.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_식품과기본식료품소매[result_식품과기본식료품소매['z_score'].notnull()]
                a=a+1
                
            if (np.sum(first_data['WICS_MID']=='식품_음료_담배')>0)&(np.sum(sector_mom['CO_NM_x']=='식품_음료_담배')==1):
                data_식품_음료_담배 = first_data[first_data['WICS_MID']=='식품_음료_담배']
                # 시총비중 구할떄는 free-float
                #        data_식품_음료_담배['size_FIF_wisefn']=data_식품_음료_담배['size_FIF_wisefn']/1000    #size 단위 thousand
                data_식품_음료_담배.loc[:,'size_FIF_wisefn']=data_식품_음료_담배.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_식품_음료_담배 = data_식품_음료_담배.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_식품_음료_담배_{}'.format(i)] = data_식품_음료_담배[data_식품_음료_담배.iloc[:,i].notnull()]
                    locals()['data_식품_음료_담배_cap_{}'.format(i)] = np.sum(locals()['data_식품_음료_담배_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_식품_음료_담배_{}'.format(i)] = locals()['data_식품_음료_담배_{}'.format(i)].assign(market_weight=locals()['data_식품_음료_담배_{}'.format(i)]['size_FIF_wisefn']/locals()['data_식품_음료_담배_cap_{}'.format(i)])
                    locals()['data_식품_음료_담배_mu_{}'.format(i)] = np.sum(locals()['data_식품_음료_담배_{}'.format(i)].iloc[:,i]*locals()['data_식품_음료_담배_{}'.format(i)]['market_weight'])
                    locals()['data_식품_음료_담배_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_식품_음료_담배_{}'.format(i)].iloc[:,i]-locals()['data_식품_음료_담배_mu_{}'.format(i)])*locals()['data_식품_음료_담배_{}'.format(i)]['market_weight']))
                    data_식품_음료_담배[i] = (locals()['data_식품_음료_담배_{}'.format(i)].iloc[:,i]-locals()['data_식품_음료_담배_mu_{}'.format(i)])/locals()['data_식품_음료_담배_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_식품_음료_담배.loc[data_식품_음료_담배[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_식품_음료_담배.loc[data_식품_음료_담배[i]<-3,i] = -3                
                      
                result_식품_음료_담배 = data_식품_음료_담배    
                result_식품_음료_담배 = result_식품_음료_담배.assign(z_score=np.nanmean(result_식품_음료_담배.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_식품_음료_담배[result_식품_음료_담배['z_score'].notnull()]
                a=a+1
                
            if (np.sum(first_data['WICS_MID']=='가정용품과개인용품')>0)&(np.sum(sector_mom['CO_NM_x']=='가정용품과개인용품')==1):
                data_가정용품과개인용품 = first_data[first_data['WICS_MID']=='가정용품과개인용품']
                # 시총비중 구할떄는 free-float
                #        data_가정용품과개인용품['size_FIF_wisefn']=data_가정용품과개인용품['size_FIF_wisefn']/1000    #size 단위 thousand
                data_가정용품과개인용품.loc[:,'size_FIF_wisefn']=data_가정용품과개인용품.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_가정용품과개인용품 = data_가정용품과개인용품.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_가정용품과개인용품_{}'.format(i)] = data_가정용품과개인용품[data_가정용품과개인용품.iloc[:,i].notnull()]
                    locals()['data_가정용품과개인용품_cap_{}'.format(i)] = np.sum(locals()['data_가정용품과개인용품_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_가정용품과개인용품_{}'.format(i)] = locals()['data_가정용품과개인용품_{}'.format(i)].assign(market_weight=locals()['data_가정용품과개인용품_{}'.format(i)]['size_FIF_wisefn']/locals()['data_가정용품과개인용품_cap_{}'.format(i)])
                    locals()['data_가정용품과개인용품_mu_{}'.format(i)] = np.sum(locals()['data_가정용품과개인용품_{}'.format(i)].iloc[:,i]*locals()['data_가정용품과개인용품_{}'.format(i)]['market_weight'])
                    locals()['data_가정용품과개인용품_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_가정용품과개인용품_{}'.format(i)].iloc[:,i]-locals()['data_가정용품과개인용품_mu_{}'.format(i)])*locals()['data_가정용품과개인용품_{}'.format(i)]['market_weight']))
                    data_가정용품과개인용품[i] = (locals()['data_가정용품과개인용품_{}'.format(i)].iloc[:,i]-locals()['data_가정용품과개인용품_mu_{}'.format(i)])/locals()['data_가정용품과개인용품_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_가정용품과개인용품.loc[data_가정용품과개인용품[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_가정용품과개인용품.loc[data_가정용품과개인용품[i]<-3,i] = -3                
                      
                result_가정용품과개인용품 = data_가정용품과개인용품    
                result_가정용품과개인용품 = result_가정용품과개인용품.assign(z_score=np.nanmean(result_가정용품과개인용품.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_가정용품과개인용품[result_가정용품과개인용품['z_score'].notnull()]
                a=a+1
                
            if (np.sum(first_data['WICS_MID']=='건강관리장비와서비스')>0)&(np.sum(sector_mom['CO_NM_x']=='건강관리장비와서비스')==1):
                data_건강관리장비와서비스 = first_data[first_data['WICS_MID']=='건강관리장비와서비스']
                # 시총비중 구할떄는 free-float
                #        data_건강관리장비와서비스['size_FIF_wisefn']=data_건강관리장비와서비스['size_FIF_wisefn']/1000    #size 단위 thousand
                data_건강관리장비와서비스.loc[:,'size_FIF_wisefn']=data_건강관리장비와서비스.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_건강관리장비와서비스 = data_건강관리장비와서비스.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_건강관리장비와서비스_{}'.format(i)] = data_건강관리장비와서비스[data_건강관리장비와서비스.iloc[:,i].notnull()]
                    locals()['data_건강관리장비와서비스_cap_{}'.format(i)] = np.sum(locals()['data_건강관리장비와서비스_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_건강관리장비와서비스_{}'.format(i)] = locals()['data_건강관리장비와서비스_{}'.format(i)].assign(market_weight=locals()['data_건강관리장비와서비스_{}'.format(i)]['size_FIF_wisefn']/locals()['data_건강관리장비와서비스_cap_{}'.format(i)])
                    locals()['data_건강관리장비와서비스_mu_{}'.format(i)] = np.sum(locals()['data_건강관리장비와서비스_{}'.format(i)].iloc[:,i]*locals()['data_건강관리장비와서비스_{}'.format(i)]['market_weight'])
                    locals()['data_건강관리장비와서비스_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_건강관리장비와서비스_{}'.format(i)].iloc[:,i]-locals()['data_건강관리장비와서비스_mu_{}'.format(i)])*locals()['data_건강관리장비와서비스_{}'.format(i)]['market_weight']))
                    data_건강관리장비와서비스[i] = (locals()['data_건강관리장비와서비스_{}'.format(i)].iloc[:,i]-locals()['data_건강관리장비와서비스_mu_{}'.format(i)])/locals()['data_건강관리장비와서비스_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_건강관리장비와서비스.loc[data_건강관리장비와서비스[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_건강관리장비와서비스.loc[data_건강관리장비와서비스[i]<-3,i] = -3                
                      
                result_건강관리장비와서비스 = data_건강관리장비와서비스    
                result_건강관리장비와서비스 = result_건강관리장비와서비스.assign(z_score=np.nanmean(result_건강관리장비와서비스.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_건강관리장비와서비스[result_건강관리장비와서비스['z_score'].notnull()]
                a=a+1
                
            if (np.sum(first_data['WICS_MID']=='제약과생물공학')>0)&(np.sum(sector_mom['CO_NM_x']=='제약과생물공학')==1):
                data_제약과생물공학 = first_data[first_data['WICS_MID']=='제약과생물공학']
                # 시총비중 구할떄는 free-float
                #        data_제약과생물공학['size_FIF_wisefn']=data_제약과생물공학['size_FIF_wisefn']/1000    #size 단위 thousand
                data_제약과생물공학.loc[:,'size_FIF_wisefn']=data_제약과생물공학.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_제약과생물공학 = data_제약과생물공학.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_제약과생물공학_{}'.format(i)] = data_제약과생물공학[data_제약과생물공학.iloc[:,i].notnull()]
                    locals()['data_제약과생물공학_cap_{}'.format(i)] = np.sum(locals()['data_제약과생물공학_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_제약과생물공학_{}'.format(i)] = locals()['data_제약과생물공학_{}'.format(i)].assign(market_weight=locals()['data_제약과생물공학_{}'.format(i)]['size_FIF_wisefn']/locals()['data_제약과생물공학_cap_{}'.format(i)])
                    locals()['data_제약과생물공학_mu_{}'.format(i)] = np.sum(locals()['data_제약과생물공학_{}'.format(i)].iloc[:,i]*locals()['data_제약과생물공학_{}'.format(i)]['market_weight'])
                    locals()['data_제약과생물공학_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_제약과생물공학_{}'.format(i)].iloc[:,i]-locals()['data_제약과생물공학_mu_{}'.format(i)])*locals()['data_제약과생물공학_{}'.format(i)]['market_weight']))
                    data_제약과생물공학[i] = (locals()['data_제약과생물공학_{}'.format(i)].iloc[:,i]-locals()['data_제약과생물공학_mu_{}'.format(i)])/locals()['data_제약과생물공학_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_제약과생물공학.loc[data_제약과생물공학[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_제약과생물공학.loc[data_제약과생물공학[i]<-3,i] = -3                
                      
                result_제약과생물공학 = data_제약과생물공학    
                result_제약과생물공학 = result_제약과생물공학.assign(z_score=np.nanmean(result_제약과생물공학.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_제약과생물공학[result_제약과생물공학['z_score'].notnull()]
                a=a+1
                
            if (np.sum(first_data['WICS_MID']=='은행')>0)&(np.sum(sector_mom['CO_NM_x']=='은행')==1):
                data_은행 = first_data[first_data['WICS_MID']=='은행']
                # 시총비중 구할떄는 free-float
                #        data_은행['size_FIF_wisefn']=data_은행['size_FIF_wisefn']/1000    #size 단위 thousand
                data_은행.loc[:,'size_FIF_wisefn']=data_은행.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_은행 = data_은행.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_은행_{}'.format(i)] = data_은행[data_은행.iloc[:,i].notnull()]
                    locals()['data_은행_cap_{}'.format(i)] = np.sum(locals()['data_은행_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_은행_{}'.format(i)] = locals()['data_은행_{}'.format(i)].assign(market_weight=locals()['data_은행_{}'.format(i)]['size_FIF_wisefn']/locals()['data_은행_cap_{}'.format(i)])
                    locals()['data_은행_mu_{}'.format(i)] = np.sum(locals()['data_은행_{}'.format(i)].iloc[:,i]*locals()['data_은행_{}'.format(i)]['market_weight'])
                    locals()['data_은행_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_은행_{}'.format(i)].iloc[:,i]-locals()['data_은행_mu_{}'.format(i)])*locals()['data_은행_{}'.format(i)]['market_weight']))
                    data_은행[i] = (locals()['data_은행_{}'.format(i)].iloc[:,i]-locals()['data_은행_mu_{}'.format(i)])/locals()['data_은행_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_은행.loc[data_은행[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_은행.loc[data_은행[i]<-3,i] = -3                
                      
                result_은행 = data_은행    
                result_은행 = result_은행.assign(z_score=np.nanmean(result_은행.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_은행[result_은행['z_score'].notnull()]
                a=a+1
                
            if (np.sum(first_data['WICS_MID']=='증권')>0)&(np.sum(sector_mom['CO_NM_x']=='증권')==1):
                data_증권 = first_data[first_data['WICS_MID']=='증권']
                # 시총비중 구할떄는 free-float
                #        data_증권['size_FIF_wisefn']=data_증권['size_FIF_wisefn']/1000    #size 단위 thousand
                data_증권.loc[:,'size_FIF_wisefn']=data_증권.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_증권 = data_증권.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_증권_{}'.format(i)] = data_증권[data_증권.iloc[:,i].notnull()]
                    locals()['data_증권_cap_{}'.format(i)] = np.sum(locals()['data_증권_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_증권_{}'.format(i)] = locals()['data_증권_{}'.format(i)].assign(market_weight=locals()['data_증권_{}'.format(i)]['size_FIF_wisefn']/locals()['data_증권_cap_{}'.format(i)])
                    locals()['data_증권_mu_{}'.format(i)] = np.sum(locals()['data_증권_{}'.format(i)].iloc[:,i]*locals()['data_증권_{}'.format(i)]['market_weight'])
                    locals()['data_증권_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_증권_{}'.format(i)].iloc[:,i]-locals()['data_증권_mu_{}'.format(i)])*locals()['data_증권_{}'.format(i)]['market_weight']))
                    data_증권[i] = (locals()['data_증권_{}'.format(i)].iloc[:,i]-locals()['data_증권_mu_{}'.format(i)])/locals()['data_증권_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_증권.loc[data_증권[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_증권.loc[data_증권[i]<-3,i] = -3                
                      
                result_증권 = data_증권    
                result_증권 = result_증권.assign(z_score=np.nanmean(result_증권.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_증권[result_증권['z_score'].notnull()]
                a=a+1
                
            if (np.sum(first_data['WICS_MID']=='다각화된금융')>0)&(np.sum(sector_mom['CO_NM_x']=='다각화된금융')==1):
                data_다각화된금융 = first_data[first_data['WICS_MID']=='다각화된금융']
                # 시총비중 구할떄는 free-float
                #        data_다각화된금융['size_FIF_wisefn']=data_다각화된금융['size_FIF_wisefn']/1000    #size 단위 thousand
                data_다각화된금융.loc[:,'size_FIF_wisefn']=data_다각화된금융.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_다각화된금융 = data_다각화된금융.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_다각화된금융_{}'.format(i)] = data_다각화된금융[data_다각화된금융.iloc[:,i].notnull()]
                    locals()['data_다각화된금융_cap_{}'.format(i)] = np.sum(locals()['data_다각화된금융_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_다각화된금융_{}'.format(i)] = locals()['data_다각화된금융_{}'.format(i)].assign(market_weight=locals()['data_다각화된금융_{}'.format(i)]['size_FIF_wisefn']/locals()['data_다각화된금융_cap_{}'.format(i)])
                    locals()['data_다각화된금융_mu_{}'.format(i)] = np.sum(locals()['data_다각화된금융_{}'.format(i)].iloc[:,i]*locals()['data_다각화된금융_{}'.format(i)]['market_weight'])
                    locals()['data_다각화된금융_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_다각화된금융_{}'.format(i)].iloc[:,i]-locals()['data_다각화된금융_mu_{}'.format(i)])*locals()['data_다각화된금융_{}'.format(i)]['market_weight']))
                    data_다각화된금융[i] = (locals()['data_다각화된금융_{}'.format(i)].iloc[:,i]-locals()['data_다각화된금융_mu_{}'.format(i)])/locals()['data_다각화된금융_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_다각화된금융.loc[data_다각화된금융[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_다각화된금융.loc[data_다각화된금융[i]<-3,i] = -3                
                      
                result_다각화된금융 = data_다각화된금융    
                result_다각화된금융 = result_다각화된금융.assign(z_score=np.nanmean(result_다각화된금융.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_다각화된금융[result_다각화된금융['z_score'].notnull()]
                a=a+1
                
            if (np.sum(first_data['WICS_MID']=='보험')>0)&(np.sum(sector_mom['CO_NM_x']=='보험')==1):
                data_보험 = first_data[first_data['WICS_MID']=='보험']
                # 시총비중 구할떄는 free-float
                #        data_보험['size_FIF_wisefn']=data_보험['size_FIF_wisefn']/1000    #size 단위 thousand
                data_보험.loc[:,'size_FIF_wisefn']=data_보험.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_보험 = data_보험.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_보험_{}'.format(i)] = data_보험[data_보험.iloc[:,i].notnull()]
                    locals()['data_보험_cap_{}'.format(i)] = np.sum(locals()['data_보험_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_보험_{}'.format(i)] = locals()['data_보험_{}'.format(i)].assign(market_weight=locals()['data_보험_{}'.format(i)]['size_FIF_wisefn']/locals()['data_보험_cap_{}'.format(i)])
                    locals()['data_보험_mu_{}'.format(i)] = np.sum(locals()['data_보험_{}'.format(i)].iloc[:,i]*locals()['data_보험_{}'.format(i)]['market_weight'])
                    locals()['data_보험_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_보험_{}'.format(i)].iloc[:,i]-locals()['data_보험_mu_{}'.format(i)])*locals()['data_보험_{}'.format(i)]['market_weight']))
                    data_보험[i] = (locals()['data_보험_{}'.format(i)].iloc[:,i]-locals()['data_보험_mu_{}'.format(i)])/locals()['data_보험_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_보험.loc[data_보험[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_보험.loc[data_보험[i]<-3,i] = -3                
                      
                result_보험 = data_보험    
                result_보험 = result_보험.assign(z_score=np.nanmean(result_보험.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_보험[result_보험['z_score'].notnull()]
                a=a+1
                
            if (np.sum(first_data['WICS_MID']=='부동산')>0)&(np.sum(sector_mom['CO_NM_x']=='부동산')==1):
                data_부동산 = first_data[first_data['WICS_MID']=='부동산']
                # 시총비중 구할떄는 free-float
                #        data_부동산['size_FIF_wisefn']=data_부동산['size_FIF_wisefn']/1000    #size 단위 thousand
                data_부동산.loc[:,'size_FIF_wisefn']=data_부동산.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_부동산 = data_부동산.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_부동산_{}'.format(i)] = data_부동산[data_부동산.iloc[:,i].notnull()]
                    locals()['data_부동산_cap_{}'.format(i)] = np.sum(locals()['data_부동산_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_부동산_{}'.format(i)] = locals()['data_부동산_{}'.format(i)].assign(market_weight=locals()['data_부동산_{}'.format(i)]['size_FIF_wisefn']/locals()['data_부동산_cap_{}'.format(i)])
                    locals()['data_부동산_mu_{}'.format(i)] = np.sum(locals()['data_부동산_{}'.format(i)].iloc[:,i]*locals()['data_부동산_{}'.format(i)]['market_weight'])
                    locals()['data_부동산_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_부동산_{}'.format(i)].iloc[:,i]-locals()['data_부동산_mu_{}'.format(i)])*locals()['data_부동산_{}'.format(i)]['market_weight']))
                    data_부동산[i] = (locals()['data_부동산_{}'.format(i)].iloc[:,i]-locals()['data_부동산_mu_{}'.format(i)])/locals()['data_부동산_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_부동산.loc[data_부동산[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_부동산.loc[data_부동산[i]<-3,i] = -3                
                      
                result_부동산 = data_부동산    
                result_부동산 = result_부동산.assign(z_score=np.nanmean(result_부동산.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_부동산[result_부동산['z_score'].notnull()]
                a=a+1
                
            if (np.sum(first_data['WICS_MID']=='기타금융서비스')>0)&(np.sum(sector_mom['CO_NM_x']=='기타금융서비스')==1):
                data_기타금융서비스 = first_data[first_data['WICS_MID']=='기타금융서비스']
                # 시총비중 구할떄는 free-float
                #        data_기타금융서비스['size_FIF_wisefn']=data_기타금융서비스['size_FIF_wisefn']/1000    #size 단위 thousand
                data_기타금융서비스.loc[:,'size_FIF_wisefn']=data_기타금융서비스.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_기타금융서비스 = data_기타금융서비스.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_기타금융서비스_{}'.format(i)] = data_기타금융서비스[data_기타금융서비스.iloc[:,i].notnull()]
                    locals()['data_기타금융서비스_cap_{}'.format(i)] = np.sum(locals()['data_기타금융서비스_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_기타금융서비스_{}'.format(i)] = locals()['data_기타금융서비스_{}'.format(i)].assign(market_weight=locals()['data_기타금융서비스_{}'.format(i)]['size_FIF_wisefn']/locals()['data_기타금융서비스_cap_{}'.format(i)])
                    locals()['data_기타금융서비스_mu_{}'.format(i)] = np.sum(locals()['data_기타금융서비스_{}'.format(i)].iloc[:,i]*locals()['data_기타금융서비스_{}'.format(i)]['market_weight'])
                    locals()['data_기타금융서비스_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_기타금융서비스_{}'.format(i)].iloc[:,i]-locals()['data_기타금융서비스_mu_{}'.format(i)])*locals()['data_기타금융서비스_{}'.format(i)]['market_weight']))
                    data_기타금융서비스[i] = (locals()['data_기타금융서비스_{}'.format(i)].iloc[:,i]-locals()['data_기타금융서비스_mu_{}'.format(i)])/locals()['data_기타금융서비스_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_기타금융서비스.loc[data_기타금융서비스[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_기타금융서비스.loc[data_기타금융서비스[i]<-3,i] = -3                
                      
                result_기타금융서비스 = data_기타금융서비스    
                result_기타금융서비스 = result_기타금융서비스.assign(z_score=np.nanmean(result_기타금융서비스.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_기타금융서비스[result_기타금융서비스['z_score'].notnull()]
                a=a+1
                
            if (np.sum(first_data['WICS_MID']=='소프트웨어와서비스')>0)&(np.sum(sector_mom['CO_NM_x']=='소프트웨어와서비스')==1):
                data_소프트웨어와서비스 = first_data[first_data['WICS_MID']=='소프트웨어와서비스']
                # 시총비중 구할떄는 free-float
                #        data_소프트웨어와서비스['size_FIF_wisefn']=data_소프트웨어와서비스['size_FIF_wisefn']/1000    #size 단위 thousand
                data_소프트웨어와서비스.loc[:,'size_FIF_wisefn']=data_소프트웨어와서비스.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_소프트웨어와서비스 = data_소프트웨어와서비스.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_소프트웨어와서비스_{}'.format(i)] = data_소프트웨어와서비스[data_소프트웨어와서비스.iloc[:,i].notnull()]
                    locals()['data_소프트웨어와서비스_cap_{}'.format(i)] = np.sum(locals()['data_소프트웨어와서비스_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_소프트웨어와서비스_{}'.format(i)] = locals()['data_소프트웨어와서비스_{}'.format(i)].assign(market_weight=locals()['data_소프트웨어와서비스_{}'.format(i)]['size_FIF_wisefn']/locals()['data_소프트웨어와서비스_cap_{}'.format(i)])
                    locals()['data_소프트웨어와서비스_mu_{}'.format(i)] = np.sum(locals()['data_소프트웨어와서비스_{}'.format(i)].iloc[:,i]*locals()['data_소프트웨어와서비스_{}'.format(i)]['market_weight'])
                    locals()['data_소프트웨어와서비스_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_소프트웨어와서비스_{}'.format(i)].iloc[:,i]-locals()['data_소프트웨어와서비스_mu_{}'.format(i)])*locals()['data_소프트웨어와서비스_{}'.format(i)]['market_weight']))
                    data_소프트웨어와서비스[i] = (locals()['data_소프트웨어와서비스_{}'.format(i)].iloc[:,i]-locals()['data_소프트웨어와서비스_mu_{}'.format(i)])/locals()['data_소프트웨어와서비스_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_소프트웨어와서비스.loc[data_소프트웨어와서비스[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_소프트웨어와서비스.loc[data_소프트웨어와서비스[i]<-3,i] = -3                
                      
                result_소프트웨어와서비스 = data_소프트웨어와서비스    
                result_소프트웨어와서비스 = result_소프트웨어와서비스.assign(z_score=np.nanmean(result_소프트웨어와서비스.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_소프트웨어와서비스[result_소프트웨어와서비스['z_score'].notnull()]
                a=a+1
                
            if (np.sum(first_data['WICS_MID']=='기술하드웨어와장비')>0)&(np.sum(sector_mom['CO_NM_x']=='기술하드웨어와장비')==1):
                data_기술하드웨어와장비 = first_data[first_data['WICS_MID']=='기술하드웨어와장비']
                # 시총비중 구할떄는 free-float
                #        data_기술하드웨어와장비['size_FIF_wisefn']=data_기술하드웨어와장비['size_FIF_wisefn']/1000    #size 단위 thousand
                data_기술하드웨어와장비.loc[:,'size_FIF_wisefn']=data_기술하드웨어와장비.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_기술하드웨어와장비 = data_기술하드웨어와장비.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_기술하드웨어와장비_{}'.format(i)] = data_기술하드웨어와장비[data_기술하드웨어와장비.iloc[:,i].notnull()]
                    locals()['data_기술하드웨어와장비_cap_{}'.format(i)] = np.sum(locals()['data_기술하드웨어와장비_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_기술하드웨어와장비_{}'.format(i)] = locals()['data_기술하드웨어와장비_{}'.format(i)].assign(market_weight=locals()['data_기술하드웨어와장비_{}'.format(i)]['size_FIF_wisefn']/locals()['data_기술하드웨어와장비_cap_{}'.format(i)])
                    locals()['data_기술하드웨어와장비_mu_{}'.format(i)] = np.sum(locals()['data_기술하드웨어와장비_{}'.format(i)].iloc[:,i]*locals()['data_기술하드웨어와장비_{}'.format(i)]['market_weight'])
                    locals()['data_기술하드웨어와장비_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_기술하드웨어와장비_{}'.format(i)].iloc[:,i]-locals()['data_기술하드웨어와장비_mu_{}'.format(i)])*locals()['data_기술하드웨어와장비_{}'.format(i)]['market_weight']))
                    data_기술하드웨어와장비[i] = (locals()['data_기술하드웨어와장비_{}'.format(i)].iloc[:,i]-locals()['data_기술하드웨어와장비_mu_{}'.format(i)])/locals()['data_기술하드웨어와장비_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_기술하드웨어와장비.loc[data_기술하드웨어와장비[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_기술하드웨어와장비.loc[data_기술하드웨어와장비[i]<-3,i] = -3                
                      
                result_기술하드웨어와장비 = data_기술하드웨어와장비    
                result_기술하드웨어와장비 = result_기술하드웨어와장비.assign(z_score=np.nanmean(result_기술하드웨어와장비.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_기술하드웨어와장비[result_기술하드웨어와장비['z_score'].notnull()]
                a=a+1
                
            if (np.sum(first_data['WICS_MID']=='반도체와반도체장비')>0)&(np.sum(sector_mom['CO_NM_x']=='반도체와반도체장비')==1):
                data_반도체와반도체장비 = first_data[first_data['WICS_MID']=='반도체와반도체장비']
                # 시총비중 구할떄는 free-float
                #        data_반도체와반도체장비['size_FIF_wisefn']=data_반도체와반도체장비['size_FIF_wisefn']/1000    #size 단위 thousand
                data_반도체와반도체장비.loc[:,'size_FIF_wisefn']=data_반도체와반도체장비.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_반도체와반도체장비 = data_반도체와반도체장비.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_반도체와반도체장비_{}'.format(i)] = data_반도체와반도체장비[data_반도체와반도체장비.iloc[:,i].notnull()]
                    locals()['data_반도체와반도체장비_cap_{}'.format(i)] = np.sum(locals()['data_반도체와반도체장비_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_반도체와반도체장비_{}'.format(i)] = locals()['data_반도체와반도체장비_{}'.format(i)].assign(market_weight=locals()['data_반도체와반도체장비_{}'.format(i)]['size_FIF_wisefn']/locals()['data_반도체와반도체장비_cap_{}'.format(i)])
                    locals()['data_반도체와반도체장비_mu_{}'.format(i)] = np.sum(locals()['data_반도체와반도체장비_{}'.format(i)].iloc[:,i]*locals()['data_반도체와반도체장비_{}'.format(i)]['market_weight'])
                    locals()['data_반도체와반도체장비_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_반도체와반도체장비_{}'.format(i)].iloc[:,i]-locals()['data_반도체와반도체장비_mu_{}'.format(i)])*locals()['data_반도체와반도체장비_{}'.format(i)]['market_weight']))
                    data_반도체와반도체장비[i] = (locals()['data_반도체와반도체장비_{}'.format(i)].iloc[:,i]-locals()['data_반도체와반도체장비_mu_{}'.format(i)])/locals()['data_반도체와반도체장비_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_반도체와반도체장비.loc[data_반도체와반도체장비[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_반도체와반도체장비.loc[data_반도체와반도체장비[i]<-3,i] = -3                
                      
                result_반도체와반도체장비 = data_반도체와반도체장비    
                result_반도체와반도체장비 = result_반도체와반도체장비.assign(z_score=np.nanmean(result_반도체와반도체장비.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_반도체와반도체장비[result_반도체와반도체장비['z_score'].notnull()]
                a=a+1
                
            if (np.sum(first_data['WICS_MID']=='전자와_전기제품')>0)&(np.sum(sector_mom['CO_NM_x']=='전자와_전기제품')==1):
                data_전자와_전기제품 = first_data[first_data['WICS_MID']=='전자와_전기제품']
                # 시총비중 구할떄는 free-float
                #        data_전자와_전기제품['size_FIF_wisefn']=data_전자와_전기제품['size_FIF_wisefn']/1000    #size 단위 thousand
                data_전자와_전기제품.loc[:,'size_FIF_wisefn']=data_전자와_전기제품.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_전자와_전기제품 = data_전자와_전기제품.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_전자와_전기제품_{}'.format(i)] = data_전자와_전기제품[data_전자와_전기제품.iloc[:,i].notnull()]
                    locals()['data_전자와_전기제품_cap_{}'.format(i)] = np.sum(locals()['data_전자와_전기제품_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_전자와_전기제품_{}'.format(i)] = locals()['data_전자와_전기제품_{}'.format(i)].assign(market_weight=locals()['data_전자와_전기제품_{}'.format(i)]['size_FIF_wisefn']/locals()['data_전자와_전기제품_cap_{}'.format(i)])
                    locals()['data_전자와_전기제품_mu_{}'.format(i)] = np.sum(locals()['data_전자와_전기제품_{}'.format(i)].iloc[:,i]*locals()['data_전자와_전기제품_{}'.format(i)]['market_weight'])
                    locals()['data_전자와_전기제품_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_전자와_전기제품_{}'.format(i)].iloc[:,i]-locals()['data_전자와_전기제품_mu_{}'.format(i)])*locals()['data_전자와_전기제품_{}'.format(i)]['market_weight']))
                    data_전자와_전기제품[i] = (locals()['data_전자와_전기제품_{}'.format(i)].iloc[:,i]-locals()['data_전자와_전기제품_mu_{}'.format(i)])/locals()['data_전자와_전기제품_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_전자와_전기제품.loc[data_전자와_전기제품[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_전자와_전기제품.loc[data_전자와_전기제품[i]<-3,i] = -3                
                      
                result_전자와_전기제품 = data_전자와_전기제품    
                result_전자와_전기제품 = result_전자와_전기제품.assign(z_score=np.nanmean(result_전자와_전기제품.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_전자와_전기제품[result_전자와_전기제품['z_score'].notnull()]
                a=a+1
                
            if (np.sum(first_data['WICS_MID']=='디스플레이')>0)&(np.sum(sector_mom['CO_NM_x']=='디스플레이')==1):
                data_디스플레이 = first_data[first_data['WICS_MID']=='디스플레이']
                # 시총비중 구할떄는 free-float
                #        data_디스플레이['size_FIF_wisefn']=data_디스플레이['size_FIF_wisefn']/1000    #size 단위 thousand
                data_디스플레이.loc[:,'size_FIF_wisefn']=data_디스플레이.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_디스플레이 = data_디스플레이.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_디스플레이_{}'.format(i)] = data_디스플레이[data_디스플레이.iloc[:,i].notnull()]
                    locals()['data_디스플레이_cap_{}'.format(i)] = np.sum(locals()['data_디스플레이_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_디스플레이_{}'.format(i)] = locals()['data_디스플레이_{}'.format(i)].assign(market_weight=locals()['data_디스플레이_{}'.format(i)]['size_FIF_wisefn']/locals()['data_디스플레이_cap_{}'.format(i)])
                    locals()['data_디스플레이_mu_{}'.format(i)] = np.sum(locals()['data_디스플레이_{}'.format(i)].iloc[:,i]*locals()['data_디스플레이_{}'.format(i)]['market_weight'])
                    locals()['data_디스플레이_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_디스플레이_{}'.format(i)].iloc[:,i]-locals()['data_디스플레이_mu_{}'.format(i)])*locals()['data_디스플레이_{}'.format(i)]['market_weight']))
                    data_디스플레이[i] = (locals()['data_디스플레이_{}'.format(i)].iloc[:,i]-locals()['data_디스플레이_mu_{}'.format(i)])/locals()['data_디스플레이_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_디스플레이.loc[data_디스플레이[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_디스플레이.loc[data_디스플레이[i]<-3,i] = -3                
                      
                result_디스플레이 = data_디스플레이    
                result_디스플레이 = result_디스플레이.assign(z_score=np.nanmean(result_디스플레이.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_디스플레이[result_디스플레이['z_score'].notnull()]
                a=a+1
                
            if (np.sum(first_data['WICS_MID']=='통신서비스')>0)&(np.sum(sector_mom['CO_NM_x']=='통신서비스')==1):
                data_통신서비스 = first_data[first_data['WICS_MID']=='통신서비스']
                # 시총비중 구할떄는 free-float
                #        data_통신서비스['size_FIF_wisefn']=data_통신서비스['size_FIF_wisefn']/1000    #size 단위 thousand
                data_통신서비스.loc[:,'size_FIF_wisefn']=data_통신서비스.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_통신서비스 = data_통신서비스.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_통신서비스_{}'.format(i)] = data_통신서비스[data_통신서비스.iloc[:,i].notnull()]
                    locals()['data_통신서비스_cap_{}'.format(i)] = np.sum(locals()['data_통신서비스_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_통신서비스_{}'.format(i)] = locals()['data_통신서비스_{}'.format(i)].assign(market_weight=locals()['data_통신서비스_{}'.format(i)]['size_FIF_wisefn']/locals()['data_통신서비스_cap_{}'.format(i)])
                    locals()['data_통신서비스_mu_{}'.format(i)] = np.sum(locals()['data_통신서비스_{}'.format(i)].iloc[:,i]*locals()['data_통신서비스_{}'.format(i)]['market_weight'])
                    locals()['data_통신서비스_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_통신서비스_{}'.format(i)].iloc[:,i]-locals()['data_통신서비스_mu_{}'.format(i)])*locals()['data_통신서비스_{}'.format(i)]['market_weight']))
                    data_통신서비스[i] = (locals()['data_통신서비스_{}'.format(i)].iloc[:,i]-locals()['data_통신서비스_mu_{}'.format(i)])/locals()['data_통신서비스_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_통신서비스.loc[data_통신서비스[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_통신서비스.loc[data_통신서비스[i]<-3,i] = -3                
                      
                result_통신서비스 = data_통신서비스    
                result_통신서비스 = result_통신서비스.assign(z_score=np.nanmean(result_통신서비스.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_통신서비스[result_통신서비스['z_score'].notnull()]
                a=a+1
                               
            if (np.sum(first_data['WICS_MID']=='유틸리티')>0)&(np.sum(sector_mom['CO_NM_x']=='유틸리티')==1):
                data_유틸리티 = first_data[first_data['WICS_MID']=='유틸리티']
                # 시총비중 구할떄는 free-float
                #        data_유틸리티['size_FIF_wisefn']=data_유틸리티['size_FIF_wisefn']/1000    #size 단위 thousand
                data_유틸리티.loc[:,'size_FIF_wisefn']=data_유틸리티.loc[:,'size_FIF_wisefn']/1000   
                # inf, -inf 값들을 NAN 값으로 변경 (그래야 한번에 제거 가능)
                data_유틸리티 = data_유틸리티.replace([np.inf, -np.inf],np.nan)  
                   
                for i in self.col_loc:
                    locals()['data_유틸리티_{}'.format(i)] = data_유틸리티[data_유틸리티.iloc[:,i].notnull()]
                    locals()['data_유틸리티_cap_{}'.format(i)] = np.sum(locals()['data_유틸리티_{}'.format(i)]['size_FIF_wisefn'])
                    locals()['data_유틸리티_{}'.format(i)] = locals()['data_유틸리티_{}'.format(i)].assign(market_weight=locals()['data_유틸리티_{}'.format(i)]['size_FIF_wisefn']/locals()['data_유틸리티_cap_{}'.format(i)])
                    locals()['data_유틸리티_mu_{}'.format(i)] = np.sum(locals()['data_유틸리티_{}'.format(i)].iloc[:,i]*locals()['data_유틸리티_{}'.format(i)]['market_weight'])
                    locals()['data_유틸리티_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['data_유틸리티_{}'.format(i)].iloc[:,i]-locals()['data_유틸리티_mu_{}'.format(i)])*locals()['data_유틸리티_{}'.format(i)]['market_weight']))
                    data_유틸리티[i] = (locals()['data_유틸리티_{}'.format(i)].iloc[:,i]-locals()['data_유틸리티_mu_{}'.format(i)])/locals()['data_유틸리티_std_{}'.format(i)]

                for i in self.col_loc:                  
                    data_유틸리티.loc[data_유틸리티[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                    data_유틸리티.loc[data_유틸리티[i]<-3,i] = -3                
                      
                result_유틸리티 = data_유틸리티    
                result_유틸리티 = result_유틸리티.assign(z_score=np.nanmean(result_유틸리티.loc[:,self.col_loc],axis=1))
                #    result_temp = result
                
                
                # z_score > 0 인것이 가치주라고 msci에서 하고있음
                locals()['result_{}'.format(a)] =result_유틸리티[result_유틸리티['z_score'].notnull()]
                a=a+1                                                                                 
            
            for y in range(2,a):    
                 locals()['result_{}'.format(1)] = pd.concat([locals()['result_{}'.format(1)],locals()['result_{}'.format(y)]],axis=0,join='inner')
   
    
            result = locals()['result_{}'.format(1)]
            result=result.assign(rnk=result['z_score'].rank(method='first',ascending=False)) 
            
#            for i in col_loc:
#                samsung[i]=0
#                samsung['z_score'] = 0
#                samsung['rnk'] = 0                                       
#            
#            result = pd.concat([result,samsung])
            result = result.drop_duplicates(subset='CO_NM', keep='last')
            result = result[result['rnk']<25]
            
            sum_data = pd.merge(target_data,result,on='GICODE') # 3개월치 수익률을 구하기 위해 3개월 후 존재하는 data에 현재 data를 붙임
            sum_data['3M_RETURN'] = sum_data['ADJ_PRC_x']/sum_data['ADJ_PRC_y'] # 3개월동안의 종목 수익률
            
            #월별 수익률을 구해보자
            #월별 수익률을 구하기 위해 month_date 에서 필요한 날짜가 몇번쨰 row에 있는지 확인
            past_month=self.month_date.loc[self.month_date['MONTH_DATE']==self.rebalancing_date.iloc[n,0]].index[0]
            cur_month=self.month_date.loc[self.month_date['MONTH_DATE']==self.rebalancing_date.iloc[n+1,0]].index[0]
            
            first_data = result.loc[:,['TRD_DATE','GICODE','ADJ_PRC']]
            for i in range(past_month+1,cur_month): # 3개월치의 월별 수익률을 구하기 위해선 4개의 price 데이터가 필요한데 2개밖에 없으니 2개를 더 받아온다.
                second_data = self.raw_data[self.raw_data['TRD_DATE']==self.month_date.iloc[i,0]]  #월별 데이터를 받아와서
                second_data = second_data.loc[:,['TRD_DATE','GICODE','ADJ_PRC']]   # 간단하게 만든다음
                first_data = pd.merge(first_data,second_data,on='GICODE')   # first_data와 합친다
            
            first_data['1ST_RETURN'] =  first_data['ADJ_PRC_y']/ first_data['ADJ_PRC_x']   #0->1 , 즉 첫 한개월간의 수익률
            first_data['2ND_RETURN'] =  first_data['ADJ_PRC']/ first_data['ADJ_PRC_y']# 1->2 한달이후 한달간 수익률
            first_data = first_data.loc[:,['GICODE','1ST_RETURN','2ND_RETURN']] #데이터를 간단하게 만들어준다음
            sum_data = pd.merge(sum_data,first_data,on='GICODE') # 기존 data와 합친다.
            sum_data['2M_CUM_RETURN'] = sum_data['1ST_RETURN'] * sum_data['2ND_RETURN'] 
            
            result = sum_data # 기존 코드를 RESULT로 만들어놔서..
                
            quarter_data[[3*n,3*n+1,3*n+2]] = result.loc[:,['CO_NM','CAP_SIZE','3M_RETURN']].reset_index(drop=True) #매 분기마다 종목명, 시가총액나눔, 3개월 수익률 저장
            market_capital=np.sum(result['size_FIF_wisefn']) # 전체 시가총액 -> 삼성전자 시총 비중을 구하기 위해
            result=result.assign(market_weight2=result['size_FIF_wisefn']/market_capital)          
            
            #전체 동일가중
            return_data.loc[0,n]=np.mean(result['3M_RETURN']) # 390이 삼성전자 index
            
            #전체 동일가중 투자
            return_month_data[3*n] = np.mean(result['1ST_RETURN'])
            return_month_data[3*n+1] = np.mean(result['2M_CUM_RETURN'])/return_month_data[3*n]
            return_month_data[3*n+2] = np.mean(result['3M_RETURN'])/np.mean(result['2M_CUM_RETURN'])

            #매 분기 종목 이름 저장
            data_name[n]=result['CO_NM'].reset_index(drop=True)                                            
                                                    
    
     
        
            return_final=np.product(return_data,axis=1)
                    #turnover 계산    
        for n in range(col_length-1):
            len1 = len(data_name[data_name[n+1].notnull()])
            aaa=data_name.loc[:,[n,n+1]]
            bbb=pd.DataFrame(aaa.stack().value_counts())
            len2=len(bbb[bbb[0]==2])
            data_name.loc[999,n+1]=(len1-len2)/len1
            turnover_quarter=data_name.loc[999,1:]
                
        turnover=np.mean(turnover_quarter)   
        #turnvoer에 1.5% 곱해서 거래비용 계산하기
        #첫기에는 거래비용이 100%이다
        
        turnover_quarter[0]=0
        turnover_quarter[4]=1
        turnover_quarter = turnover_quarter * 0.01
        return_diff = return_data - turnover_quarter
        return_transaction_cost_final=np.product(return_diff,axis=1)    
            
        #monthly data에도 cost 반영
        import copy   # 엠창 존나 어려운거발견함 장족의 발전이다
        #deep copy랑 swallow copy 가 있는데  a=[1,2,3]을 만들면 a에 [1,2,3]이 저장되는게 아니라
        #[1,2,3]이라는 객체가 생성되고 여기에 a 가 할당됨. 그런데 여기다 a=b 를 해버리면 b도 
        # 저 객체에 할당되어버려서, b를변경하든 a를 변경하든 같이 바뀜. 
        #deep copy를 하면 새로운 객체가 생김.
        return_month_data_costed = copy.deepcopy(return_month_data)
        
        
        # monthly data에 turnover cost를 빼는건, 종목을 변경한 달에 적용...
        for n in range(4,col_length):
            return_month_data_costed[3*n] = np.subtract(return_month_data[3*n],turnover_quarter[n])
        
            
            
#               
        
            
        return [return_final, return_diff, return_month_data_costed, data_name]  # 이렇게 return 하면 list로 받아짐
                
        