import Lib.Utility as ut
import Lib.Strategy as st
import os
import pandas as pd

if __name__ == '__main__':
                
    print "Initialising BackTest 0.1. Please enjoy a drink while I crunch the numbers"

    lag = 2
    
    #inputDir = os.path.dirname(__file__) + '/Forex Input'

    h = os.getcwd()
    inputDir = h + '/Data/'
        
    # Check the list of files available
    inputfiles = os.listdir(inputDir)
    
    # eg : file = 'sample.csv'
    # Load Data Set
    for file in inputfiles :
        
        if not '.csv' in file:
            continue
        
        filename = file
        
        filename = filename.split('.')[0]
        
        file = inputDir + '/' + file
        
        dSet_df = pd.DataFrame()
        dSet_df = ut.loadData(file)    
    
        st.backtest(dSet_df,lag,filename)
    

    


    
    
