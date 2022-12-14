from ast import And
import numpy as np
import pandas as pd
import statistics as st

"""
    [Functions Review]

    psypy_reduce(dataf): Reduce the PsychoPy dataset to columns of interest & Adds the previous trial's accuracy

    get_demographics(dataf): Extracts demographic info

    get_RT(dataf, condition_type, allow_error=False): Retrive the RT data based on the condition 
                type and whether the current trial should be correct

    compute_sn_oneTrial(trial_RT): Return the median_list and Computes Sn for the specified trial type.

    compute_sn_all(dataf): Add new column 'median_distance' for each trial and Computer Sn for each trial type

    identify_outliers(dataf): Label respective trials as 'outlier' based on their RT and Sn

    get_means(dataf): Return the mean RT of each trial type

    get_error_rate(dataf): Return the error rate of each trial type

    get_overall_accuracy(data): Return the overall accuracy of one participant

    get_total_percent_outliers(): Return the total percent of outliers
"""

def psypy_reduce(dataf):
    """
    Reduce the PsychoPy dataset to columns of interest & Adds the previous trial's accuracy to each row entry
    
    Parameters:
        dataf (DataFrame): the psychopy data read from the csv file

    Returns:
        clean_v (DataFrame): the reduced DataFrame
    """
    #clean useless columns
    clean_v = pd.DataFrame()
    clean_v['ExpName'] = dataf['expName']
    clean_v['PsNum'] = dataf['participant']
    clean_v['Age'] = dataf["How old are you (in years)?"]
    clean_v['Sex'] = dataf['Are you male or female (M or F)?']
    clean_v['Vision'] = dataf['Do you have normal vision and hearing (Y or N)?']
    clean_v['Date'] = dataf['date']
    clean_v['RunType'] = dataf['RunType']
    clean_v['Distractor'] = dataf['Distractor']
    clean_v['Target'] = dataf['Target']
    clean_v['corrAns'] = dataf['corrAns']
    clean_v['arduino_rt'] = dataf['Arduino Response Time (ms)']
    clean_v['CurrTrialType']=dataf['CurrTrialType']
    clean_v['PrevTrialType'] = dataf['PrevTrialType']
    clean_v['CurrAcc'] = dataf['Feedback']
    clean_v['Distractor_onset'] = dataf['Distractor_Onset_Arduino (ms)']
    clean_v['Target_onset'] = dataf['Target_Onset_Arduino (ms)']
    clean_v['Key_press'] = dataf['Arduino Key Press Time (ms)']
    clean_v = clean_v[clean_v['RunType'] == "Test"]
    if "Computer" in dataf.columns:
        clean_v['Computer'] = dataf["Computer"]
    else:
        clean_v['Computer'] = "PSYC-DANWEISS24"
        print("No computer information provided! Automatically use the calibration matrix for PSYC-DANWEISS24, but it is better to add this information to the psychopy file!")
    
    #add previous accuracy
    prev_acc = []
    for i in clean_v.index:
        if clean_v['PrevTrialType'][i] == 'None':
            prev_acc.append('None')
        else:
            prev_acc.append(clean_v['CurrAcc'][i-1])
    clean_v['PrevAcc'] = prev_acc

    clean_v = clean_v[(clean_v["PrevTrialType"]!="Neutral") & (clean_v["CurrTrialType"]!="Neutral")]
    return clean_v


def get_demographics(dataf):
    """
    Extracts demographic info
    
    Parameters:
        dataf (DataFrame): the reduced version of the psychopy data 
    
    Returns:
        reduced dataframe representation of a participant file including basic demographic information
    """
    return dataf.loc[:, ["ExpName", "PsNum", "Age", "Sex", "Vision", "Date"]]


def get_RT(dataf, condition_type, allow_error=False):
    """
    Retrieves RT data of trials based on the condition_type and whether the error in the current trial is allowed
        The previous trial must be correct

    Parameters:
        dataf (DataFrame): the reduced version of the psychopy data 
        condition_type(string): one of [cC, cN, CI, nC, nN, nI, iC, iN, iI]
        allow_error (boolean): True of False. whether the error in the current trial is allowed
    
    Returns:
        RT_df (DataFrame): all the data
        RT_df["arduino_rt"] (Series): only the rt data

    """
    RT_df = pd.DataFrame()

    if allow_error == False: #only consider the trials whose CurrAcc is correct
        RT_df = dataf[(dataf['PrevAcc'] == 'Correct') & (dataf['CurrAcc'] == 'Correct')]
    else: #allows errors in current trial but only includes "Correct" and "Incorrect" current trials
        RT_df = dataf[(dataf['PrevAcc'] == 'Correct') & ((dataf['CurrAcc'] == 'Correct') | (dataf['CurrAcc'] == 'Incorrect'))]
    
    if condition_type == 'cC':
        RT_df = RT_df[(RT_df['PrevTrialType'] == 'Congruent') & (RT_df['CurrTrialType'] == 'Congruent')]
    #elif condition_type == 'cN':
    #    RT_df = RT_df[(RT_df['PrevTrialType'] == 'Congruent') & (RT_df['CurrTrialType'] == 'Neutral')]
    elif condition_type == 'cI':
        RT_df = RT_df[(RT_df['PrevTrialType'] == 'Congruent') & (RT_df['CurrTrialType'] == 'Incongruent')]
    elif condition_type == 'iC':
        RT_df = RT_df[(RT_df['PrevTrialType'] == 'Incongruent') & (RT_df['CurrTrialType'] == 'Congruent')]
    #elif condition_type == 'iN':
    elif condition_type == 'iI':
        RT_df = RT_df[(RT_df['PrevTrialType'] == 'Incongruent') & (RT_df['CurrTrialType'] == 'Incongruent')]

    return RT_df, RT_df["arduino_rt"]


def compute_sn_oneTrial(trial_RT):
    """
    Return the median_list and Computes Sn for the specified trial type.

    Parameters:
        trial_RT (Series): the rt data (only) of one trial
    
    Returns:
        median_list (list): list of all median distance of each trial
        sn (double): the Sn value of one trial type
    """
    trial_RT.index= range(len(trial_RT))
    median_list =[]
    for i in range(len(trial_RT)):
        dist = []
        for ind in range(len(trial_RT)):
            if i!= ind:
                # compute each trial's RT's distance from all other RTs
                dist.append(abs(trial_RT[i] - trial_RT[ind])) 
        median_list.append(st.median(dist)) #select the median

    c=0
    if len(median_list)<10:
        cc = [float('nan'), 0.743, 1.851, 0.954, 1.351, 0.993, 1.198, 1.005, 1.131] # Unsure if this line runs correctly. Run diagnostics!
        c = cc[len(median_list)]
    elif len(median_list)%2 == 1:
        c = len(median_list) / (len(median_list) - 0.9)
    else:
        c = 1
    
    sn = st.median(median_list) * c
    return median_list, sn


def compute_sn_all(dataf, allow_error=False):
    """
    Add new column 'median_distance' for each trial and Computer Sn for each trial type

    Parameters:
        dataf (DataFrame): the reduced version of the psychopy data 
        allow_error (boolean): True of False. whether the error in the current trial is allowed

    Returns:
        dataf (DataFrame): the reduced version of the psychopy data with the column 'median_distance'
        sn_all (Dictionary): the sn of each trial type that specified by allow_error
        sn_all_all (Dictionary)
    """
    sn_all = {}
    sn_all_all = {}
    #cC_ind, cN_ind, cI_ind, nC_ind, nN_ind, nI_ind, iC_ind, iN_ind, iI_ind = 0, 0, 0,0, 0, 0,0, 0, 0
    cC_ind, cI_ind, iC_ind, iI_ind = 0, 0, 0,0
    #cC_ind_all, cN_ind_all, cI_ind_all, nC_ind_all, nN_ind_all, nI_ind_all, iC_ind_all, iN_ind_all, iI_ind_all = 0, 0, 0,0, 0, 0,0, 0, 0
    cC_ind_all, cI_ind_all, iC_ind_all, iI_ind_all = 0, 0, 0,0
    median_dic = {}
    median_dic_all = {}

    for name in ["cC", "cI", "iC", "iI"]:
        _, rt = get_RT(dataf, name, allow_error)
        median_list, sn_all[name] = compute_sn_oneTrial(rt)
        median_dic[name] = median_list

        _, rt_all = get_RT(dataf, name, True)
        median_list_all, sn_all_all[name] = compute_sn_oneTrial(rt_all)
        median_dic_all[name] = median_list_all

    # create the median_distance column
    dataf['median_distance'] = list(np.arange(dataf.shape[0])) #depend on allow_error
    dataf['median_distance_all'] = list(np.arange(dataf.shape[0])) #include both correct & incorrect current trial
    if(allow_error == False): #median_distance, only correct current trials
        for i in dataf.index:
            if ((dataf['PrevAcc'][i] == 'Correct') & (dataf['CurrAcc'][i] == 'Correct')):
                if ((dataf['PrevTrialType'][i] == 'Congruent') & (dataf['CurrTrialType'][i] == 'Congruent')):
                    dataf['median_distance'][i] = median_dic["cC"][cC_ind]
                    cC_ind +=1
                #elif ((dataf['PrevTrialType'][i] == 'Congruent') & (dataf['CurrTrialType'][i] == 'Neutral')):
                #    dataf['median_distance'][i] = median_dic["cN"][cN_ind]
                #    cN_ind +=1
                elif ((dataf['PrevTrialType'][i] == 'Congruent') & (dataf['CurrTrialType'][i] == 'Incongruent')):
                    dataf['median_distance'][i] = median_dic["cI"][cI_ind]
                    cI_ind +=1
                elif ((dataf['PrevTrialType'][i] == 'Incongruent') & (dataf['CurrTrialType'][i] == 'Congruent')):
                    dataf['median_distance'][i] = median_dic["iC"][iC_ind]
                    iC_ind +=1
                elif ((dataf['PrevTrialType'][i] == 'Incongruent') & (dataf['CurrTrialType'][i] == 'Incongruent')):
                    dataf['median_distance'][i] = median_dic["iI"][iI_ind]
                    iI_ind +=1
            else:
                dataf['median_distance'][i] = 'Invalid'
            
            if ((dataf['PrevAcc'][i] == 'Correct') & ((dataf['CurrAcc'][i] == 'Correct') | (dataf['CurrAcc'][i] == 'Incorrect'))):
                if ((dataf['PrevTrialType'][i] == 'Congruent') & (dataf['CurrTrialType'][i] == 'Congruent')):
                    dataf['median_distance_all'][i] = median_dic_all["cC"][cC_ind_all]
                    cC_ind_all +=1
                #elif ((dataf['PrevTrialType'][i] == 'Congruent') & (dataf['CurrTrialType'][i] == 'Neutral')):
                 #   dataf['median_distance_all'][i] = median_dic_all["cN"][cN_ind_all]
                 #   cN_ind_all +=1
                elif ((dataf['PrevTrialType'][i] == 'Congruent') & (dataf['CurrTrialType'][i] == 'Incongruent')):
                    dataf['median_distance_all'][i] = median_dic_all["cI"][cI_ind_all]
                    cI_ind_all +=1
                elif ((dataf['PrevTrialType'][i] == 'Incongruent') & (dataf['CurrTrialType'][i] == 'Congruent')):
                    dataf['median_distance_all'][i] = median_dic_all["iC"][iC_ind_all]
                    iC_ind_all +=1
                elif ((dataf['PrevTrialType'][i] == 'Incongruent') & (dataf['CurrTrialType'][i] == 'Incongruent')):
                    dataf['median_distance_all'][i] = median_dic_all["iI"][iI_ind_all]
                    iI_ind_all +=1
            else:
                dataf['median_distance_all'][i] = 'Invalid'
            

    else: #median_distance == median_distance_all. both correct & incorrect trials
        for i in dataf.index:
            if ((dataf['PrevAcc'][i] == 'Correct') & ((dataf['CurrAcc'][i] == 'Correct') | (dataf['CurrAcc'][i] == 'Incorrect'))):
                if ((dataf['PrevTrialType'][i] == 'Congruent') & (dataf['CurrTrialType'][i] == 'Congruent')):
                    dataf['median_distance'][i] = median_dic["cC"][cC_ind]
                    dataf['median_distance_all'][i] = median_dic["cC"][cC_ind]
                    cC_ind +=1
                elif ((dataf['PrevTrialType'][i] == 'Congruent') & (dataf['CurrTrialType'][i] == 'Incongruent')):
                    dataf['median_distance'][i] = median_dic["cI"][cI_ind]
                    dataf['median_distance_all'][i] = median_dic["cI"][cI_ind]
                    cI_ind +=1
                elif ((dataf['PrevTrialType'][i] == 'Incongruent') & (dataf['CurrTrialType'][i] == 'Congruent')):
                    dataf['median_distance'][i] = median_dic["iC"][iC_ind]
                    dataf['median_distance_all'][i] = median_dic["iC"][iC_ind]
                    iC_ind +=1
                elif ((dataf['PrevTrialType'][i] == 'Incongruent') & (dataf['CurrTrialType'][i] == 'Incongruent')):
                    dataf['median_distance'][i] = median_dic["iI"][iI_ind]
                    dataf['median_distance_all'][i] = median_dic["iI"][iI_ind]
                    iI_ind +=1
            else:
                dataf['median_distance'][i] = 'Invalid'
                dataf['median_distance_all'][i] = 'Invalid'

    return dataf, sn_all, sn_all_all


def identify_outliers(dataf, allow_error=False):
    """
    Label respective trials as 'outlier' based on their RT and Sn

    Parameters:
        dataf (DataFrame): the reduced version of the psychopy data 
        allow_error (boolean): True of False. whether the error in the current trial is allowed

    Returns:
        dataf = with outliers labeled 'outlier'
    """
    dataf, sn_dic, sn_dic_all = compute_sn_all(dataf, allow_error)
    dataf['Outlier'] = list(np.arange(dataf.shape[0]))
    dataf['Outlier_all'] = list(np.arange(dataf.shape[0]))
    for i in dataf.index:
        prev, cur = dataf['PrevTrialType'][i], dataf['CurrTrialType'][i]
        type = f'{prev[:1]}'.lower() + f'{cur[:1]}'.upper()

        #for RT
        if (bool(dataf['median_distance'][i] != "Invalid")):# & bool(dataf['median_distance'][i] != "Wrong_cur")):
            if dataf['median_distance'][i] > 3*sn_dic[type]:
                dataf['Outlier'][i] = True
            else:
                dataf['Outlier'][i] = False
        else:
            dataf['Outlier'][i]= "Invalid"
        
        #for ER
        if (bool(dataf['median_distance_all'][i] != "Invalid")):# & bool(dataf['median_distance'][i] != "Wrong_cur")):
            if dataf['median_distance_all'][i] > 3*sn_dic_all[type]:
                dataf['Outlier_all'][i] = True
            else:
                dataf['Outlier_all'][i] = False
        else:
            dataf['Outlier_all'][i]= "Invalid"

    return dataf


def get_means(dataf, allow_error = False):
    """
    Return the mean RT of each trial type

    Parameters:
        dataf (DataFrame): the reduced version of the psychopy data, either with 'Outlier' or not 
        allow_error (boolean): True of False. whether the error in the current trial is allowed

    Returns:
        means (dictionary): a dictionary whose keys are trial types and 
                whose values are the means of that trial type's RTs
    """
    mean_dict = {}
    clear_data = dataf[dataf["Outlier"]!=True]
    for name in ["cC", "cI", "iC", "iI"]:
        _, rt = get_RT(clear_data, name, allow_error)
        mean_dict[name] = rt.mean()
    return mean_dict


def get_error_rate(dataf):
    """
    Return the error rate of each trial type
        for error rate, we will exclude outliers. Here, outliers are determined only 
        based on trials when CurrAcc

    Parameters:
        dataf (DataFrame): the reduced version of the psychopy data, 'Outlier' required

    Returns:
        er_ra (dictionary): the dictionary that key == trial type and item == corresponding error rate
    """
    er_ra = {}
    num_correct = {"cC":0, "cI":0, "iC":0, "iI":0}
    total = {"cC":0, "cI":0,  "iC":0, "iI":0}
    for i in dataf.index:
        if((dataf['Outlier_all'][i] != True) and ((dataf['CurrAcc'][i]=="Correct") or (dataf['CurrAcc'][i]=="Incorrect")) 
                    and (dataf['PrevTrialType'][i]!="None") and (dataf["PrevAcc"][i]=="Correct")):
            prev, cur = dataf['PrevTrialType'][i], dataf['CurrTrialType'][i]
            type = f'{prev[:1]}'.lower() + f'{cur[:1]}'.upper()
            total[type] +=1
            if dataf['CurrAcc'][i] == "Correct":
                num_correct[type] +=1

    for typ in num_correct.keys():
        #print(num_correct[typ], total[typ])
        er_ra[typ] = round(1- num_correct[typ] /total[typ], 6)
    
    print(total, "total number")
    print(num_correct, "num_correct")

    return er_ra


def get_overall_accuracy(dataf):
    """
    Return the overall accuracy of one participant

    Parameters:
        dataf (DataFrame): the reduced version of the psychopy data, 'Outlier' required

    Returns:
        acc (float): the overall accuracy
    """
    num_correct = 0
    total = 0
    for i in dataf.index:
        total +=1
        if dataf['CurrAcc'][i] == "Correct":
            num_correct +=1
    return round(num_correct/total, 6)


def get_total_percent_outliers(dataf):
    """
    Return the total percent of outliers

    Parameters:
        dataf (DataFrame): the reduced version of the psychopy data, 'Outlier' required

    Returns:
        out_per (float): the overall proportion of outliers
    """
    total = 0
    outl = 0
    for i in dataf.index:
        total +=1
        if dataf['Outlier'][i] == True:
            outl +=1
    return round(outl / total, 6)