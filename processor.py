import numpy as np
import pandas as pd


def psypy_reduce(dataf):
    """
    Reduce the PsychoPy dataset to columns of interest. Attempts to 
        remove rows without applicable data (conditioned on not having a distractor)
    
    Parameters:
    dataf (pandas DataFrame): the psychopy data read from the csv file

    Returns:
    clean_v (pandas DataFrame): the reduced DataFrame
    """
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
    clean_v['key_resp_rt'] = dataf['key_resp.rt']
    clean_v['CurrTrialType']=dataf['CurrTrialType']
    clean_v['PrevTrialType'] = dataf['PrevTrialType']
    clean_v['CurrAcc'] = dataf['Feedback']
    clean_v = clean_v[clean_v['\ufeffRunType'] == "Test"]
    return clean_v