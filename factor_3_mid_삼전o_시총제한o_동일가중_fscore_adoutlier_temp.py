# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 09:24:22 2017

@author: SH-NoteBook
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 14:57:16 2017

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
class factor_3_mid_adoutlier:
 
    def __init__(self,raw_data,rebalancing_date,month_date,wics_mid,col_num,col_num2,col_num3):
        raw_data = raw_data
        rebalancing_date = rebalancing_date
        month_date = month_date
        col_num = 47
        col_num2 = 48
        col_num3 = 49
        col_loc = [col_num,col_num2,col_num3] 
        wics_mid = wics_mid
       
        

    def factor_3_mid_adoutlier(self):
        col_length = len(rebalancing_date)-1 #rebalancing_date의 길이는 66이다. range로 이렇게 하면 0부터 65까지 66개의 i 가 만들어진다. -1을 해준건 실제 수익률은 -1개가 생성되기 때문.
        
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
            first_mom = wics_mid[wics_mid['TRD_DATE']==rebalancing_date.iloc[n,0]] 
            cur_mom_row=month_date.loc[month_date['MONTH_DATE']==rebalancing_date.iloc[n,0]].index[0]
            
            #cur_month=month_date.loc[month_date['MONTH_DATE']==rebalancing_date.iloc[n+1,0]].index[0]
            
            mom_return_data_1 = wics_mid[wics_mid['TRD_DATE']==month_date.iloc[cur_mom_row-1,0]] #t-2 data
            mom_return_data_2 = wics_mid[wics_mid['TRD_DATE']==month_date.iloc[cur_mom_row-12,0]] #t-12 data
            mom_return_data_1 = pd.merge(mom_return_data_1,mom_return_data_2,on='GICODE') # 따로따로 계산하려고 했더니 index가 안맞아서 gicode로 merge 했다.
            mom_return_data_1['11M_GROSS_RETURN'] = mom_return_data_1['END_PRICE_x'] / mom_return_data_1['END_PRICE_y'] # 머지하면 index가 필요 없어져서 수익률 계산이 쉬워짐
            
            mom_return_data_1=mom_return_data_1.assign(rnk=np.floor(mom_return_data_1['11M_GROSS_RETURN'].rank(method='first',ascending=False))) # 누적수익률이 높은 섹터별로 ranking
            sector_mom = mom_return_data_1.query('rnk<16') #상위 15 섹터 선택 완료
    
            first_data = raw_data[raw_data['TRD_DATE']==rebalancing_date.iloc[n,0]] # rebalanging할 날짜에 들어있는 모든 db data를 받아온다.
            target_data = raw_data[raw_data['TRD_DATE']==rebalancing_date.iloc[n+1,0]]
            target_data = target_data.loc[:,['TRD_DATE','GICODE','ADJ_PRC']]
            first_data = first_data[(first_data['CAP_SIZE']==1)|(first_data['CAP_SIZE']==2)|(first_data['CAP_SIZE']==3)|(first_data['ISKOSDAQ']=='KOSDAQ')]
            first_data = first_data[first_data['MARKET_CAP']>100000000000]
#            first_data = first_data[first_data['EQUITY'].notnull()] ################################################
#            first_data['size_FIF_wisefn'] = first_data['JISU_STOCK']*first_data['FIF_RATIO']*first_data['ADJ_PRC'] # f_score을 body에서 column index로 주기 위해서는 순서가 중요하다. 따라서 매번 선언해주지 않고 raw_data선에서 한번에 선언해주어서 column index 순서를 앞쪽으로 .. => 팩터들끼리 모아둘 수 있게
            samsung = first_data[first_data['CO_NM']=='삼성전자']
            
            past_data = raw_data[raw_data['TRD_DATE']==rebalancing_date.iloc[n-4,0]] # 전년도와 비교하기 위해서 받아온다
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
            sector_mom = sector_mom.rename(columns={'CO_NM_x':'WICS_MID'}) # column 이름 변경
            first_data=pd.merge(sector_mom,first_data,on='WICS_MID') # 모멘텀 상위 15개 섹터에 존재하는 주식들 모임 <<<첫번째 팩터가 47번째..>
                      
            data_length = len(first_data) # 몇개의 종목이 rebalanging_date때 존재했는지 본다.
            
            first_data.loc[:,'size_FIF_wisefn']=first_data.loc[:,'size_FIF_wisefn']/1000  
            first_data = first_data.replace([np.inf, -np.inf],np.nan)  
            
            #팩터들 중에서 nan 값 제거 
            for i in col_loc:
                first_data = first_data[first_data.iloc[:,i].notnull()]
            
            # 팩터들 중에서 아웃라이어 제거
            for i in col_loc:  #섹터에 남는주식수가 너무 적어짐.. 5% 너무 많나??
                first_data = first_data[(first_data.iloc[:,i]>np.percentile(first_data.iloc[:,i],1))&(first_data.iloc[:,i]<np.percentile(first_data.iloc[:,i],99))]
#                
            for i in col_loc:
                locals()['first_data_{}'.format(i)] = first_data[first_data.iloc[:,i].notnull()]
                locals()['first_data_cap_{}'.format(i)] = np.sum(locals()['first_data_{}'.format(i)]['size_FIF_wisefn'])
                locals()['first_data_{}'.format(i)] = locals()['first_data_{}'.format(i)].assign(market_weight=locals()['first_data_{}'.format(i)]['size_FIF_wisefn']/locals()['first_data_cap_{}'.format(i)])
                locals()['first_data_mu_{}'.format(i)] = np.sum(locals()['first_data_{}'.format(i)].iloc[:,i]*locals()['first_data_{}'.format(i)]['market_weight'])
                locals()['first_data_std_{}'.format(i)] = np.sqrt(np.sum(np.square(locals()['first_data_{}'.format(i)].iloc[:,i]-locals()['first_data_mu_{}'.format(i)])*locals()['first_data_{}'.format(i)]['market_weight']))
                first_data[i] = (locals()['first_data_{}'.format(i)].iloc[:,i]-locals()['first_data_mu_{}'.format(i)])/locals()['first_data_std_{}'.format(i)]
            
            #이제 섹터별로 z_score의 평균 빼줘서 표준화 
            
            for i in range(len(sector_mom)):
                locals()['data_{}'.format(i)] = first_data[first_data['WICS_MID']==sector_mom.iloc[i,2]]
                for j in col_loc:
                     locals()['data_{}'.format(i)][j] = locals()['data_{}'.format(i)][j] - np.mean(locals()['data_{}'.format(i)][j])
            
            for y in range(1,len(sector_mom)):    
                 locals()['data_{}'.format(0)] = pd.concat([locals()['data_{}'.format(0)],locals()['data_{}'.format(y)]],axis=0,join='inner')

            for i in col_loc:                  
                data_0.loc[data_0[i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                data_0.loc[data_0[i]<-3,i] = -3
                
            data_0 = data_0.assign(z_score=np.nanmean(data_0.loc[:,col_loc],axis=1))
            
            
            result = data_0
            result=result.assign(rnk=result['z_score'].rank(method='first',ascending=False)) 
            
            for i in col_loc:
                samsung[i]=0
                samsung['z_score'] = 0
                samsung['rnk'] = 0                                       
            
            result.drop('TRD_DATE_y', axis=1, inplace=True)
            result.drop('TRD_DATE_x', axis=1, inplace=True)
            result.drop('CO_NM_y_y', axis=1, inplace=True)
            result.drop('CO_NM_y_x', axis=1, inplace=True)
            result = result.rename(columns={'GICODE_x':'GICODE'}) # column 이름 변경
            result.drop('GICODE', axis=1, inplace=True)
            result = result.rename(columns={'GICODE_y':'GICODE'})
            samsung.drop('CO_NM_y', axis=1, inplace=True)
            
            
            result = pd.concat([result,samsung],axis=0)
            result = result.drop_duplicates(subset='CO_NM', keep='last')
            result = result[result['rnk']<25]
            
            sum_data = pd.merge(target_data,result,on='GICODE') # 3개월치 수익률을 구하기 위해 3개월 후 존재하는 data에 현재 data를 붙임
            sum_data['3M_RETURN'] = sum_data['ADJ_PRC_x']/sum_data['ADJ_PRC_y'] # 3개월동안의 종목 수익률
            
            #월별 수익률을 구해보자
            #월별 수익률을 구하기 위해 month_date 에서 필요한 날짜가 몇번쨰 row에 있는지 확인
            past_month=month_date.loc[month_date['MONTH_DATE']==rebalancing_date.iloc[n,0]].index[0]
            cur_month=month_date.loc[month_date['MONTH_DATE']==rebalancing_date.iloc[n+1,0]].index[0]
            
            first_data = result.loc[:,['TRD_DATE','GICODE','ADJ_PRC']]
            for i in range(past_month+1,cur_month): # 3개월치의 월별 수익률을 구하기 위해선 4개의 price 데이터가 필요한데 2개밖에 없으니 2개를 더 받아온다.
                second_data = raw_data[raw_data['TRD_DATE']==month_date.iloc[i,0]]  #월별 데이터를 받아와서
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
            
            first_data = raw_data[raw_data['TRD_DATE']==rebalancing_date.iloc[n,0]]
            samsung_weight = first_data[(first_data['CAP_SIZE']==1)|(first_data['CAP_SIZE']==2)|(first_data['CAP_SIZE']==3)]
            samsung_weight = pd.merge(target_data,samsung_weight,on='GICODE') # 3개월치 수익률을 구하기 위해 3개월 후 존재하는 data에 현재 data를 붙임
            samsung_weight['3M_RETURN'] = samsung_weight['ADJ_PRC_x']/samsung_weight['ADJ_PRC_y'] # 3개월동안의 종목 수익률
            samsung_weight=samsung_weight[samsung_weight['3M_RETURN']!=0]
            samsung_weight=samsung_weight[samsung_weight.notnull()]
            
            samsung_weight = samsung_weight[samsung_weight['CO_NM']=='삼성전자']['MARKET_CAP'].reset_index(drop=True) / np.sum(samsung_weight['MARKET_CAP']) # 삼성전자 시가총액 비중
            rest_weight = 1 - samsung_weight # 나머지 종목들의 시총비중
        
            #삼성전자를 시가총액 비중으로 투자, 나머지는 동일가중 투자    
            return_data.loc[0,n]=np.sum(result[result['CO_NM']!='삼성전자']['3M_RETURN']*rest_weight.iloc[0]/(len(result)-1))+(result[result['CO_NM']=='삼성전자']['3M_RETURN']*samsung_weight.loc[0]).reset_index(drop=True).loc[0] # 390이 삼성전자 index
            
            #여기도 삼성전자 시가총액, 나머지 동일가중으로 바꿔줘야함
            return_month_data[3*n] = np.sum(result[result['CO_NM']!='삼성전자']['1ST_RETURN']*rest_weight.iloc[0]/(len(result)-1))+(result[result['CO_NM']=='삼성전자']['1ST_RETURN']*samsung_weight.loc[0]).reset_index(drop=True).loc[0]
            return_month_data[3*n+1] = (np.sum(result[result['CO_NM']!='삼성전자']['2M_CUM_RETURN']*rest_weight.iloc[0]/(len(result)-1))+(result[result['CO_NM']=='삼성전자']['2M_CUM_RETURN']*samsung_weight.loc[0]).reset_index(drop=True).loc[0])/return_month_data[3*n].loc[0]  
            return_month_data[3*n+2] = (np.sum(result[result['CO_NM']!='삼성전자']['3M_RETURN']*rest_weight.iloc[0]/(len(result)-1))+(result[result['CO_NM']=='삼성전자']['3M_RETURN']*samsung_weight.loc[0]).reset_index(drop=True).loc[0])/(np.sum(result[result['CO_NM']!='삼성전자']['2M_CUM_RETURN']*rest_weight.iloc[0]/(len(result)-1))+(result[result['CO_NM']=='삼성전자']['2M_CUM_RETURN']*samsung_weight.loc[0]).reset_index(drop=True).loc[0])
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
                
        