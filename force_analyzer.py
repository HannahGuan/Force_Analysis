import numpy as np
import pandas as pd
import statistics as st
import processor as pr

"""
    [Functions Review]

    col_read (filename): read in & add the column name to the force data and return the dataframe

    each trial condition, calculate the average forces of both target and distracor keys
         in each timestap within the range, plot
    
    Thoughts:
        funcA for calculating the average in one trial conditon
            receive a few pieces of range, probably stored in pandas (x as which piece, y as timestamp; so 567 rows)
            for each row of all pieces, calculate the mean 
        funcB for assgning pieces (from funcC) into funcA 9*2 times
            return 18 567*2(Time, force) df, which enable the visualization
        funcC for finding pieces; create 9*2 dataframe
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
        self.cC_force = dict
        self.cI_force = dict
        self.nC_force = dict
        self.nI_force = dict
        self.iC_force = dict
        self.iI_force = dict



    def col_read(self):
        """
        Read in & Add the column name to the force data and return the dataframe that only keep the test trials
        
        Parameters:
            filename (string): the file path of the desired force data

        Returns:
            dataf (dataframe): the dataframe with correct column names & reduced trials
        """
        #read in & add column names
        col = ['force_F', 'force_G', 'force_J', 'force_K', 'force_N', 'Photodiode', 
                'record_F', 'record_G', 'record_J', 'record_K', 'record_N', 
                'record_X_', 'record_Y_', 'stimulus_flag', 
                'Timestamps']
        self.ps_data = pr.psypy_reduce(pd.read_csv(self.ps_filename))
        self.ps_data = self.ps_data[self.ps_data["PrevAcc"]=="Correct"]
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
        self.force_data.index = range(len(self.force_data))
        
        return dataf

    def calc_force_average(self, dataf):
        """
        Read in 

        Parameters:
            dataf (dataframe): psychpy dataframe of one specific condition

        Returns:
            aver_force (dictionary): key: distractor/target. 
                    values: forces, length = 567; the average data of one participant
        """
        distractor_onsets = dataf["Distractor_onset"]
        dis = list(dataf["Distractor"])
        tar = list(dataf["Target"])
        conv = {'Left.png':"force_F", "D_Up.png":"force_J", "Down.png":"force_N", 
                    "ight.png":"force_G", "T_Up.png":"force_J", }
        dis_frame = pd.DataFrame()
        tar_frame = pd.DataFrame()

        indexes = []
        for i in distractor_onsets:
            indexes.append(self.force_data[self.force_data["Timestamps"]==i].index.to_list()[0])
        for j in list(range(len(dis))):
            #one 'column'
            dis_col = conv[dis[j][-8:]]
            tar_col = conv[tar[j][-8:]]
            ind = indexes[j]
            piece = self.force_data[ind-100:ind+468]
            dis_frame[i] = list(piece[dis_col])  #column name-> trials; rows-> each time timestamp
            tar_frame[i] = list(piece[tar_col])

        aver_force = {'distractor':dis_frame.mean(axis=1), 'target':tar_frame.mean(axis=1)}
        return aver_force
    

    def get_force(self):
        """
        Divide the ps_data into nine dataframes: cC, cN, CI, nC, nN, nI, iC, iN, iI
        """
        #divide_py_data
        cC=self.ps_data[(self.ps_data["PrevTrialType"]=="Congruent")&(self.ps_data["CurrTrialType"]=="Congruent")]
        #cN=self.ps_data[(self.ps_data["PrevTrialType"]=="Congruent")&(self.ps_data["CurrTrialType"]=="Neutral")]
        cI=self.ps_data[(self.ps_data["PrevTrialType"]=="Congruent")&(self.ps_data["CurrTrialType"]=="Incongruent")]
        nC=self.ps_data[(self.ps_data["PrevTrialType"]=="Neutral")&(self.ps_data["CurrTrialType"]=="Congruent")]
        #nN=self.ps_data[(self.ps_data["PrevTrialType"]=="Neutral")&(self.ps_data["CurrTrialType"]=="Neutral")]
        nI=self.ps_data[(self.ps_data["PrevTrialType"]=="Neutral")&(self.ps_data["CurrTrialType"]=="Incongruent")]
        iC=self.ps_data[(self.ps_data["PrevTrialType"]=="Incongruent")&(self.ps_data["CurrTrialType"]=="Congruent")]
        #iN=self.ps_data[(self.ps_data["PrevTrialType"]=="Incongruent")&(self.ps_data["CurrTrialType"]=="Neutral")]
        iI=self.ps_data[(self.ps_data["PrevTrialType"]=="Incongruent")&(self.ps_data["CurrTrialType"]=="Incongruent")]

        self.cC_force = self.calc_force_average(cC)
        self.cI_force = self.calc_force_average(cI)
        self.nC_force = self.calc_force_average(nC)
        self.nI_force = self.calc_force_average(nI)
        self.iC_force = self.calc_force_average(iC)
        self.iI_force = self.calc_force_average(iI)