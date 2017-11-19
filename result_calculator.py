# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 16:41:39 2017

@author: SH-NoteBook
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 09:04:01 2017


n_w : net_wealth
port_g_rtn_d : daily_gross_return of wealth
kospi_day : kospi jisu daily gross return


@author: SH-NoteBook
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from drawdown import drawdown

class result_calculator:
 
    def __init__(self,n_w,kospi_day):
        self.n_w = n_w # 일별 net_wealth
        
        self.kospi_day = kospi_day # 일별 종가 (위에서도 net_wealth를 받아왔기 때문에 계산이 편하다.)

    def rolling_12month_return_3factor(self,i,j,z):
        factor_name = [i,j,z]
        
        datetime=pd.DataFrame(pd.to_datetime(self.n_w.index)) # 월말 날짜를 뽑기위해 datetime으로 바꿔줌
        self.n_w = pd.DataFrame(self.n_w, index = datetime[0]) # n_w의 index를 python의 date type로 바꿔줌
        n_w_m= self.n_w.resample("M",how="max") # 월말 net_wealth만 저장
        n_w_3m= self.n_w.resample("3M",how="max") # 분기별 net_wealth 저장
        port_g_rtn_d = self.n_w.pct_change(1)
        port_g_rtn_3m = n_w_3m.pct_change(1) # 분기별 수익률
        port_g_rtn_12m = n_w_m.pct_change(12) # 12개월 롤링 누적 수익률 : rollint_return
        port_g_rtn_3m_2008 = port_g_rtn_3m[port_g_rtn_3m.index>'2008-02-29']
        
        
        datetime_kospi=pd.DataFrame(pd.to_datetime(self.kospi_day.index))
        self.kospi_day = pd.DataFrame(self.kospi_day['PRC'], index = datetime_kospi['TRD_DATE'])
        self.kospi_day = self.kospi_day[(self.kospi_day.index>=self.n_w.index[0])&(self.kospi_day.index<=self.n_w.index[-1])] # 벤치마크의 prc를 포트폴리오의 투자기간과 맞춤
        kospi_day_m= self.kospi_day.resample("M",how="max") # 코스피 지수의 월말 지수
        kospi_g_rtn_d = self.kospi_day.pct_change(1) # 코스피 일별 gross return
        kospi_g_rtn_12m = kospi_day_m.pct_change(12) # 12개월 롤링 누적 수익률 : rollint_return
        kospi_day_3m= self.kospi_day.resample("3M",how="max") # 분기별 net_wealth 저장
        kospi_g_rtn_3m = kospi_day_3m.pct_change(1)
        kospi_g_rtn_3m_2008 = kospi_g_rtn_3m[kospi_g_rtn_3m.index>'2008-02-29']        
        
        
        
        diff_rtn_d_2002 = port_g_rtn_d[0] - kospi_g_rtn_d['PRC'] # 일별 초과수익률
        winrate_20020228_d = round(diff_rtn_d_2002[diff_rtn_d_2002>0].count()/len(diff_rtn_d_2002),2) # 일별 초과수익률의 승률
        
        diff_rtn_d_2008 = diff_rtn_d_2002[diff_rtn_d_2002.index>'2008-02-29']
        winrate_20080229_d = round(diff_rtn_d_2008[diff_rtn_d_2008>0].count()/len(diff_rtn_d_2008),2) # 일별 초과수익률의 승률
        
        diff_rtn_12m_2002 = port_g_rtn_12m[0] - kospi_g_rtn_12m['PRC']
        diff_rtn_12m_2008 = diff_rtn_12m_2002[diff_rtn_12m_2002.index>'2008-02-29']
        
        winrate_20020228 = round(diff_rtn_12m_2002[diff_rtn_12m_2002>0].count()/len(diff_rtn_12m_2002),2)
        winrate_20080229 = round(diff_rtn_12m_2008[diff_rtn_12m_2008>0].count()/len(diff_rtn_12m_2008),2)
        
        ir_20020228 = round(2*(np.mean(port_g_rtn_3m)[0]-np.mean(kospi_g_rtn_3m)['PRC'])/np.std(port_g_rtn_3m[0]-kospi_g_rtn_3m['PRC']),2)        
        ir_20080229 = round(2*(np.mean(port_g_rtn_3m_2008)[0]-np.mean(kospi_g_rtn_3m_2008)['PRC'])/np.std(port_g_rtn_3m_2008[0]-kospi_g_rtn_3m_2008['PRC']),2)        
        
        
        title_20020228 = ['ir_20020228='+str(ir_20020228), 'winrate_20020228='+str(winrate_20020228)  ]
        title_20080229 = ['ir_20080229='+str(ir_20080229), 'winrate_20080229='+str(winrate_20080229)  ]
             
        
        dd_port = drawdown(pd.DataFrame(port_g_rtn_d))
        mdd_port = dd_port.min() # Maximum drawdown
        dd_kospi = drawdown(pd.DataFrame(kospi_g_rtn_d))
        mdd_kospi = dd_kospi.min() # Maximum drawdown
        dd_p_k = drawdown(pd.DataFrame(port_g_rtn_d[0]-kospi_g_rtn_d['PRC']))
        mdd_p_k = dd_p_k.min()
        
        plt.figure(figsize=(12,4))           
        plt.subplot(221)
        plt.plot(diff_rtn_12m_2002)   
        plt.grid(True)
        plt.suptitle(factor_name,fontsize=17,y=1.05)
        plt.tight_layout()
        plt.title(title_20020228)
        plt.subplot(223)
        plt.plot(diff_rtn_12m_2008)    
        plt.grid(True)
        plt.title(title_20080229)
        plt.tight_layout()  # 아랫 그림의 제목과 윗 그림의 x축이 겹치는걸 방지해
        plt.subplot(222)
        plt.plot(dd_port)
        plt.grid(True)
        plt.title(['mdd_port='+str(round(np.float64(mdd_port),2)), 'mdd_port='+str(round(np.float64(mdd_kospi),2))])
        plt.tight_layout()
        plt.subplot(224)
        plt.plot(dd_p_k)
        plt.grid(True)
        plt.title(['mdd_port-kospi='+str(round(np.float64(mdd_p_k),2))])
        plt.tight_layout()
        factor_name = ['ir_200102='+str(ir_20020228), 'ir_200802='+str(ir_20080229), 'win_200802='+str(winrate_20080229),'win_200102='+str(winrate_20020228)] # 파일 이름에 팩터를 넣지 않은 이유는 '/' 가 들어갈 수 없기 때문
        plt.savefig(str(factor_name)+'.jpg',bbox_inches = 'tight')  # bbox_inches 해야 모든 글자가 그림안에 표현됨
        return plt.show()
    
  
    