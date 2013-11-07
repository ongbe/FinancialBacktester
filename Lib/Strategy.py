'''
Created on Nov 7, 2013

@author: Calvin
'''
from __future__ import division
from math import * 
from Portfolio import *
from Utility import * 

import pandas as pd
import time
import matplotlib.pyplot as plt
import os



capital_list = []
currency_list = []
unit_list = []
transaction_type_list = []
transaction_price_list = []
stop_loss_list = []
atr_list = []

columns_header = ['Capital','Currency','Units','Enter Price','Transaction Type','Stop Loss','Current Atr']

hold_record = {'Capital':capital_list, 'Currency':currency_list, 'Units':unit_list,  'Enter Price' : transaction_price_list,
           'Transaction Type': transaction_type_list, 'Stop Loss' : stop_loss_list, 'Current Atr' : atr_list
           }

def backtest(df,lagInput):
    
    #Reset
    df.convert_objects(convert_numeric=True).dtypes
    lag = lagInput

    #Exit Strategy
    # 3 ranges for next move
    # Range comes from data 2 days from now
    # High - Low, Abs(High - Close), Abs(Low - Close)
    count = len(df.index)
    range_low = df['Low'][0:count]
    range_high = df['High'][0:count]
    range_close = df['Close'][0:count]
    range_high_low = range_high.shift(2) - range_low.shift(2)
    range_high_close = abs(range_high.shift(2) - range_close.shift(1))
    range_low_close = abs(range_low.shift(2) - range_close.shift(1))


    # Select the max range from the 3 choices and add to dataframe
    atr = []
    iterate = 0
    while iterate < count:
        trading_band = max_range(range_high_low.iloc[iterate],
                               range_high_close.iloc[iterate],
                               range_low_close.iloc[iterate])
        atr.append(trading_band * 1)
        iterate = iterate + 1
    
    df['ATR'] = atr
    df[str(lag) + '_MA_Close'] = pd.stats.moments.rolling_mean(df['Close'],lag)
    df[str(lag) + '_MA_ATR'] = pd.stats.moments.rolling_mean(df['ATR'],lag)

    
    # Risk Capital (Risk Management Monitoring)
    # Eg: Capital is RM 1,000,000 . Bet 3% - 5%
    # 3% * 1,000,000 = RM 30,000
    # if leverage is 10 times, cushion is RM 300,000
    # if mark to market reaches 700,000 , cut loss

    iterate = lag + 2
    number_of_trades = 0
    number_of_winning_trades = 0
    number_of_lossing_trades = 0
    action_signal =""
    
    Leverage_Multiplier = 10
    
    Capital = 100000
    Leverage_Capital  =  Capital * Leverage_Multiplier
    Equity_Value = 0
    Balance = 0
    
    Enter_price = 0
    Notional_Amount = 0
    Number_of_units = 0
    Stop_Loss = 0
    Take_Profit = 0
    Risk_Capital = 0.03
    Bet_Value = 0
    PnL = 0
    PnL_List = []
    
    max_notianal_long = 3000000
    max_notianal_short = 3000000
   
    #total_PnL = {}
    
    currency = str(df['Currency'][0])
    currency = currency.replace('/', '_')
    filename = currency + "_" + str(lag) + "_output_"  + time.strftime("%d_%m_%Y") + ".txt"
        
    while iterate < count:
        
        #Get previous day signal to enter 
        iterate -= 1
        current_price = df['Close'][iterate]
        current_MA_Close = round(df[str(lag) +'_MA_Close'][iterate],4)
        current_atr = round(df[str(lag) + '_MA_ATR'][iterate],4)
    
        action_signal = check_signal(current_price,current_MA_Close)   
        iterate += 1
          
        if action_signal == "":
            iterate += 1
            continue    
                    
        if Capital < 0:
            break   
    
        if current_atr == 0 :
            iterate += 1
            continue
            
        # Enter At Next Day Price,    
        current_price = df['Close'][iterate]
        current_MA_Close = round(df[str(lag) +'_MA_Close'][iterate],4)
        current_atr = round(df[str(lag) + '_MA_ATR'][iterate],4)
        
        Bet = Capital * Risk_Capital
        #Balance = Capital - Bet 
        Enter_price = round(df['Close'][iterate],4)
        Number_of_Units = round(Bet / current_atr,0)
        Notional_Amount = df['Close'][iterate] * Number_of_Units  
              
        if action_signal == "BUY":   

            Stop_Loss =  current_price - current_atr
                              
        if action_signal == "SELL":
    
            Stop_Loss =  current_price + current_atr
        
        #data = dataStr(action_signal,iterate,Enter_price,lag,current_MA_Close,Capital,current_atr)
               
        #savefile(filename,data)       
                       
        hold_record_df = pd.DataFrame(hold_record, columns = columns_header)
        hold_record_df = hold_record_df.reset_index(drop = True) 
        check_count = len(hold_record_df.index)
                
        if(check_count < 2):
            #Current Action to Take 
            hold = Holdings(Capital,currency,Number_of_Units,Enter_price,action_signal,Stop_Loss,current_atr)    
            
            if (check_count == 0):                   
                
                notional_value = Number_of_Units * Enter_price
                
                #Action signal indicate SELL, THEN SELL
                if (action_signal == "SELL" and notional_value <= max_notianal_short):
                    #if record has NO SELL ,Short a new position                
                    
                    order(hold)
                    hold_record_df = pd.DataFrame(hold_record, columns = columns_header)
                    
                    
                    data = dataStr(action_signal,iterate,Enter_price,lag,current_MA_Close,Capital,current_atr)
                    
                    savefile(filename,data)
                    
                    Capital = Capital - ((Number_of_Units*Enter_price)/Leverage_Multiplier)
                    Leverage_Capital  = Capital * Leverage_Multiplier
                    Equity_Value = Equity_Value + (Number_of_Units*Enter_price)
                    #Balance = Leverage_Capital - Equity_Value
                    
                             
                #Action signal indicate BUY, THEN BUY
                if (action_signal == "BUY" and notional_value <= max_notianal_long):
                    #if record has NO BUY,Buy a new position

                    order(hold)
                    hold_record_df = pd.DataFrame(hold_record, columns = columns_header)
            
                    data = dataStr(action_signal,iterate,Enter_price,lag,current_MA_Close,Capital,current_atr)
                    
                    savefile(filename,data)
                    
                    Capital = Capital - ((Number_of_Units*Enter_price)/Leverage_Multiplier)
                    Leverage_Capital = Capital * Leverage_Multiplier
                    Equity_Value = Equity_Value + (Number_of_Units*Enter_price)
                    
                                  
            if (check_count == 1):
                
                #retrieve existing record and check the previous transacton
                # if previous transaction is SELL and Action Signal is BUY, Enter BUY
                # if previosu transcation is BUY and Action Signal is SELL, Enter SELL
                previous_transaction = hold_record_df['Transaction Type'][0]
                
                notional_value = Number_of_Units * Enter_price
                
                if(previous_transaction == "SELL" and action_signal == "BUY" and notional_value <= max_notianal_long):

                    order(hold)                
                    hold_record_df = pd.DataFrame(hold_record, columns = columns_header)
                    
                    data = dataStr(action_signal,iterate,Enter_price,lag,current_MA_Close,Capital,current_atr)
                    
                    savefile(filename,data)
                    
                    Capital = Capital - ((Number_of_Units*Enter_price)/Leverage_Multiplier)
                    Leverage_Capital  = Capital * Leverage_Multiplier
                    Equity_Value = Equity_Value + (Number_of_Units*Enter_price)
                    
                if(previous_transaction == "BUY" and action_signal == "SELL" and notional_value <= max_notianal_short):
                    
                    order(hold)                    
                    hold_record_df = pd.DataFrame(hold_record, columns = columns_header)
                    
                    data = dataStr(action_signal,iterate,Enter_price,lag,current_MA_Close,Capital,current_atr)
                           
                    savefile(filename,data)
                    
                    Capital = Capital - ((Number_of_Units*Enter_price)/Leverage_Multiplier)
                    Leverage_Capital  = Capital * Leverage_Multiplier
                    Equity_Value = Equity_Value + (Number_of_Units*Enter_price)
        
                inner_rec = 0
                #Update Record
                hold_temp = Holdings(hold_record_df.ix[inner_rec]['Capital'],hold_record_df.ix[inner_rec]['Currency'],\
                                     hold_record_df.ix[inner_rec]['Units'],hold_record_df.ix[inner_rec]['Enter Price'],\
                                     hold_record_df.ix[inner_rec]['Transaction Type'],hold_record_df.ix[inner_rec]['Stop Loss'],\
                                     hold_record_df.ix[inner_rec]['Current Atr'])
                
                rec_tt = hold_temp.getTransactionType()
                if (previous_transaction == "SELL"):                    
                    #Update or Exit Current Position        
                    if (current_price > hold_temp.getStopLoss()):
                                
                        Notional_Amount = current_price * hold_temp.getUnits()                 
                        PnL = (hold_temp.getTransactionPrice() - current_price) * hold_temp.getUnits()
                        PnL_List.append(PnL)
                        Capital = Capital + PnL
                        
                        if (PnL > 0):
                            number_of_winning_trades += 1
                            number_of_trades = number_of_lossing_trades + number_of_winning_trades
                        else:
                            number_of_lossing_trades += 1
                            number_of_trades = number_of_lossing_trades + number_of_winning_trades
                        
                        data = "Exit"
                        savefile(filename,data)
                        
                        data = hold_record_df
                        savefile(filename,data)
                        
                        remove_record(inner_rec)
                        hold_record_df = hold_record_df.drop([inner_rec])
                        hold_record_df = pd.DataFrame(hold_record, columns = columns_header)
                                           
                    else:
                        #Main Stop Loss, and quantity, closing partial position  
                        spread = hold_temp.getUnits() * hold_temp.getAtr()
                        quantity = round(spread / current_atr,0)
                        
                        # Current ATR Greater than Holding ATR, reduce current holdings                                         
                        if(current_atr > hold_temp.getAtr()):                        
                         
                            #Notional_Amount = current_price * hold_temp.getUnits()                 
                            PnL = (hold_temp.getTransactionPrice() - current_price) * (hold_temp.getUnits() - quantity)
                            PnL_List.append(PnL)
                            Capital = Capital + PnL
                        
                            #hold_temp.setStopLoss(current_price + current_atr)           
                            #hold_temp.setAtr(current_atr)
                            hold_temp.setUnits(quantity)
                            
                            #stop_loss_list[inner_rec] = hold_temp.getStopLoss()
                            #atr_list[inner_rec] = hold_temp.getAtr()
                            unit_list[inner_rec] = hold_temp.getUnits()
                        
                            if (PnL > 0):
                                number_of_winning_trades += 1
                                number_of_trades = number_of_lossing_trades + number_of_winning_trades
                            else:
                                number_of_lossing_trades += 1
                                number_of_trades = number_of_lossing_trades + number_of_winning_trades
    
                            
                            hold_record_df = pd.DataFrame(hold_record, columns = columns_header)
                        
                        else:
                        
                            #Reset Stop Loss
                            hold_temp.setStopLoss(current_price + current_atr)           
                            hold_temp.setAtr(current_atr)
                             
                            stop_loss_list[inner_rec] = hold_temp.getStopLoss()
                            atr_list[inner_rec] = hold_temp.getAtr()
                                                   
                            hold_record_df = pd.DataFrame(hold_record, columns = columns_header)
                            
                            
                            data = "Reset Stop Loss and Close Partial Position"
                            savefile(filename,data)
                            
                            data = hold_record_df
                            savefile(filename,data)
                                        
                if (previous_transaction == "BUY"):
                    if (current_price < hold_temp.getStopLoss()):
                                
                        Notional_Amount = current_price * hold_temp.getUnits()                 
                        PnL = (current_price - hold_temp.getTransactionPrice()) * hold_temp.getUnits()
                        PnL_List.append(PnL)
                        Capital = Capital + PnL
                        
                        if (PnL > 0):
                            number_of_winning_trades += 1
                            number_of_trades = number_of_lossing_trades + number_of_winning_trades
                        else:
                            number_of_lossing_trades += 1
                            number_of_trades = number_of_lossing_trades + number_of_winning_trades
                    
                        
                        data = "Exit"
                        savefile(filename,data)
                        
                        data = hold_record_df
                        savefile(filename,data)
                        

                        remove_record(inner_rec)
                        hold_record_df = hold_record_df.drop([inner_rec])
                        hold_record_df = pd.DataFrame(hold_record, columns = columns_header)
                        
                    else:
                        #Main Stop Loss, and quantity, closing partial position  
                        spread = hold_temp.getUnits() * hold_temp.getAtr()
                        quantity = round(spread / current_atr,0)
                        
                        # Current ATR Greater than Holding ATR, reduce current holdings                                         
                        if(current_atr > hold_temp.getAtr()):                        
                        
                            #Notional_Amount = current_price * hold_temp.getUnits()                 
                            PnL = (current_price - hold_temp.getTransactionPrice()) * (hold_temp.getUnits() - quantity)
                            PnL_List.append(PnL)
                            Capital = Capital + PnL
                            
                            #hold_temp.setStopLoss(current_price + current_atr)           
                            hold_temp.setAtr(current_atr)
                            hold_temp.setUnits(quantity)
                            
                            #stop_loss_list[inner_rec] = hold_temp.getStopLoss()
                            atr_list[inner_rec] = hold_temp.getAtr()
                            unit_list[inner_rec] = hold_temp.getUnits()
                        
                            if (PnL > 0):
                                number_of_winning_trades += 1
                                number_of_trades = number_of_lossing_trades + number_of_winning_trades
                            else:
                                number_of_lossing_trades += 1
                                number_of_trades = number_of_lossing_trades + number_of_winning_trades 
                                
                                hold_record_df = pd.DataFrame(hold_record, columns = columns_header)    
                        
                        else:
                        #Reset Stop Loss
                            hold_temp.setStopLoss(current_price - current_atr) 
                            hold_temp.setAtr(current_atr)
                            
                            stop_loss_list[inner_rec] = hold_temp.getStopLoss()
                            atr_list[inner_rec] = hold_temp.getAtr()
                            
                            hold_record_df = pd.DataFrame(hold_record, columns = columns_header)
                            
                            
                            data = "Reset Stop Loss"
                            savefile(filename,data)
                            
                            data = hold_record_df
                            savefile(filename,data) 
                             
                                                            
        inner_rec = 0            
        #Tf there is position, update or close   
        if (check_count == 2):
            while inner_rec < check_count:
                             
                hold_temp = Holdings(hold_record_df.ix[inner_rec]['Capital'],hold_record_df.ix[inner_rec]['Currency'],\
                                     hold_record_df.ix[inner_rec]['Units'],hold_record_df.ix[inner_rec]['Enter Price'],\
                                     hold_record_df.ix[inner_rec]['Transaction Type'],hold_record_df.ix[inner_rec]['Stop Loss'],\
                                     hold_record_df.ix[inner_rec]['Current Atr'])
                
                rec_tt = hold_temp.getTransactionType()
                previous_transaction = hold_temp.getTransactionType()
                
                if (previous_transaction == "SELL"): 
                
                    if (current_price > hold_temp.getStopLoss()):
                                
                        Notional_Amount = current_price * hold_temp.getUnits()                 
                        PnL = (hold_temp.getTransactionPrice() - current_price) * hold_temp.getUnits()
                        PnL_List.append(PnL)
                        Capital = Capital + PnL
                        
                        if (PnL > 0):
                            number_of_winning_trades += 1
                            number_of_trades = number_of_lossing_trades + number_of_winning_trades
                        else:
                            number_of_lossing_trades += 1
                            number_of_trades = number_of_lossing_trades + number_of_winning_trades
                        
                        data = "Exit"
                        savefile(filename,data)
                        
                        data = hold_record_df
                        savefile(filename,data)
                        
                        remove_record(inner_rec)
                        hold_record_df = hold_record_df.drop([inner_rec])
                        hold_record_df = pd.DataFrame(hold_record, columns = columns_header)
                        check_count = len(hold_record_df.index)
                        
                        
                        continue
                        
                    else:
                        
                        #Main Stop Loss, and quantity, closing partial position  
                        spread = hold_temp.getUnits() * hold_temp.getAtr()
                        quantity = round(spread / current_atr,0)

                        # Current ATR Greater than Holding ATR, reduce current holdings                                         
                        if(current_atr > hold_temp.getAtr()):                        
                             
                            #Notional_Amount = current_price * hold_temp.getUnits()                 
                            PnL = (hold_temp.getTransactionPrice() - current_price) * (hold_temp.getUnits() - quantity)
                            PnL_List.append(PnL)
                            Capital = Capital + PnL
                         
                            #hold_temp.setStopLoss(current_price + current_atr)           
                            #hold_temp.setAtr(current_atr)
                            hold_temp.setUnits(quantity)
                            
                            #stop_loss_list[inner_rec] = hold_temp.getStopLoss()
                            #atr_list[inner_rec] = hold_temp.getAtr()
                            unit_list[inner_rec] = hold_temp.getUnits()
                            
                            if (PnL > 0):
                                number_of_winning_trades += 1
                                number_of_trades = number_of_lossing_trades + number_of_winning_trades
                            else:
                                number_of_lossing_trades += 1
                                number_of_trades = number_of_lossing_trades + number_of_winning_trades
                                                
                                hold_record_df = pd.DataFrame(hold_record, columns = columns_header)
                                
                        else:
                        #Reset Stop Loss
                            hold_temp.setStopLoss(current_price + current_atr)           
                            hold_temp.setAtr(current_atr)
                        
                            stop_loss_list[inner_rec] = hold_temp.getStopLoss()
                            atr_list[inner_rec] = hold_temp.getAtr()
                                          
                            hold_record_df = pd.DataFrame(hold_record, columns = columns_header)
                        
                        
                            data = "Reset Stop Loss and Close Partial Position"
                            savefile(filename,data)
                        
                            data = hold_record_df
                            savefile(filename,data)
                        
                                        
                if (previous_transaction == "BUY"):
                    if (current_price < hold_temp.getStopLoss()):
                                
                        Notional_Amount = current_price * hold_temp.getUnits()                 
                        PnL = (current_price - hold_temp.getTransactionPrice()) * hold_temp.getUnits()
                        PnL_List.append(PnL)
                        Capital = Capital + PnL
                        
                        if (PnL > 0):
                            number_of_winning_trades += 1
                            number_of_trades = number_of_lossing_trades + number_of_winning_trades
                        else:
                            number_of_lossing_trades += 1
                            number_of_trades = number_of_lossing_trades + number_of_winning_trades
                    
                        data = "Exit"
                        savefile(filename,data)
                        
                        data = hold_record_df
                        savefile(filename,data)
                                            
                        remove_record(inner_rec)
                        hold_record_df = hold_record_df.drop([inner_rec])
                        hold_record_df = pd.DataFrame(hold_record, columns = columns_header)
                        check_count = len(hold_record_df.index)
                        
                        
                        continue 
                    
                    else:
                        
                        #Main Stop Loss, and quantity, closing partial position  
                        spread = hold_temp.getUnits() * hold_temp.getAtr()
                        quantity = round(spread / current_atr,0)
                        
                        # Current ATR Greater than Holding ATR, reduce current holdings                                         
                        if(current_atr > hold_temp.getAtr()):                        
                        
                            #Notional_Amount = current_price * hold_temp.getUnits()                 
                            PnL = (current_price - hold_temp.getTransactionPrice()) * (hold_temp.getUnits() - quantity)
                            PnL_List.append(PnL)
                            Capital = Capital + PnL
                        
                            #hold_temp.setStopLoss(current_price + current_atr)           
                            hold_temp.setAtr(current_atr)
                            hold_temp.setUnits(quantity)
                        
                            #stop_loss_list[inner_rec] = hold_temp.getStopLoss()
                            atr_list[inner_rec] = hold_temp.getAtr()
                            unit_list[inner_rec] = hold_temp.getUnits()
                        
                            if (PnL > 0):
                                number_of_winning_trades += 1
                                number_of_trades = number_of_lossing_trades + number_of_winning_trades
                            else:
                                number_of_lossing_trades += 1
                                number_of_trades = number_of_lossing_trades + number_of_winning_trades 
                                hold_record_df = pd.DataFrame(hold_record, columns = columns_header)
                        
                        else: 

                            #Reset Stop Loss
                            hold_temp.setStopLoss(current_price - current_atr) 
                            hold_temp.setAtr(current_atr)
                            
                            stop_loss_list[inner_rec] = hold_temp.getStopLoss()
                            atr_list[inner_rec] = hold_temp.getAtr()
                            
                            hold_record_df = pd.DataFrame(hold_record, columns = columns_header)
                            
                            data = "Reset Stop Loss and Close Partial Position"
                            savefile(filename,data)
                            
                            data = hold_record_df
                            savefile(filename,data)                       
                                                    
                inner_rec +=1
                        
        iterate += 1

    # Generate final results
    final_results(Capital,number_of_trades,number_of_winning_trades,number_of_lossing_trades,filename)
    #Plot Data
    plotGraph(df,PnL_List,lag,currency,filename)
  
'''Order Function'''    
def order(hold):
    
    
    capital_list.append(hold.getCapital())
    currency_list.append(hold.getUnderlying())
    unit_list.append(hold.getUnits())
    transaction_type_list.append(hold.getTransactionType())
    transaction_price_list.append(hold.getTransactionPrice())
    stop_loss_list.append(hold.getStopLoss())
    atr_list.append(hold.getAtr())

'''Close Position Function'''

def remove_record(inner_rec):
    
    capital_list.pop(inner_rec)
    currency_list.pop(inner_rec)
    unit_list.pop(inner_rec)
    transaction_type_list.pop(inner_rec)
    transaction_price_list.pop(inner_rec)
    stop_loss_list.pop(inner_rec)
    atr_list.pop(inner_rec)

'''Plot Data'''
def plotGraph(df,PnL_List,lag,currency,filename):
    
    #datetime = list(df['Date'])
    #datetime = [w.replace(".","/") for w in datetime]
    #datetime = [w.replace("00:00:00", "") for w in datetime]
    
    #date = dates.datestr2num(datetime)
    
    fig = plt.figure(facecolor='white')
    
    plt.rc('axes', grid=True)
    plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)
    
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
        
    ax1.plot(df.index, df[str(lag) + '_MA_Close'], color='red',label= str(lag) +  'Day MA')
    ax1.plot(df.index, df['Close'], color='green',label='Close')
    ax1.set_title(currency)
    
    total_PnL = {'Profit and Loss': PnL_List}
    PnL_df = pd.DataFrame(total_PnL) 
    
    ax2.set_title("Profit and Loss")
    ax2.plot(PnL_df.index,PnL_df['Profit and Loss'],color='blue',label='Profit and Loss')
    
    ax1.legend(loc='best')
    ax2.legend(loc='best')
 
    h = os.getcwd()
    outputDir = h + '/Output/'
    
    filename = filename.replace("txt","png")
    filename = outputDir + filename
    plt.savefig(filename, dpi=400, bbox_inches='tight')
    #plt.show()

'''Get max range for ATR'''
def max_range(high_low,high_close,low_close):
    
    if(high_low > high_close):
        
        if high_low > low_close:
            return high_low
        else:
            return low_close
        
    else:
        if high_close > low_close:
            return high_close
        
        return low_close

'''Get Signal to Buy or Sell'''  
def check_signal(current_price,current_MA_Close):
    
        # If current price is above Lag SMA , BUY on current price
        if(current_price > current_MA_Close):
            action_signal = "BUY"
        # If current price is above Lag SMA , SELL on current price
        elif(current_price < current_MA_Close):
            action_signal = "SELL"
        else:
            action_signal = ""
               
        return action_signal

def dataStr(action_signal,iterate,Enter_price,lag,current_MA_Close,Capital,current_atr):
                    
    return "Previous day signal indicates " + action_signal + " " + str(iterate) + ". Current price " + str(Enter_price) + \
            " Current " + str(lag) +  " MA Last " + str(current_MA_Close) + " Current Capital  " \
           + str(Capital) + " Current ATR " + str(current_atr)


def final_results(Capital,number_of_trades,number_of_winning_trades,number_of_lossing_trades,filename):
    # Print final results
    print "Capital " + str(Capital)    
    print "Number of Trades " + str(number_of_trades)
    print "Number of Winning Trades " + str(number_of_winning_trades)
    print "Number of Lossing Trades " + str(number_of_lossing_trades)
    print "Percentage of Success " + str(number_of_winning_trades/number_of_trades)
    print "\n"
    print "Back Test End. Please review results"

    data = "Capital " + str(Capital) + '\n' + \
            "Number of Trades " + str(number_of_trades) + '\n' + \
            "Number of Winning Trades " + str(number_of_winning_trades) + "\n" + \
            "Number of Lossing Trades " + str(number_of_lossing_trades) + "\n" + \
            "Percentage of Success " + str(number_of_winning_trades/number_of_trades) + "\n" + \
             "Back Test End. Please review results"
    
    savefile(filename,data)


