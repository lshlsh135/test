# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 16:28:12 2017

@author: SH-NoteBook
"""
import pandas as pd
import numpy as np

def drawdown(R) :
    dd = pd.DataFrame(data = np.zeros(shape = (R.shape[0], R.shape[1])), index = R.index, columns = [R.columns])
    R[np.isnan(R)] = 0
    
    for j in range(0, R.shape[1]):
        
        if (R.iloc[0, j] > 0) :
            dd.iloc[0, j] = 0
        else :
            dd.iloc[0, j] = R.iloc[0, j]
            
        for i in range(1 , len(R)):
            temp_dd = (1+dd.iloc[i-1, j]) * (1+R.iloc[i, j]) -1
            if (temp_dd > 0) :
                dd.iloc[i, j] = 0
            else:
                dd.iloc[i, j] = temp_dd
    
    return(dd)