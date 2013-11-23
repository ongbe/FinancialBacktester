from __future__ import division
from zipline import TradingAlgorithm
from zipline.transforms import MovingAverage
from zipline.finance.commission import PerTrade
from zipline.utils.factory import load_from_yahoo
from datetime import datetime
from zipline.finance.slippage import FixedSlippage
from zipline.finance.performance import PerformancePeriod
from zipline.finance.risk import RiskReport
from math import *


import zipline.finance.trading as trading
import Lib.Utility as ut
import os
import pandas as pd
import numpy as np
import pytz
import matplotlib.pyplot as plt
import time

class GreedySmart(TradingAlgorithm):
    """Smart Greedy algorithm.

    This algorithm buys if current price is above current 
    moving average , shorts when current price is below 
    moving average
    """

    def initialize(self,basket,short_window=25):
        
        # To keep track of whether we invested in the stock or not 
        self.invested = False
        self.commission = PerTrade(0.00)
        #self.starting_cash(10000)
        self.set_slippage(FixedSlippage())
        self.capital_base = 10000
        self.basket = basket
        self.quantity = 0
        
    def setQuantity(self,quantity):
        self.quantity = quantity
        
    def getQuantity(self):
        return self.quantity
        
    def handle_data(self, ohlc):
        
        current_price = ohlc['Close'].price
        close_mavg = ohlc[str(lag) + '_MA_Close'].price
        atr_mavg = ohlc[str(lag) + '_MA_Atr'].price
        buy = False
        sell = False
        
        if current_price > close_mavg:
            self.quantity = self.capital_base/ ohlc['Close'].price
            self.order(current_price, self.quantity,stop_price=None,limit_price=None)
            self.invested = True
            buy = True
            print "Buy " + str(current_price) 
        elif self.invested:
            self.order(current_price, -self.quantity,stop_price=None,limit_price=None)
            self.invested = False
            print "Buy " + str(current_price)
            
            
    # Record state variables. A column for each
    # variable will be added to the performance
    # DataFrame returned by .run()
        self.record(buy=buy,
                    sell=sell)

def max_value(number1,number2):
        return max(number1,number2)

if __name__ == '__main__':
    
    # Path for files
    lag = 25
    h = os.getcwd()
    inputDir = h + '/Data/'
    filename = 'KLCI_Main' 
    filepath = inputDir + filename + '.csv'
    ohlc = pd.read_csv(filepath,parse_dates=True,index_col=0)
    
    ohlc['HL'] = abs(ohlc['High'].shift(2) - ohlc['Low'].shift(2))
    ohlc['HC'] = abs(ohlc['High'].shift(2) - ohlc['Close'].shift(1))
    ohlc['LC'] = abs(ohlc['Low'].shift(2) - ohlc['Close'].shift(1))

    
    iterate = 0
    count = len(ohlc.index)
    atr = []
    while iterate < count:
        atr.append(max_value(max_value(ohlc['HL'].ix[iterate],ohlc['LC'].ix[iterate]),ohlc['HC'].ix[iterate]))
        iterate +=1
    
    ohlc['Atr'] = pd.Series(atr,index=ohlc.index)
    
    del ohlc['HL']
    del ohlc['HC']
    del ohlc['LC'] 

    ohlc[str(lag) + '_MA_Close'] = pd.stats.moments.rolling_mean(ohlc['Close'],lag)
    ohlc[str(lag) + '_MA_Atr'] = pd.stats.moments.rolling_mean(ohlc['Atr'],lag)
    
    ohlc=ohlc.tz_localize('UTC')

    basket = [] 
    
    ohlc = ohlc.dropna()     
    dma = GreedySmart(basket)
    perf = dma.run(ohlc)
    
    bm = pd.DataFrame()
    perf['algorithm_returns'] = (1 + perf.returns).cumprod()
    
    # Plot results
    fig = plt.figure()
    ax1 = fig.add_subplot(311, ylabel='cumulative returns')
    #perf[['algorithm_returns', 'benchmark_returns']].plot(ax=ax1,sharex=True)
    perf['algorithm_returns'].plot(ax=ax1,sharex=True)
        
    ax2 = fig.add_subplot(312,  ylabel='Portfolio value in RM')
    perf.portfolio_value.plot(ax=ax2)
    ax2.plot(perf.ix[perf.buy].index, perf.portfolio_value[perf.buy],
             '^', markersize=10, color='m')
    ax2.plot(perf.ix[perf.sell].index, perf.portfolio_value[perf.sell],
             'v', markersize=10, color='k')
    
    sharpe = [risk['sharpe'] for risk in dma.risk_report['one_month']]
    print "Monthly Sharpe ratios:", sharpe
    
    plt.tight_layout()
    plt.legend(loc=0)
    plt.gcf().set_size_inches(18, 8)

    # Save Report and Figure
    outputname = time.strftime("%Y_%m_%d_%H_%M_%S")
    h = os.getcwd()
    
    outputDir = h + '/Output/'
    filename = outputDir + 'Report_' + outputname
    perf.to_csv(filename,sep='\t',encoding='utf-8')
    
    filename = outputDir + 'Figure_' + outputname
    plt.savefig(filename, dpi=400, bbox_inches='tight')
    
    
    
    
    
    