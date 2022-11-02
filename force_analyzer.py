import numpy as np
import pandas as pd
import statistics as st
import processor as pr
import matplotlib.pyplot as plt
import seaborn as sns

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
        self.cC_force_dis = {'prime_cong':[], 'prime_incon':[]}
        self.cI_force_dis = {'prime_cong':[], 'prime_incon':[]}
        self.nC_force_dis = {'prime_cong':[], 'prime_incon':[]}
        self.nI_force_dis = {'prime_cong':[], 'prime_incon':[]}
        self.iC_force_dis = {'prime_cong':[], 'prime_incon':[]}
        self.iI_force_dis = {'prime_cong':[], 'prime_incon':[]}
        self.cC_force_tar = {'prime_cong':[], 'prime_incon':[]}
        self.cI_force_tar = {'prime_cong':[], 'prime_incon':[]}
        self.nC_force_tar = {'prime_cong':[], 'prime_incon':[]}
        self.nI_force_tar = {'prime_cong':[], 'prime_incon':[]}
        self.iC_force_tar = {'prime_cong':[], 'prime_incon':[]}
        self.iI_force_tar = {'prime_cong':[], 'prime_incon':[]}



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
        self.ps_data = self.ps_data[(self.ps_data["PrevAcc"]=="Correct") & (self.ps_data["CurrAcc"]=="Correct")]
        dataf = pd.read_csv(self.force_filename, names=col)

        #reduce the trials
        start = self.ps_data['Distractor_onset'][self.ps_data.index[0]]
        ind = 0
        for i in dataf.index:
            if (dataf['Timestamps'][i]>=start):
                ind = i
                break
        #print(ind)
        dataf=dataf[ind-100:]
        self.force_data = dataf
        self.force_data.index = range(len(self.force_data))
        
        return dataf

    def calc_force_average_distractOn(self, dataf, cond):
        """
        Read in 

        Parameters:
            dataf (dataframe): psychpy dataframe of one specific condition
            cond (string): what kind of condition; determing which should be prime-con & which prime-incon
                when xC: prime-con [distractor key], prime-incon [the other]; target key = distractor key
                when xI: prime-con [distractor key], prime-incon [target key]

        Returns:
            aver_force (dictionary): key: prime-cong/prime-incon. 
                    values: forces, length = 567; the average data of one participant
        """
        distractor_onsets = dataf["Distractor_onset"]
        dis = list(dataf["Distractor"])
        tar = list(dataf["Target"])
        conv = {'Left.png':"force_F", "D_Up.png":"force_J", "Down.png":"force_N", 
                    "ight.png":"force_G", "T_Up.png":"force_J"}
        cong_frame = pd.DataFrame()
        inco_frame = pd.DataFrame()

        indexes = []
        for i in distractor_onsets:
            indexes.append(self.force_data[self.force_data["Timestamps"]==i].index.to_list()[0])
        for j in list(range(len(dis))):
            #prime congruent
            dis_col = conv[dis[j][-8:]] #type(dis_col) = string
            #prime incongruent
            if cond.endswith("I"):
                tar_col = conv[tar[j][-8:]]
            else:
                if dis_col == "force_F":
                    tar_col = "force_G"
                elif dis_col == "force_G":
                    tar_col = "force_F"
                elif dis_col == "force_J":
                    tar_col = "force_N"
                else:
                    tar_col = "force_J"
            
            ind = indexes[j]
            piece = self.force_data[ind-100:ind+468]
            cong_frame[i] = list(piece[dis_col])  #column name-> trials; rows-> each time timestamp
            inco_frame[i] = list(piece[tar_col])

        aver_force = {'prime_cong':cong_frame.mean(axis=1), 'prime_incon':inco_frame.mean(axis=1)}
        return aver_force
    
    def calc_force_average_targetOn(self, dataf, cond):
        """
        Read in 

        Parameters:
            dataf (dataframe): psychpy dataframe of one specific condition
            cond (string): what kind of condition; determing which should be prime-con & which prime-incon
                when xC: prime-con [distractor key], prime-incon [the other]; target key = distractor key
                when xI: prime-con [distractor key], prime-incon [target key]

        Returns:
            aver_force (dictionary): key: prime-cong/prime-incon. 
                    values: forces, length = 567; the average data of one participant
        """
        target_onsets = dataf["Target_onset"]
        dis = list(dataf["Distractor"])
        tar = list(dataf["Target"])
        conv = {'Left.png':"force_F", "D_Up.png":"force_J", "Down.png":"force_N", 
                    "ight.png":"force_G", "T_Up.png":"force_J"}
        cong_frame = pd.DataFrame()
        inco_frame = pd.DataFrame()

        indexes = []
        for i in target_onsets:
            indexes.append(self.force_data[self.force_data["Timestamps"]==i].index.to_list()[0])
        for j in list(range(len(dis))):
            #one 'column'
            dis_col = conv[dis[j][-8:]]
            if cond.endswith("I"):
                tar_col = conv[tar[j][-8:]]
            else:
                if dis_col == "force_F":
                    tar_col = "force_G"
                elif dis_col == "force_G":
                    tar_col = "force_F"
                elif dis_col == "force_J":
                    tar_col = "force_N"
                else:
                    tar_col = "force_J"
            ind = indexes[j]
            piece = self.force_data[ind-100:ind+468]
            cong_frame[i] = list(piece[dis_col])  #column name-> trials; rows-> each time timestamp
            inco_frame[i] = list(piece[tar_col])

        aver_force = {'prime_cong':cong_frame.mean(axis=1), 'prime_incon':inco_frame.mean(axis=1)}
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

        self.cC_force_dis = self.calc_force_average_distractOn(cC, "cC")
        self.cI_force_dis = self.calc_force_average_distractOn(cI,"cI")
        self.nC_force_dis = self.calc_force_average_distractOn(nC,"nC")
        self.nI_force_dis = self.calc_force_average_distractOn(nI,"nI")
        self.iC_force_dis = self.calc_force_average_distractOn(iC,"iC")
        self.iI_force_dis = self.calc_force_average_distractOn(iI,"iI")

        self.cC_force_tar = self.calc_force_average_targetOn(cC, "cC")
        self.cI_force_tar = self.calc_force_average_targetOn(cI,"cI")
        self.nC_force_tar = self.calc_force_average_targetOn(nC,"nC")
        self.nI_force_tar = self.calc_force_average_targetOn(nI,"nI")
        self.iC_force_tar = self.calc_force_average_targetOn(iC,"iC")
        self.iI_force_tar = self.calc_force_average_targetOn(iI,"iI")
    
    
    def plot_distractorON(self):
        pc_prev_cong = (self.cC_force_dis["prime_cong"] + self.cI_force_dis["prime_cong"])/2
        #pc_prev_neu = (self.nC_force_dis["prime_cong"] + self.nI_force_dis["prime_cong"])/2
        pc_prev_inc = (self.iC_force_dis["prime_cong"] + self.iI_force_dis["prime_cong"])/2
        pi_prev_cong = (self.cC_force_dis["prime_incon"] + self.cI_force_dis["prime_incon"])/2
        #pi_prev_neu = (self.nC_force_dis["prime_incon"] + self.nI_force_dis["prime_incon"])/2
        pi_prev_inc = (self.iC_force_dis["prime_incon"] + self.iI_force_dis["prime_incon"])/2

        plt.plot(np.arange(len(pc_prev_cong)), pc_prev_cong, label = "Prev Cong")
        #plt.plot(np.arange(len(pc_prev_neu)), pc_prev_neu, label = "Prev Neutral")
        plt.plot(np.arange(len(pc_prev_inc)), pc_prev_inc, label = "Prev Incong")
        plt.legend()
        plt.title("Prime-Congruent Key")
        plt.ylim([320, 650])
        plt.show()

        plt.plot(np.arange(len(pi_prev_cong)), pi_prev_cong, label = "Prev Cong")
        #plt.plot(np.arange(len(pi_prev_neu)), pi_prev_neu, label = "Prev Neutral")
        plt.plot(np.arange(len(pi_prev_inc)), pi_prev_inc, label = "Prev Incong")
        plt.legend()
        plt.title("Prime-Incongruent Key")
        plt.ylim([320, 650])
        plt.show()

        bar_summary = pd.DataFrame()
        force = []
        prev = []
        prime = []
        for i in pc_prev_cong:
            force.append(i)
            prev.append("Prev Cong")
            prime.append("Prime-Cong")
        for i in pc_prev_inc:
            force.append(i)
            prev.append("Prev Incong")
            prime.append("Prime-Cong")
        for i in pi_prev_cong:
            force.append(i)
            prev.append("Prev Cong")
            prime.append("Prime-Incong")
        for i in pi_prev_inc:
            force.append(i)
            prev.append("Prev Incong")
            prime.append("Prime-Incong")
        bar_summary['force'] = force
        bar_summary['prev'] = prev
        bar_summary['prime'] = prime
        sns.barplot(data=bar_summary, x = prime, y=force, hue = prev)
        plt.ylim([320, 550])
        plt.show()


    def plot_targetON(self):
        pc_prev_cong = (self.cC_force_tar["prime_cong"] + self.cI_force_tar["prime_cong"])/2
        pc_prev_neu = (self.nC_force_tar["prime_cong"] + self.nI_force_tar["prime_cong"])/2
        pc_prev_inc = (self.iC_force_tar["prime_cong"] + self.iI_force_tar["prime_cong"])/2
        pi_prev_cong = (self.cC_force_tar["prime_incon"] + self.cI_force_tar["prime_incon"])/2
        pi_prev_neu = (self.nC_force_tar["prime_incon"] + self.nI_force_tar["prime_incon"])/2
        pi_prev_inc = (self.iC_force_tar["prime_incon"] + self.iI_force_tar["prime_incon"])/2

        plt.plot(np.arange(len(pc_prev_cong)), pc_prev_cong, label = "Prev Cong")
        #plt.plot(np.arange(len(pc_prev_neu)), pc_prev_neu, label = "Prev Neutral")
        plt.plot(np.arange(len(pc_prev_inc)), pc_prev_inc, label = "Prev Incong")
        plt.legend()
        plt.title("Prime-Congruent Key")
        plt.ylim([320, 650])
        plt.show()
        
        plt.plot(np.arange(len(pi_prev_cong)), pi_prev_cong, label = "Prev Cong")
        #plt.plot(np.arange(len(pi_prev_neu)), pi_prev_neu, label = "Prev Neutral")
        plt.plot(np.arange(len(pi_prev_inc)), pi_prev_inc, label = "Prev Incong")
        plt.legend()
        plt.title("Prime-Incongruent Key")
        plt.ylim([320, 650])
        plt.show()

        bar_summary = pd.DataFrame()
        force = []
        prev = []
        prime = []
        for i in pc_prev_cong:
            force.append(i)
            prev.append("Prev Cong")
            prime.append("Prime-Cong")
        for i in pc_prev_inc:
            force.append(i)
            prev.append("Prev Incong")
            prime.append("Prime-Cong")
        for i in pi_prev_cong:
            force.append(i)
            prev.append("Prev Cong")
            prime.append("Prime-Incong")
        for i in pi_prev_inc:
            force.append(i)
            prev.append("Prev Incong")
            prime.append("Prime-Incong")
        bar_summary['force'] = force
        bar_summary['prev'] = prev
        bar_summary['prime'] = prime
        sns.barplot(data=bar_summary, x = prime, y=force, hue = prev)
        plt.ylim([320, 550])
        plt.show()

