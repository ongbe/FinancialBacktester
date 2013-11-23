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
import pytz
import matplotlib.pyplot as plt
import time

class DualMovingAverage(TradingAlgorithm):
    """Dual Moving Average Crossover algorithm.

    This algorithm buys apple once its short moving average crosses
    its long moving average (indicating upwards momentum) and sells
    its shares once the averages cross again (indicating downwards
    momentum).

    """
    
    
    def initialize(self,tickers,basket):
        
        # To keep track of whether we invested in the stock or not
        
        self.invested = False
        self.commission = PerTrade(0.00)
        #self.starting_cash(10000)
        self.set_slippage(FixedSlippage())
        self.capital_base = 10000
        self.tickers = tickers
        self.basket = basket
        self.quantity = 0
        
    def setQuantity(self,quantity):
        self.quantity = quantity
        
    def getQuantity(self):
        return self.quantity
    
    def handle_data(self, data):
        

        KLCI_PerChange = data['KLCI_PerChange'].price
        
        
        percent_changes = []    
        
        for ticker in tickers:
            
            percent_change = []
            
            if ticker == 'KLCI_Close':
                continue 
            
            key = ticker
            
            ticker = ticker.replace('Close','PerChange')           
            target = data[ticker].price
            
            if str(target) != 'nan':
            
                percent_change.append(key)
                percent_change.append(target)
                percent_changes.append(percent_change)

        
        #Look for the most minimum percentage change and invest
        
        temp = 0
        ticker_PerChange = 0.00
        ticker_price = 0.00
        for s in percent_changes:
            
            min = s[1]  
            if min < temp:
                temp = min 
                ticker_PerChange = s[0]
                ticker = s[0].replace('PerChange','Close')
                ticker_price = data[ticker].price
                
        buy = False
        sell = False

        if KLCI_PerChange < 0 and not self.invested:
            if ticker not in basket:
                
                if self.capital_base > 0 and target > 0:
                    basket.append(ticker)
                    q = ticker_price
                    w = data[ticker].price
                    self.quantity = self.capital_base/ data[ticker].price
                    self.order(ticker, self.quantity,stop_price=None,limit_price=None)
                    self.invested = True
                    buy = True
                    print "Buy " + ticker 
            
        elif self.invested:
            for ticker in tickers: 
                if ticker in basket:
                    ticker = ticker.replace('Close','PerChange')
                    ticker_PerChange = data[ticker].price                
                    #if ticker_PerChange > 0.01:
                    ticker = ticker.replace('PerChange','Close')
                    basket.remove(ticker)
                    quantity = self.getQuantity()
                    self.order(ticker, -quantity,stop_price=None,limit_price=None)
                    sell = True
                    self.invested = False
                    print "Sold " + ticker

    # Record state variables. A column for each
    # variable will be added to the performance
    # DataFrame returned by .run()
        self.record(buy=buy,
                    sell=sell)




if __name__ == '__main__':

    start = datetime(2013, 1, 2, 0, 0, 0, 0, pytz.utc)
    end = datetime(2013, 11, 14, 0, 0, 0, 0, pytz.utc)
    
    # Path for files
    h = os.getcwd()
    inputDir = h + '/Data/'
    
    KLSETickerfile = 'KLSETickers.txt'
    filename = 'Chen_KLCI_Main'
        
    filepath = inputDir + KLSETickerfile
    tickers = ut.readfile(filepath) 
    

    
    filepath = inputDir + filename + '.csv'
    ohlc = pd.read_csv(filepath,parse_dates=True,index_col=0)
    #ohlc=ohlc.tz_localize('UTC')
    
    data = pd.DataFrame(index=ohlc.index)
    
    for ticker in tickers:    
        data[ticker]=pd.DataFrame(ohlc[ticker])
        ticker = ticker.replace('_Close',"")        
        if ticker == 'KLCI':
            data[ticker + '_PerChange'] = ohlc[ticker + '_Close']/ohlc[ticker + '_Close'].shift(1)-1
            #data[ticker + '_PerChange'] = data[ticker + '_PerChange'].shift(1)
        else:
            data[ticker + '_PerChange'] = ohlc[ticker + '_Close']/ohlc[ticker + '_Close'].shift(1)-1
            #data[ticker + '_PerChange'] = data[ticker + '_PerChange'].shift(1)
        
    data=data.tz_localize('UTC')
    
    basket = []
    
    '''index = [br.date for br in trading.environment.benchmark_returns]
    rets = [br.returns for br in trading.environment.benchmark_returns]
    bm_returns = pd.Series(rets, index=index).ix[start:end]
    perf['benchmark_returns'] = (1 + bm_returns).cumprod().values
    perf[['algorithm_returns', 'benchmark_returns']].plot(ax=ax1,
                                                             sharex=True)
    '''
    
    
    dma = DualMovingAverage(tickers,basket)
    perf = dma.run(data)
    
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
    
    
    
    
    
    