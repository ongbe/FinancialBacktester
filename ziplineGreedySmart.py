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

    def initialize(self,basket):
        
        # To keep track of whether we invested in the stock or not 
        self.invested = False
        self.commission = PerTrade(0.00)
        #self.starting_cash(10000)
        self.set_slippage(FixedSlippage())
        self.capital_base = 10000
        self.risk_capital = 0.03
        self.basket = basket
        self.quantity_short = 0
        self.quantity_long = 0
        self.stoploss_short = 0
        self.stoploss_long = 0
        
        
    def setQuantity_short(self,quantity):
        self.quantity_short = quantity
        
    def getQuantity_short(self):
        return self.quantity_short
     
    def setQuantity_long(self,quantity):
        self.quantity_long = quantity
        
    def getQuantity_long(self):
        return self.quantity_long
    
    def getQuantity(self):
        return self.quantity
        
    def setStopLoss_short(self,stoploss):
        self.stoploss_short = stoploss
        
    def getStopLoss_short(self):
        return self.stoploss_short
    
    def setStopLoss_long(self,stoploss):
        self.stoploss_long = stoploss
        
    def getStopLoss_long(self):
        return self.stoploss_long
    
    def handle_data(self, ohlc):
        
        current_price = ohlc['Open'].price
        close_mavg = ohlc[str(lag) + '_MA_Close'].price
        atr_mavg = ohlc[str(lag) + '_MA_Atr'].price
        buy = False
        sell = False
        
        print "Current price" + str(current_price) + " Current MAVG " + str(close_mavg)
                 
        if not "Long" in basket:
            if current_price > close_mavg:
                basket.append("Long")
                self.stoploss_long = current_price - atr_mavg
                self.quantity_long = self._portfolio.portfolio_value * self.risk_capital/ atr_mavg
                self.order('KLCI', self.quantity_long,stop_price=None,limit_price=None)
                buy = True
                print "Long " + str(current_price)                
                self.record(buy=buy,
                            sell=sell) 
                return
        
        if not "Short" in basket:
            if current_price < close_mavg:
                basket.append("Short")
                self.stoploss_short = current_price + atr_mavg
                self.quantity_short = self._portfolio.portfolio_value * self.risk_capital/ atr_mavg
                self.order('KLCI', self.quantity_short,stop_price=None,limit_price=None)
                sell = True
                print "Short " + str(current_price)    
                self.record(buy=buy,
                            sell=sell)             
                return
                   
        if "Long" in basket:
            # exit position if current price below stop loss
            if current_price < self.stoploss_long:
                basket.remove("Long")
                qlong = self.getQuantity_long()
                self.order('KLCI', qlong,stop_price=None,limit_price=None)
                sell = True
                print "Close Long Position " + str(current_price)    
                          
                
            
        if "Short" in basket:
            # exit position if current price above stop loss
            if current_price > self.stoploss_long:
                basket.remove("Short")
                qshort = self.getQuantity_short()
                self.order('KLCI', qshort,stop_price=None,limit_price=None)
                buy = True
                print "Close Short Position " + str(current_price)    
             
                        
    
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
    
    ohlc[str(lag) + '_MA_Close'] = ohlc[str(lag) + '_MA_Close'].shift(1)
    ohlc[str(lag) + '_MA_Atr'] = ohlc[str(lag) + '_MA_Atr'].shift(1)
    ohlc['KLCI'] = ohlc['Open'].shift(1)
        
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
    
    ax3 = fig.add_subplot(313,  ylabel='KLCI')
    ohlc[['KLCI',str(lag) + '_MA_Close']].plot(ax=ax3,sharex=True)
    
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
    
    print "Backtest Complete"
    
    
    
    
    