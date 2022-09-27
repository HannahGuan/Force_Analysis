import numpy as np
import pandas as pd

"""
    [Functions Review]

    psypy_reduce(dataf): Reduce the PsychoPy dataset to columns of interest & Adds the previous trial's accuracy

    get_demographics(dataf): Extracts demographic info

    get_RT(dataf, condition_type, allow_error=False): Retrive the RT data based on the condition 
                type and whether the current trial should be correct

    medians_sn(dataf): 

    compute_sn(medians_lists):

    identify_outliers(dataf):

    get_means(dataf):

    get_error_rate(dataf):

    get_overall_accuracy(data):

    get_total_percent_outliers():
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
    clean_v["ExpName"] = dataf['expName']
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
    clean_v = clean_v[clean_v['RunType'] == "Test"]
    
    #add previous accuracy
    prev_acc = []
    for i in clean_v.index:
        if clean_v['PrevTrialType'][i] == 'None':
            prev_acc.append('None')
        else:
            prev_acc.append(clean_v['CurrAcc'][i-1])
    clean_v['PrevAcc'] = prev_acc

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
    elif condition_type == 'cN':
        RT_df = RT_df[(RT_df['PrevTrialType'] == 'Congruent') & (RT_df['CurrTrialType'] == 'Neutral')]
    elif condition_type == 'cI':
        RT_df = RT_df[(RT_df['PrevTrialType'] == 'Congruent') & (RT_df['CurrTrialType'] == 'Incongruent')]
    elif condition_type == 'nC':
        RT_df = RT_df[(RT_df['PrevTrialType'] == 'Neutral') & (RT_df['CurrTrialType'] == 'Congruent')]
    elif condition_type == 'nN':
        RT_df = RT_df[(RT_df['PrevTrialType'] == 'Neutral') & (RT_df['CurrTrialType'] == 'Neutral')]
    elif condition_type == 'nI':
        RT_df = RT_df[(RT_df['PrevTrialType'] == 'Neutral') & (RT_df['CurrTrialType'] == 'Incongruent')]
    elif condition_type == 'iC':
        RT_df = RT_df[(RT_df['PrevTrialType'] == 'Incongruent') & (RT_df['CurrTrialType'] == 'Congruent')]
    elif condition_type == 'iN':
        RT_df = RT_df[(RT_df['PrevTrialType'] == 'Incongruent') & (RT_df['CurrTrialType'] == 'Neutral')]
    elif condition_type == 'iI':
        RT_df = RT_df[(RT_df['PrevTrialType'] == 'Incongruent') & (RT_df['CurrTrialType'] == 'Incongruent')]

    return RT_df, RT_df["arduino_rt"]
