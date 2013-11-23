'''
Created on Nov 22, 2013

@author: CLYG
@Title : Correlation Script
'''

import Lib.Utility as ut
import os
import pandas as pd
import pytz
import matplotlib.pyplot as plt
import time
import numpy as np


if __name__ == '__main__':
 
    # Path for files
    ''''h = os.getcwd()
    inputDir = h + '/Data/'
    
    tickerfile = 'Kospi200Tickers.txt'
    filename = 'Kospi200HistoricalLast'
        
    filepath = inputDir + tickerfile
    tickers = ut.readfile(filepath)     
    filepath = inputDir + filename + '.csv'
    ohlc = pd.read_csv(filepath,parse_dates=True,index_col=0)
    #ohlc=ohlc.tz_localize('UTC')
    
    index_futures = ohlc['KM1 COMB Index']
    del ohlc['KM1 COMB Index']
    componets_rets = ohlc.pct_change()
    index_futures_rets = index_futures.pct_change()
    
    corr =  componets_rets.corr()
    print corr

    plt.imshow(corr, cmap='hot', interpolation='none')
    plt.colorbar()
    plt.xticks(range(len(corr)), corr.columns)
    plt.yticks(range(len(corr)), corr.columns);

    plt.show()'''
    
    df = pd.DataFrame({'APPL' : [40,10,30], 'GOOG' : [50,20,40]},index=[1,2,3])
    s = pd.Series([0.6,0.4],index=['APPL','GOOG'])
    index_closing = pd.Series([100,200],index=['APPL','GOOG'])
    
    print df
    print '\n'
    print s
    print '\n'
    print index_closing
    print '\n'
    mv = pd.DataFrame(df.dot(s),columns=['Market_Value'])
    mv_change = mv / mv.shift(1)
    print mv
    print '\n'
    print mv_change
    print '\n'
    print mv_change[1:]
    print '\n'
    my_index = mv_change[1:].dot(index_closing.transpose())
    print my_index
    
    
    