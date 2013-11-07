import Lib.Utility as ut
import Lib.Strategy as st
import os
import pandas as pd

if __name__ == '__main__':
                
    print "Initialising BackTest 0.1. Please enjoy a drink while I crunch the numbers"

    lag = 2
    
    #inputDir = os.path.dirname(__file__) + '/Forex Input'

    inputDir = 'C:\Users\Calvin\Documents\Aptana Studio 3 Workspace\FinancialBacktester\Data'
    # Check the list of files available
    inputfiles = os.listdir(inputDir)
    #file = 'sample.csv'
    # Load Data Set
    for file in inputfiles :
        
        if not '.csv' in file:
            continue

        file = inputDir + '/' + file
        
        dSet_df = pd.DataFrame()
        dSet_df = ut.loadData(file)    
    
        st.backtest(dSet_df,lag)
    

    


    
    
