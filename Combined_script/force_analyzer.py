import numpy as np
import pandas as pd
import os 
import processor as pr
import matplotlib.pyplot as plt
from scipy.linalg import lstsq

calibration_matrix_left = np.matrix([
    [1.0000, 1.9493,    1.6587,    2.2420,    1.7540,    1.9193],
    [2.0000,    3.6907,    3.5587,    3.9753,    3.4786,    3.8687],
    [5.0000,    8.8000,    9.3114,    9.2673,    8.4786,    9.5333],
    [10.0000,   17.5027,   18.9934,   17.9506,   16.8893,   19.2387],
    [20.0000,   34.3767,   38.4054,   35.0546,   33.5433,   38.1693],
    [50.0000,   86.1053,   95.7240,   87.9353,   83.9440,   95.6927]
])

calibration_matrix_middle= np.matrix([
    [1.0000,     1.6638,     1.9447,     1.8651,     1.9108,     1.4993],
    [2.0000 ,    3.2618 ,    3.8481,     3.7791 ,    3.7948 ,    3.2386],
    [5.0000  ,   8.2305  ,   9.4354,     9.3625 ,    9.5075 ,    7.8660],
   [10.0000 ,   16.6231 ,   19.0834,    18.6811,    18.8928,    16.0100],
   [20.0000   , 33.2878 ,   38.1934,    37.3471,    37.7435 ,   32.0826],
   [50.0000  ,  83.6805 ,   95.5994 ,   93.2598 ,   94.5148 ,   81.3853]
])

calibration_matrix_right = np.matrix([
    [1.0000,    1.9564,   1.9894,    1.9617,    1.9434,    1.7588],
    [2.0000,    3.4971,    3.8274,    3.8237 ,   3.6300 ,   3.5828],
   [ 5.0000,    8.5471,    9.4460 ,   9.1737,    9.4027 ,   8.5048],
   [10.0000,   17.2671 ,  18.8220,   18.6490,   19.0007 ,  16.7115],
   [20.0000,   34.1691 ,  37.7080 ,  36.9123 ,  38.1627 ,  33.3355],
   [50.0000,   85.0704 ,  94.4140 ,  92.2503 ,  96.4520 ,  83.2661]]
)

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
        self.iC_force_dis = {'prime_cong':[], 'prime_incon':[]}
        self.iI_force_dis = {'prime_cong':[], 'prime_incon':[]}
        self.cC_force_tar = {'prime_cong':[], 'prime_incon':[]}
        self.cI_force_tar = {'prime_cong':[], 'prime_incon':[]}
        self.iC_force_tar = {'prime_cong':[], 'prime_incon':[]}
        self.iI_force_tar = {'prime_cong':[], 'prime_incon':[]}
        self.prime_os_cC = []
        self.prime_os_cI = []
        self.prime_os_iC = []
        self.prime_os_iI = []
        self.probe_os_cC = []
        self.probe_os_cI = []
        self.probe_os_iC = []
        self.probe_os_iI = []


    def calibrate(self, dataf, base, keyboard):
        """
        Do the force calibration process

        Parameters:
            dataf(DataFrame): the data to calibrate
            base(series): the base levels of key F, G, J, K, and N
            keyboard(string): "PSYC-DANWEISS23", "PSYC-DANWEISS25", or "PSYC-DANWEISS24". 
                    Decide which calibration matrix should this dataf use

        Return:
            none
        """
        #1. get the baseline value
       
        dataf['force_F'] =  dataf['force_F'] -base['force_F']
        dataf['force_G'] =  dataf['force_G'] -base['force_G']
        dataf['force_J'] =  dataf['force_J'] -base['force_J']
        dataf['force_K'] =  dataf['force_K'] -base['force_K']
        dataf['force_N'] =  dataf['force_N'] -base['force_N']
        

        #2. calibration matrix
        if(keyboard == "PSYC-DANWEISS23"):
            cm = calibration_matrix_left
        if(keyboard == "PSYC-DANWEISS25"):
            cm = calibration_matrix_middle
        if(keyboard == "PSYC-DANWEISS24"):
            cm = calibration_matrix_right
        
        #3. convert the mass values from grams to centinewtons
        cm[:,0] = cm[:,0]/1000 *9.8 *100
        
        #4. design matrix
        dm = np.hstack([cm[:, 0], np.ones([cm.shape[0], 1])])

        #5. regression
            # in matlab, regress(y, X); in python, lstsq(A, y); X: DM
        key_f, _, _, _ = lstsq(dm, cm[:, 1])
        key_g, _, _, _ = lstsq(dm, cm[:, 2])
        key_j, _, _, _ = lstsq(dm, cm[:, 3])
        key_k, _, _, _ = lstsq(dm, cm[:, 4])
        key_n, _, _, _ = lstsq(dm, cm[:, 5])
            # convert
        dataf['force_F']  = (dataf['force_F']  - key_f[1])/key_f[0]
        dataf['force_G']  = (dataf['force_G']  - key_g[1])/key_g[0]
        dataf['force_J']  = (dataf['force_J']  - key_j[1])/key_j[0]
        dataf['force_K']  = (dataf['force_K']  - key_k[1])/key_k[0]
        dataf['force_N']  = (dataf['force_N']  - key_n[1])/key_n[0]

        return 0

    def col_read(self):
        """
        Read in & Add the column name to the force data and return the dataframe that only keep the test trials
        
        Parameters:
            filename (string): the file path of the desired force data

        Returns:
            base (dataframe): the base levels for all five keys
            dataf (dataframe): the dataframe with correct column names & reduced trials
        """
        #read in & add column names
        col = ['force_F', 'force_G', 'force_J', 'force_K', 'force_N', 'Photodiode', 
                'record_F', 'record_G', 'record_J', 'record_K', 'record_N', 
                'record_X_', 'record_Y_', 'stimulus_flag', 
                'Timestamps']
        self.ps_data = pr.identify_outliers(pr.psypy_reduce(pd.read_csv(self.ps_filename)))
        self.ps_data = self.ps_data[(self.ps_data["PrevAcc"]=="Correct") ] #& (self.ps_data["CurrAcc"]=="Correct")]
        #self.ps_data = self.ps_data[self.ps_data["Outlier"]==False]
        dataf = pd.read_csv(self.force_filename, names=col)
        base = dataf.iloc[:500, 0:5].mean()

        #reduce the trials
        start = self.ps_data['Distractor_onset'][self.ps_data.index[0]]
        ind = 0
        for i in dataf.index:
            if (dataf['Timestamps'][i]>=start):
                ind = i
                break
        #print(ind)
        dataf=dataf[ind-100:]
        self.calibrate(dataf, base, "PSYC-DANWEISS24")
        self.force_data = dataf
        self.force_data.index = range(len(self.force_data))
        
        return base, dataf

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
            distracotr_onsets (series): the collection of all onset timestamps of distractors (primes)
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
            # timestamp in psychpy --> timestamp in force data --> the index of that row in force data
            indexes.append(self.force_data[self.force_data["Timestamps"]==i].index.to_list()[0])

        for j in list(range(len(dis))):
            #prime congruent
            dis_col = conv[dis[j][-8:]] #type(dis_col) = string
            #prime incongruent
            if dis_col == "force_F":
                tar_col = "force_G" #prime incongruent key
            elif dis_col == "force_G":
                tar_col = "force_F"
            elif dis_col == "force_J":
                tar_col = "force_N"
            else:
                tar_col = "force_J"
            ind = indexes[j]
            piece = self.force_data[ind:ind+1500]
            cong_frame[j] = list(piece[dis_col])  #column name-> trials; rows-> each time timestamp
            inco_frame[j] = list(piece[tar_col])

        aver_force = {'prime_cong':cong_frame.mean(axis=1), 'prime_incon':inco_frame.mean(axis=1)}
        return aver_force, distractor_onsets
    
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
            target_onsets (series): the collection of all onset timestamps of targets (probes)
        """
        target_onsets = dataf["Target_onset"]
        dis = list(dataf["Distractor"])
        tar = list(dataf["Target"])
        conv = {'Left.png':"force_F", "D_Up.png":"force_J", "Down.png":"force_N", 
                    "ight.png":"force_G", "T_Up.png":"force_J"}
        primeC_frame = pd.DataFrame()
        primeI_frame = pd.DataFrame()
        probeC_frame = pd.DataFrame()
        probeI_frame = pd.DataFrame()

        indexes = []
        for i in target_onsets:
            indexes.append(self.force_data[self.force_data["Timestamps"]==i].index.to_list()[0])
        for j in list(range(len(dis))):
            #one 'column'
            dis_col = conv[dis[j][-8:]]
            tar_col = conv[tar[j][-8:]]

            if dis_col == "force_F":
                disC_col = "force_G"
            elif dis_col == "force_G":
                disC_col = "force_F"
            elif dis_col == "force_J":
                disC_col = "force_N"
            else:
                disC_col = "force_J"

            if tar_col == "force_F":
                tarC_col = "force_G"
            elif tar_col == "force_G":
                tarC_col = "force_F"
            elif tar_col == "force_J":
                tarC_col = "force_N"
            else:
                tarC_col = "force_J"

            ind = indexes[j]
            piece = self.force_data[ind:ind+1500]
            primeC_frame[j] = list(piece[dis_col])  #column name-> trials; rows-> each time timestamp
            primeI_frame[j] = list(piece[disC_col])
            probeC_frame[j] = list(piece[tar_col])
            probeI_frame[j] = list(piece[tarC_col])

        aver_force = {'prime_cong':primeC_frame.mean(axis=1), 'prime_incon':primeI_frame.mean(axis=1),
                'probe_cong':probeC_frame.mean(axis=1), 'probe_incon':probeI_frame.mean(axis=1)}
        return aver_force, target_onsets

    def get_force(self):
        """
        Divide the ps_data into 4 dataframes: cC, CI, iC,  iI
        """
        #divide_py_data
        cC=self.ps_data[(self.ps_data["PrevTrialType"]=="Congruent")&(self.ps_data["CurrTrialType"]=="Congruent")]
        cI=self.ps_data[(self.ps_data["PrevTrialType"]=="Congruent")&(self.ps_data["CurrTrialType"]=="Incongruent")]
        iC=self.ps_data[(self.ps_data["PrevTrialType"]=="Incongruent")&(self.ps_data["CurrTrialType"]=="Congruent")]
        iI=self.ps_data[(self.ps_data["PrevTrialType"]=="Incongruent")&(self.ps_data["CurrTrialType"]=="Incongruent")]

        self.cC_force_dis, self.prime_os_cC = self.calc_force_average_distractOn(cC, "cC")
        self.cI_force_dis, self.prime_os_cI = self.calc_force_average_distractOn(cI,"cI")
        self.iC_force_dis, self.prime_os_iC = self.calc_force_average_distractOn(iC,"iC")
        self.iI_force_dis, self.prime_os_iI = self.calc_force_average_distractOn(iI,"iI")

        self.cC_force_tar, self.probe_os_cC = self.calc_force_average_targetOn(cC, "cC")
        self.cI_force_tar, self.probe_os_cC = self.calc_force_average_targetOn(cI,"cI")
        self.iC_force_tar, self.probe_os_cC = self.calc_force_average_targetOn(iC,"iC")
        self.iI_force_tar, self.probe_os_cC = self.calc_force_average_targetOn(iI,"iI")
    
    

    def plot_primeON(self):
        """
        Prepare the data used for creating force curves based on the prime onset

        Parameters: 
            None
        
        Return: 
            pc_prev_cong (list): the list of all forces of prime-congruent keys when the previous trial is congruent
            pc_prev_inc (list): the list of all forces of prime-congruent keys when the previous trial is incongruent
            pi_prev_cong (list): the list of all forces of prime-incongruent keys when the previous trial is congruent
            pi_prev_inc (list): the list of all forces of prime-incongruent keys when the previous trial is incongruent
        """
        #time_x = np.arange(-200, 468*2, 2)
        time_x = np.arange(0, 1500, 1)

        pc1, _ = self.calc_force_average_distractOn(self.ps_data[self.ps_data["PrevTrialType"]=="Congruent"], "xx")
        pc_prev_cong = pc1["prime_cong"]
        
        pc2, _ = self.calc_force_average_distractOn(self.ps_data[self.ps_data["PrevTrialType"]=="Incongruent"], "xx")
        pc_prev_inc = pc2["prime_cong"]

        pc3, _ =self.calc_force_average_distractOn(self.ps_data[self.ps_data["PrevTrialType"]=="Congruent"], "xx")
        pi_prev_cong = pc3["prime_incon"]

        pc4, _ = self.calc_force_average_distractOn(self.ps_data[self.ps_data["PrevTrialType"]=="Incongruent"], "xx")
        pi_prev_inc = pc4["prime_incon"]

        return pc_prev_cong, pc_prev_inc, pi_prev_cong, pi_prev_inc


    def plot_probeON(self):
        """
        Prepare the data used for creating force curves based on the probe onset

        Parameters: 
            None
        
        Return: 
            pc_prev_cong (list): the list of all forces of prime-congruent keys when the previous trial is congruent
            pc_prev_inc (list): the list of all forces of prime-congruent keys when the previous trial is incongruent
            pi_prev_cong (list): the list of all forces of prime-incongruent keys when the previous trial is congruent
            pi_prev_inc (list): the list of all forces of prime-incongruent keys when the previous trial is incongruent
        """
        """
        probe-congruent key / probe-incongruent key; still prev cong/inc
        """

        pc1,_ = self.calc_force_average_targetOn(self.ps_data[self.ps_data["PrevTrialType"]=="Congruent"], "xx")
        pc_prev_cong = pc1["probe_cong"]

        pc2, _ = self.calc_force_average_targetOn(self.ps_data[self.ps_data["PrevTrialType"]=="Incongruent"], "xx")
        pc_prev_inc = pc2["probe_cong"]

        pc3, _ =self.calc_force_average_targetOn(self.ps_data[self.ps_data["PrevTrialType"]=="Congruent"], "xx")
        pi_prev_cong = pc3["probe_incon"]

        pc4, _ = self.calc_force_average_targetOn(self.ps_data[self.ps_data["PrevTrialType"]=="Incongruent"], "xx")
        pi_prev_inc = pc4["probe_incon"]

        return pc_prev_cong, pc_prev_inc, pi_prev_cong, pi_prev_inc



"""
    Driver for multiple files
"""
def folder_select(psych_folder = "Data", force_folder = "Forcefiles"):
    """
        Run analysis on all files in the selected folders. Store the converted data & force curve figures

        Parameters:
            psych_folder (string): the folder that contains all psychopy data. Default: Data
            force_folder (string): the folder that contains all force data. Default: Forcefiles

        Return:
            None
    """

    psych_list = os.listdir(psych_folder)
    psych_list.remove(".DS_Store")
    force_list = os.listdir(force_folder)
    force_list.remove(".DS_Store")
    tool = Force_analysis(force_folder+"/"+force_list[0], psych_folder+"/"+psych_list[0])
    prime_dict = {"pc_prev_cong":np.zeros([1500,]), "pc_prev_inc":np.zeros([1500,]), "pi_prev_cong":np.zeros([1500,]), "pi_prev_inc":np.zeros([1500,])}
    probe_dict = {"pc_prev_cong":np.zeros([1500,]), "pc_prev_inc":np.zeros([1500,]), "pi_prev_cong":np.zeros([1500,]), "pi_prev_inc":np.zeros([1500,])}
    for psych in psych_list:
        for force in force_list:
            if psych[:3] == force[:3]:
                tool = Force_analysis(force_folder+"/"+force, psych_folder+"/"+psych)
                print(psych)
        _, force_data = tool.col_read()
        force_data.to_csv("Converted_force/"+psych[:8]+".csv")
        tool.get_force()
        a, b, c, d = tool.plot_primeON()
        e, f, g, h = tool.plot_probeON()
        prime_dict["pc_prev_cong"] += a
        print(prime_dict["pc_prev_cong"])
        prime_dict["pc_prev_inc"] += b
        prime_dict["pi_prev_cong"] += c
        prime_dict["pi_prev_inc"] += d
        probe_dict["pc_prev_cong"] += e
        probe_dict["pc_prev_inc"] +=f
        probe_dict["pi_prev_cong"] +=g
        probe_dict["pi_prev_inc"] += h
    for i in ["pc_prev_cong", "pc_prev_inc", "pi_prev_cong", "pi_prev_inc"]:
        prime_dict[i]  = prime_dict[i]/len(psych_list)
        probe_dict[i]  = probe_dict[i]/len(psych_list)
    time_x = np.arange(0, 1500, 1)
    print(prime_dict["pc_prev_cong"])
    
    # Figure for Prime On
    plt.figure(figsize=(16, 6))
    plt.subplot(1, 2, 1)
    plt.plot(time_x, prime_dict["pc_prev_cong"], label = "Prev Cong")
    plt.plot(time_x, prime_dict["pc_prev_inc"], label = "Prev Incong")
    plt.legend()
    plt.title("Prime-Congruent Key")
    #plt.ylim([300, 570])
    plt.subplot(1, 2, 2)
    plt.plot(time_x, prime_dict["pi_prev_cong"], label = "Prev Cong")
    plt.plot(time_x, prime_dict["pi_prev_inc"], label = "Prev Incong")
    plt.legend()
    plt.title("Prime-Incongruent Key")
    #plt.ylim([300, 570])
    plt.savefig("Figures/group_primeON")

    # Figure for Probe On
    plt.figure(figsize=(16, 6))
    plt.subplot(1, 2, 1)
    plt.plot(time_x, probe_dict["pc_prev_cong"], label = "Prev Cong")
    plt.plot(time_x, probe_dict["pc_prev_inc"], label = "Prev Incong")
    plt.legend()
    plt.title("Probe-Congruent Key")
    #plt.ylim([300, 570])
    plt.subplot(1, 2, 2)
    plt.plot(time_x, probe_dict["pi_prev_cong"], label = "Prev Cong")
    plt.plot(time_x, probe_dict["pi_prev_inc"], label = "Prev Incong")
    plt.legend()
    plt.title("Probe-Incongruent Key")
    #plt.ylim([300, 570])
    plt.savefig("Figures/group_probeON")



def multiple_files_select(psych_list, force_list, name):
    """
        Run analysis on all files in the provided lists. Store the converted data & force curve figures

        Parameters:
            psych_list (list): string list. example: "657_pressure-data.csv". All files should in the folder "Data"
            force_list (list): string list. example: "657_Prime-Probe_2022-10-25_18h18.22.999.csv". 
                    All files should in the folder "Forcefiles"
            name (string): to name the force curve figures. example: "test"

        Return:
            None
    """
    prime_dict = {"pc_prev_cong":np.zeros([1500,]), "pc_prev_inc":np.zeros([1500,]), "pi_prev_cong":np.zeros([1500,]), "pi_prev_inc":np.zeros([1500,])}
    probe_dict = {"pc_prev_cong":np.zeros([1500,]), "pc_prev_inc":np.zeros([1500,]), "pi_prev_cong":np.zeros([1500,]), "pi_prev_inc":np.zeros([1500,])}

    for i in np.arange(len(psych_list)):
        print(force_list[i])
        tool = Force_analysis("Forcefiles/"+force_list[i], "Data/"+psych_list[i])
        _, force_data = tool.col_read()
        force_data.to_csv("Converted_force/"+psych_list[i][:8]+".csv")
        tool.get_force()
        a, b, c, d = tool.plot_primeON()
        e, f, g, h = tool.plot_probeON()
        prime_dict["pc_prev_cong"] += a
        print(prime_dict["pc_prev_cong"])
        prime_dict["pc_prev_inc"] += b
        prime_dict["pi_prev_cong"] += c
        prime_dict["pi_prev_inc"] += d
        probe_dict["pc_prev_cong"] += e
        probe_dict["pc_prev_inc"] +=f
        probe_dict["pi_prev_cong"] +=g
        probe_dict["pi_prev_inc"] += h

    for i in ["pc_prev_cong", "pc_prev_inc", "pi_prev_cong", "pi_prev_inc"]:
        prime_dict[i]  = prime_dict[i]/len(psych_list)
        probe_dict[i]  = probe_dict[i]/len(psych_list)
    time_x = np.arange(0, 1500, 1)
    print(prime_dict["pc_prev_cong"])

    # Figure for Prime On
    plt.figure(figsize=(16, 6))
    plt.subplot(1, 2, 1)
    plt.plot(time_x, prime_dict["pc_prev_cong"], label = "Prev Cong")
    plt.plot(time_x, prime_dict["pc_prev_inc"], label = "Prev Incong")
    plt.legend()
    plt.title("Prime-Congruent Key")
    #plt.ylim([300, 570])
    plt.subplot(1, 2, 2)
    plt.plot(time_x, prime_dict["pi_prev_cong"], label = "Prev Cong")
    plt.plot(time_x, prime_dict["pi_prev_inc"], label = "Prev Incong")
    plt.legend()
    plt.title("Prime-Incongruent Key")
    #plt.ylim([300, 570])
    plt.savefig("Figures/"+name+"_primeON")

    # Figure for Probe On
    plt.figure(figsize=(16, 6))
    plt.subplot(1, 2, 1)
    plt.plot(time_x, probe_dict["pc_prev_cong"], label = "Prev Cong")
    plt.plot(time_x, probe_dict["pc_prev_inc"], label = "Prev Incong")
    plt.legend()
    plt.title("Probe-Congruent Key")
    #plt.ylim([300, 570])
    plt.subplot(1, 2, 2)
    plt.plot(time_x, probe_dict["pi_prev_cong"], label = "Prev Cong")
    plt.plot(time_x, probe_dict["pi_prev_inc"], label = "Prev Incong")
    plt.legend()
    plt.title("Probe-Incongruent Key")
    #plt.ylim([300, 570])
    plt.savefig("Figures/"+name+"_probeON")