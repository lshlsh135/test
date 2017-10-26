# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 10:53:12 2017

29개의 wics 섹터 중에서 1년 - 1개월 누적수익률 상위 15섹터를 고른 후에, 
그 섹터에 포함되는 종목중에서 factor들의 outlier들을 winsorize 해주고
섹터별로 z_score을 구한다음 +-3 보정해준다.

@author: SH-NoteBook
"""


import numpy as np
import pandas as pd
class factor_3_mid_adoutlier2:
 
    def __init__(self,raw_data,rebalancing_date,month_date,wics_mid,col_num,col_num2,col_num3):
        self.raw_data = raw_data
        self.rebalancing_date = rebalancing_date
        self.month_date = month_date
        self.col_num = '1/pbr'
        self.col_num2 = '1/per'
        self.col_num3 = 'div_yield'
        self.col_loc = [col_num,col_num2,col_num3]
        self.z_col_loc = ['z_'+col_num,'z_'+col_num2,'z_'+col_num3]
        self.wics_mid = wics_mid
       
        

    def factor_3_mid_adoutlier2(self):
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
        
        for n in range(col_length): 
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

            for i in self.z_col_loc:                  
                locals()['data_{}'.format(0)].loc[locals()['data_{}'.format(0)][i]>3,i] = 3 # df.loc[selection criteria,column i want] = value
                locals()['data_{}'.format(0)].loc[locals()['data_{}'.format(0)][i]<-3,i] = -3
                
            locals()['data_{}'.format(0)] = locals()['data_{}'.format(0)].assign(z_score=np.nanmean(locals()['data_{}'.format(0)].loc[:,self.z_col_loc],axis=1))
            
            
            result = locals()['data_{}'.format(0)]
            result=result.assign(rnk=result['z_score'].rank(method='first',ascending=False)) 
            
            for i in self.col_loc:
                samsung[i]=0
                samsung['z_score'] = 0
                samsung['rnk'] = 0                                       
            

            result.drop('CO_NM_y', axis=1, inplace=True)
            samsung.drop('CO_NM_y', axis=1, inplace=True)
            
            
            result = pd.concat([result,samsung],axis=0)
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
            
            first_data = self.raw_data[self.raw_data['TRD_DATE']==self.rebalancing_date.iloc[n,0]]
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
#        turnover_quarter[4]=1
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
        for n in range(col_length):
            return_month_data_costed[3*n] = np.subtract(return_month_data[3*n],turnover_quarter[n])
        
            
            
#               
        
            
        return [return_final, return_diff, return_month_data_costed, data_name]  # 이렇게 return 하면 list로 받아짐
                
        