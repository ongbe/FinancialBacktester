'''
Created on Nov 7, 2013

@author: Calvin
'''
'''Holding Template / Class'''

class Holdings(object):
        
    def __init__(self,capital,underlying,units,transactionprice,transactiontype,stoploss,atr):
        self.capital = capital
        self.underlying = underlying
        self.units = units
        self.transactionprice = transactionprice
        self.transactiontype = transactiontype
        self.stoploss = stoploss
        self.atr = atr
        
    def getCapital(self):
        
        return self.capital
    
    def setCapital(self,capital):
        
        self.capital = capital
    
    def getUnderlying(self):
        
        return self.underlying
    
    def setUnderlying(self,underlying):
        
        self.underlying = underlying
    
    def getUnits(self):
        
        return self.units
    
    def setUnits(self,units):
        
        self.units = units
    
    def getTransactionPrice(self):
        
        return self.transactionprice
    
    def setTransactionPrice(self,transactionprice):
        
        self.transactionprice = transactionprice
    
    def getTransactionType(self):
        
        return self.transactiontype
    
    def setStopLoss(self,stoploss):
        
        self.stoploss = stoploss
    
    def getStopLoss(self):
        
        return self.stoploss
           
    def setAtr(self,atr):
        self.atr = atr
    
    def getAtr(self):
        
        return self.atr

class Context(object):
    
    def __init__(self,Capital,Leverage_Capital,Equity_Value,Balance):
        self.capital = Capital
        self.leverage = Leverage_Capital
        self.equity_value = Equity_Value
        self.balance = Balance

    def getCapital(self):
        return self.capital
    
    def getLeverage(self):
        return self.leverage

    def getEquityValue(self):
        return self.equity_value
        
    def getBalance(self,Balance):
        return self.balance
    
    def setCapital(self,Capital):
        self.capital = Capital
        
    def setLeverageCapital(self,Leverage_Capital):
        self.leverage = Leverage_Capital
        
    def setEquityValue(self,Equity_Value):
        self.equity_value = Equity_Value
    
    def setBalance(self,Balance):
        self.balance = Balance

