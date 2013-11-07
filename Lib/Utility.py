'''
Created on Nov 7, 2013

@author: Calvin
'''
'''Read File Function'''

import os
import pandas as pd

def readfile(filepath):
        f = open(filepath,"r")
        
        s = f.read()
        
        f.close()
        
        return s.splitlines()

'''Save Output Function'''

def savefile(filename,data):
        
        h = os.getcwd()
        outputDir = h + '/Output/'
        
        filename = outputDir + filename 
        
        output_file = open(filename,"a")
    
        output_file.write(str(data))
        output_file.write('\n')
        output_file.write('\n')

        output_file.close() 

'''Load Data Function'''

def loadData(filename):
    
    #Load Sample data
    df = pd.read_csv(filename)
    return df


            
        