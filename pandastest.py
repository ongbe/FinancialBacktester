
from tradingWithPython import sharpe # general trading toolbox functions

import tradingWithPython.lib.yahooFinance as yf # yahoo finance functions
import pandas as pd # pandas time series library
import matplotlib.pyplot as plt
import os

'''The strategy rules are:
Yesterday must have been a down day of at least 0.25%.
If XLP opens down more than 0.1% today, go long and exit on the close.'''

def backtest(ohlc, ccThresh=-0.25, coThresh=-0.1):
    ''' Function to backtest the Boring Consumer Stocks strategy '''
    stratData = pd.DataFrame(index=ohlc.index)
    stratData['cc'] = 100*ohlc['Close'].pct_change() # close-to-close change in %
    stratData['co'] = 100*(ohlc['Open']/ohlc['Close'].shift(1)-1) # previous close to open change in %
    stratData['oc'] = 100*(ohlc['Close']/ohlc['Open']-1) # open to close change in %
    
    idx = (stratData['cc']<ccThresh).shift(1) & (stratData['co'] < coThresh) # find days that satisfy the strategy rules
    idx[0] = False # fill first entry with False (needed because .shift(1) adds a NaN in the first element)

    stratData['goLong'] = idx
    stratData['pnl'] = 0. # init pnl column with zeros (Watch out: if initialized with integer value (0), an error will pop later on)
    stratData['pnl'][idx] = stratData['oc'][idx] # set pnl column values to daily return wehere 'goLong' is true

    return stratData

def loadData(filename):
    
    #Load Sample data
    df = pd.read_csv(filename)
    return df


'''Plot Data'''
def plotGraph(stratData):

    fig = plt.figure(facecolor='white')
    
    plt.rc('axes', grid=True)
    plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)
    
    ax1 = fig.add_subplot(3,1,1)
    ax2 = fig.add_subplot(3,1,2)
    ax3 = fig.add_subplot(3,1,3)
        
    ax1.plot(stratData.index, stratData['cc'],label= 'CC')
    ax1.plot(stratData.index, stratData['co'],label= 'CO')
    ax1.plot(stratData.index, stratData['oc'],label= 'OC')
    
    ax2.plot(stratData.index, stratData['cc'].cumsum(),label= 'CC')
    ax2.plot(stratData.index, stratData['co'].cumsum(),label= 'CO')
    ax2.plot(stratData.index, stratData['oc'].cumsum(),label= 'OC')
    
    
    ax3.plot(stratData.index, stratData['pnl'].cumsum(), color='red',label= 'PnL')
    
    ax1.legend(loc='best',prop={'size':14})
    ax2.legend(loc='best',prop={'size':14})
    ax3.legend(loc='best',prop={'size':14})

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    
    #ohlc = yf.getHistoricData('XLP')[['open','high','low','close']] # get data from yahoo finance
    
    h = os.getcwd()
    inputDir = h + '/Input'
    inputfiles = os.listdir(inputDir)
    ohlc = pd.DataFrame()
    
    for file in inputfiles :
        
        if not '.csv' in file:
            continue
        
        filename = file
        
        #filename = filename.split('.')[0]
        
        file = inputDir + '/' + file
    
        
        ohlc = loadData(file)
        ohlc.tail()
        
        stratData = backtest(ohlc)
        pnl = stratData['pnl']
        plotGraph(stratData)
        print 'Sharpe:', sharpe(pnl)
    
    
    