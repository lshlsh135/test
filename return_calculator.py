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
        self.kospi_month = pd.DataFrame(kospi_month.iloc[12:,:]).transpose().reset_index(drop=True)
        self.diff_12m_monthly = pd.DataFrame(np.zeros((1,self.col_num-11)))
        
    
        
    def rolling_12month_return_3factor(self,i,j,z):
        self.factor_name = [i,j,z]
        for i in range(self.col_num-11):
            self.diff_12m_monthly.iloc[0,i]=np.prod(self.return_month_data_costed.iloc[0,i:i+12])-np.prod(self.kospi_month.iloc[1,i:i+12])
        
        ir_20020228 = round(2*(np.mean(self.return_diff.iloc[0,4:])-np.mean(self.kospi_quarter.transpose().iloc[1,4:]))/np.std(self.return_diff.iloc[0,:]-self.kospi_quarter.transpose().iloc[1,:]),2)        
        ir_20080228 = round(2*(np.mean(self.return_diff.iloc[0,28:])-np.mean(self.kospi_quarter.transpose().iloc[1,28:]))/np.std(self.return_diff.iloc[0,28:]-self.kospi_quarter.transpose().iloc[1,28:]),2)        
        winrate_20080228=round((np.cumsum(self.diff_12m_monthly.iloc[0,84:]>0)/len(self.diff_12m_monthly.iloc[0,84:])).loc[len(self.diff_12m_monthly.columns)-1],3)
        winrate_20020228=round((np.cumsum(self.diff_12m_monthly.iloc[0,:]>0)/len(self.diff_12m_monthly.iloc[0,:])).loc[len(self.diff_12m_monthly.columns)-1],3)
        
        title_20020228 = [self.factor_name, 'ir_20020228='+str(ir_20020228), 'winrate_20020228='+str(winrate_20020228)  ]
        title_20080228 = [self.factor_name, 'ir_20080228='+str(ir_20080228), 'winrate_20080228='+str(winrate_20080228)  ]
        
        plt.figure(1)           
        plt.subplot(211)
        plt.plot(self.diff_12m_monthly.iloc[0,84:].transpose())   
        plt.grid(True)
        plt.title(title_20080228)
        plt.subplot(212)
        plt.plot(self.diff_12m_monthly.transpose())    
        plt.grid(True)
        plt.title(title_20020228)
        plt.tight_layout()  # 아랫 그림의 제목과 윗 그림의 x축이 겹치는걸 방지해
        self.factor_name = [self.factor_name, 'ir_20020228='+str(ir_20020228), 'ir_20080228='+str(ir_20080228), 'winrate_20080228='+str(winrate_20080228),'winrate_20020228='+str(winrate_20020228)]
        plt.savefig(str(self.factor_name)+'.jpg')
        return plt.show()
    
    
    
    
    def rolling_12month_return_4factor(self,i,j,z,p):
        self.factor_name = [i,j,z,p]
        for i in range(self.col_num-11):
            self.diff_12m_monthly.iloc[0,i]=np.prod(self.return_month_data_costed.iloc[0,i:i+12])-np.prod(self.kospi_month.iloc[1,i:i+12])
        
        ir_20020228 = round(2*(np.mean(self.return_diff.iloc[0,4:])-np.mean(self.kospi_quarter.transpose().iloc[1,4:]))/np.std(self.return_diff.iloc[0,:]-self.kospi_quarter.transpose().iloc[1,:]),2)        
        ir_20080228 = round(2*(np.mean(self.return_diff.iloc[0,28:])-np.mean(self.kospi_quarter.transpose().iloc[1,28:]))/np.std(self.return_diff.iloc[0,28:]-self.kospi_quarter.transpose().iloc[1,28:]),2)        
        winrate_20080228=round((np.cumsum(self.diff_12m_monthly.iloc[0,84:]>0)/len(self.diff_12m_monthly.iloc[0,84:])).loc[len(self.diff_12m_monthly.columns)-1],3)
        winrate_20020228=round((np.cumsum(self.diff_12m_monthly.iloc[0,:]>0)/len(self.diff_12m_monthly.iloc[0,:])).loc[len(self.diff_12m_monthly.columns)-1],3)
        
        title_20020228 = [self.factor_name, 'ir_20020228='+str(ir_20020228), 'winrate_20020228='+str(winrate_20020228)  ]
        title_20080228 = [self.factor_name, 'ir_20080228='+str(ir_20080228), 'winrate_20080228='+str(winrate_20080228)  ]
        
        plt.figure(1)           
        plt.subplot(211)
        plt.plot(self.diff_12m_monthly.iloc[0,84:].transpose())   
        plt.grid(True)
        plt.title(title_20080228)
        plt.subplot(212)
        plt.plot(self.diff_12m_monthly.transpose())    
        plt.grid(True)
        plt.title(title_20020228)
        plt.tight_layout()  # 아랫 그림의 제목과 윗 그림의 x축이 겹치는걸 방지해
        self.factor_name = [self.factor_name, 'ir_20020228='+str(ir_20020228), 'ir_20080228='+str(ir_20080228), 'winrate_20080228='+str(winrate_20080228),'winrate_20020228='+str(winrate_20020228)]
        plt.savefig(str(self.factor_name)+'.jpg')
        return plt.show()
        