# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 10:59:38 2017

@author: SH-NoteBook
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 15:35:00 2017

@author: SH-NoteBook
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt




class return_calculator:
 
    def __init__(self,return_diff,return_month_data_costed,kospi_quarter,kospi_month):
        self.return_diff = return_diff
        self.return_month_data_costed = return_month_data_costed
        self.kospi_quarter = kospi_quarter
        self.col_num = len(kospi_month)
        self.kospi_month = pd.DataFrame(kospi_month).transpose().reset_index(drop=True)
        self.diff_12m_monthly = pd.DataFrame(np.zeros((1,self.col_num-11)))
        

        
    def rolling_12month_return_3factor(self,i,j,z):
        factor_name = [i,j,z]
        for i in range(self.col_num-11):
            self.diff_12m_monthly.iloc[0,i]=np.prod(self.return_month_data_costed.iloc[0,i:i+12])-np.prod(self.kospi_month.iloc[1,i:i+12])
        
        ir_20010228 = round(2*(np.mean(self.return_diff.iloc[0,:])-np.mean(self.kospi_quarter.transpose().iloc[1,:]))/np.std(self.return_diff.iloc[0,:]-self.kospi_quarter.transpose().iloc[1,:]),2)        
        ir_20080228 = round(2*(np.mean(self.return_diff.iloc[0,28:])-np.mean(self.kospi_quarter.transpose().iloc[1,28:]))/np.std(self.return_diff.iloc[0,28:]-self.kospi_quarter.transpose().iloc[1,28:]),2)        
        winrate_20080228=round((np.cumsum(self.diff_12m_monthly.iloc[0,84:]>0)/len(self.diff_12m_monthly.iloc[0,84:])).loc[len(self.diff_12m_monthly.columns)-1],3)
        winrate_20010228=round((np.cumsum(self.diff_12m_monthly.iloc[0,:]>0)/len(self.diff_12m_monthly.iloc[0,:])).loc[len(self.diff_12m_monthly.columns)-1],3)
        
        title_20010228 = ['ir_20010228='+str(ir_20010228), 'winrate_20010228='+str(winrate_20010228)  ]
        title_20080228 = ['ir_20080228='+str(ir_20080228), 'winrate_20080228='+str(winrate_20080228)  ]
        
        plt.figure(1)           
        plt.subplot(211)
        plt.plot(self.diff_12m_monthly.iloc[0,84:].transpose())   
        plt.grid(True)
        plt.suptitle(factor_name,fontsize=17,y=1.05)
        plt.tight_layout()
        plt.title(title_20080228)
        plt.subplot(212)
        plt.plot(self.diff_12m_monthly.transpose())    
        plt.grid(True)
        plt.title(title_20010228)
        plt.tight_layout()  # 아랫 그림의 제목과 윗 그림의 x축이 겹치는걸 방지해
        factor_name = ['ir_200102='+str(ir_20010228), 'ir_200802='+str(ir_20080228), 'win_200802='+str(winrate_20080228),'win_200102='+str(winrate_20010228)] # 파일 이름에 팩터를 넣지 않은 이유는 '/' 가 들어갈 수 없기 때문
        plt.savefig(str(factor_name)+'.jpg',bbox_inches = 'tight')  # bbox_inches 해야 모든 글자가 그림안에 표현됨
        return plt.show()
    
  
    