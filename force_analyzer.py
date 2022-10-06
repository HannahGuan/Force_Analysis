import numpy as np
import pandas as pd
import statistics as st
import processor as pr

"""
    [Functions Review]

    col_read (filename): read in & add the column name to the force data and return the dataframe

    each trial condition, calculate the average force of both target and distracor keys
         in each timestap within the range, plot
    
    Thoughts:
        funcA for calculating the average in one trial conditon
            receive a few pieces of range, probably stored in pandas (x as which piece, y as timestamp; so 567 rows)
            for each row of all pieces, calculate the mean 
        funcB for assgning pieces (from funcC) into funcA 9 times
            return 9 567*2(Time, force) df, which enable the visualization
        funcC for finding pieces; create 9 dataframe
            1. the time in force --> return to py to determine the type
            2. select all columns and let it to be one column in the corresponding df, name it X
            3. use one dictionary to store all df(s)

"""

class Force_analysis:

    def __init__(self, file_force, file_ps):
        self.force_filename = file_force
        self.ps_filename = file_ps
        self.ps_data = pd.DataFrame()
        self.force_data = pd.DataFrame()


    def col_read(self):
        """
        Read in & Add the column name to the force data and return the dataframe that only keep the test trials
        
        Parameters:
            filename (string): the file path of the desired force data

        Returns:
            dataf (dataframe): the dataframe with correct column names & reduced trials
        """
        #read in & add column names
        col = ['force_F', 'force_G', 'force_J', 'force_K', 'force_N', 
            'force_X_', 'force_Y_', 'record_F', 'record_G', 'record_J', 'record_K', 'record_N', 
            'record_X_', 'record_Y_', 'Timestamps']
        self.ps_data = pr.psypy_reduce(pd.read_csv(self.ps_filename))
        dataf = pd.read_csv(self.force_filename, names=col)

        #reduce the trials
        start = self.ps_data['Distractor_onset'][self.ps_data.index[0]]
        ind = 0
        for i in dataf.index:
            if (dataf['Timestamps'][i]>=start):
                #print(dataf['Timestamps'][i])
                ind = i
                break
        #print(ind)
        dataf=dataf[ind-100:]
        self.force_data = dataf
        
        return dataf
