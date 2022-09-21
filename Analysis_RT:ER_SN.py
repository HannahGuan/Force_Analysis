#Analysis Script

import csv
import json
import statistics
import os
import numpy as np

NONE_VALUES = ('', 'n/a', 'none', 'unknown')

def read_csv_to_dicts(filepath, encoding='utf-8', newline='', delimiter=','):
    """Accepts a file path, creates a file object, and returns a list of dictionaries that
    represent the row values using the cvs.DictReader().

    Parameters:
        filepath (str): path to file
        encoding (str): name of encoding used to decode the file
        newline (str): specifies replacement value for newline '\n'
                       or '\r\n' (Windows) character sequences
        delimiter (str): delimiter that separates the row values

    Returns:
        list: nested dictionaries representing the file contents
     """

    # with open(filepath, 'r', newline=newline, encoding=encoding) as file_obj:
    #     reader = csv.DictReader(file_obj, delimiter=delimiter, dialect='excel')
    #     return [line for line in reader]

    with open(filepath, 'r', newline=newline, encoding=encoding) as file_obj:
        reader = csv.DictReader(file_obj, delimiter=delimiter, dialect='excel')

        clean_list = []
        for line in reader:
            for key in line.keys():
                clean_key = ''.join(filter(str.isalnum, key))
                key = clean_key
            clean_list.append(line)

        return clean_list

def write_dicts_to_csv(filepath, data, fieldnames, encoding='utf-8', newline=''):
    """
    Writes dictionary data to a target CSV file as row data using the csv.DictWriter().
    The passed in fieldnames list is used by the DictWriter() to determine the order
    in which each dictionary's key-value pairs are written to the row.

    Parameters:
        filepath (str): path to target file (if file does not exist it will be created)
        data (list): dictionary content to be written to the target file
        fieldnames (seq): sequence specifing order in which key-value pairs are written to each row
        encoding (str): name of encoding used to encode the file
        newline (str): specifies replacement value for newline '\n'
                       or '\r\n' (Windows) character sequences

    Returns:
        None
    """

    with open(filepath, 'w', encoding=encoding, newline=newline) as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=fieldnames)

        writer.writeheader() # first row
        writer.writerows(data)
        # for row in data:
        #     writer.writerow(row)

def read_json(filepath, encoding='utf-8'):
    """Reads a JSON document, decodes the file content, and returns a list or dictionary if
    provided with a valid filepath.

    Parameters:
        filepath (str): path to file
        encoding (str): name of encoding used to decode the file

    Returns:
        dict/list: dict or list representations of the decoded JSON document
    """

    with open(filepath, 'r', encoding=encoding) as file_obj:
        return json.load(file_obj)

def write_json(filepath, data, encoding='utf-8', ensure_ascii=False, indent=2):
    """Serializes object as JSON. Writes content to the provided filepath.

    Parameters:
        filepath (str): the path to the file
        data (dict)/(list): the data to be encoded as JSON and written to the file
        encoding (str): name of encoding used to encode the file
        ensure_ascii (str): if False non-ASCII characters are printed as is; otherwise
                            non-ASCII characters are escaped.
        indent (int): number of "pretty printed" indention spaces applied to encoded JSON

    Returns:
        None
    """

    with open(filepath, 'w', encoding=encoding) as file_obj:
        json.dump(data, file_obj, ensure_ascii=ensure_ascii, indent=indent)

def convert_to_float(value):
    """Attempts to convert the passed in < value > to a float in the try block.

    If an exception is encountered the < value > is passed to < convert_to_none > in an attempt
    to convert the < value > to None if the < value > matches a < NONE_VALUES > item. The return
    value of < convert_to_none > is then returned to the caller.

    Note that a boolean value passed to the function will be converted to a float (e.g., True
    converted to 1.0; False converted to 0.0).

    Parameters:
        value (obj): string or number to be converted

    Returns:
        obj: float if converted to number; None if value in < NONE_VALUES >; otherwise returns
             value unchanged
    """

    try:
        return float(value)
    except:
        none = convert_to_none(value)
        return none

def convert_to_none(value):
    """Attempts to convert the passed in < value > to < None > in the try block if the < value >
    matches any of the strings in the constant < NONE_VALUES >. Leading or trailing spaces are
    removed from the < value > before a case-insensitive comparison is performed between the
    < value > and the < NONE_VALUES > items. If a match is obtained None is returned; otherwise
    the < value > is returned unchanged.

    If a runtime exception is encountered in the except block the < value > is also returned
    unchanged.

    Parameters:
        value (obj): string or number to be converted

    Returns:
        None: if value successfully converted; otherwise returns value unchanged
    """


    try:
        mod_val = value.strip().lower()
        if mod_val in NONE_VALUES:
            return None
        else:
            return value
    except:
        return value

def reduce_data(file):
    """"Reduces the overall data set to columns of interest. Attempts to remove rows without applicable data (conditioned on not having a distractor)

    Parameters:

    file (list): A list of dictionaries each representing a row in a single subject's data file

    returns:

    file (list): A reduced list of dictionaries, including only information pertinent to following analyses
    """

    list = []
    for line in file:
        if line['\ufeffRunType'] == "Test":
            dict = {
                'ExpName': line['expName'],
                'PsNum': line['participant'],
                'Age': convert_to_float(line['How old are you (in years)?']),
                'Sex': line['Are you male or female (M or F)?'],
                'Vision': line['Do you have normal vision and hearing (Y or N)?'],
                'Date': line['date'],
                'RunType': line['\ufeffRunType'], #keyword error without \ufeff
                'Distractor': line['Distractor'],
                'Target': line['Target'],
                'corrAns': line['corrAns'],
                'key_resp_rt': convert_to_float(line['key_resp.rt']),
                'CurrTrialType': line['CurrTrialType'],
                'PrevTrialType': line['PrevTrialType'],
                'CurrAcc': line['Feedback']
                }
            list.append(dict)
    return list

def get_demographics(file):
        """Extracts demographic info from a dictionary representation of a participant file

        Parameters:
            file (dict): dictionary representation of a participant file

        Returns:
            demo_dict (dict): reduced dictionary representation of a participant file including basic demographic information
        """

        demo_dict = {
        'ExpName': file[0]['expName'],
        'PsNum': file[0]['participant'],
        'Age': file[0]['How old are you (in years)?'],
        'Sex': file[0]['Are you male or female (M or F)?'],
        'Vision': file[0]['Do you have normal vision and hearing (Y or N)?'],
        'Date': file[0]['date']
        }
        return demo_dict

def add_previous_accuracy(file):
    """Adds the previous trial's accuracy to each row entry within a dictionary representation of a participant data file.

    Parameters:
        file (dict): dictionary representation of a participant file

    Returns:
        file (dict): updated dictionary representation of a participant file including each trial's previous accuracy
    """

    n = 0
    for line in file:
        if line['PrevTrialType'] == 'None':
            prev_acc = 'None'
        else:
            prev_acc = file[n-1]['CurrAcc']
        line['PrevAcc'] = prev_acc
        n += 1

    return file

def get_RT(file, current_errors=False):
    """Retrieves RT data from a dictionary representation of a participant file. Sorts RT data into lists according to trial type.

    Parameters:
        file (dict): dictionary representation of a participant file
        current_errors: False returns RTs from trials with correct previous AND current accuracy (for mean RT calculations); True returns RTs from trials with correct previous accuracy (for accuracy outlier calculations)

    Returns:
        outliers_RT (dict): a dictionary including a participant's RT in each trial sorted by trial type (i.e., trial n-1 sequence)
    """

    cC_RT = []
    cN_RT = []
    cI_RT = []
    nC_RT = []
    nN_RT = []
    nI_RT = []
    iC_RT = []
    iN_RT = []
    iI_RT = []

    for line in file:
        if current_errors == False:

            if line['PrevAcc'] == 'Correct' and line['CurrAcc'] == 'Correct':

                if line['PrevTrialType'] == 'Congruent' and line['CurrTrialType'] == 'Congruent':
                    cC_RT.append(line['key_resp_rt'])
                elif line['PrevTrialType'] == 'Congruent' and line['CurrTrialType'] == 'Neutral':
                    cN_RT.append(line['key_resp_rt'])
                elif line['PrevTrialType'] == 'Congruent' and line['CurrTrialType'] == 'Incongruent':
                    cI_RT.append(line['key_resp_rt'])

                elif line['PrevTrialType'] == 'Neutral' and line['CurrTrialType'] == 'Congruent':
                    nC_RT.append(line['key_resp_rt'])
                elif line['PrevTrialType'] == 'Neutral' and line['CurrTrialType'] == 'Neutral':
                    nN_RT.append(line['key_resp_rt'])
                elif line['PrevTrialType'] == 'Neutral' and line['CurrTrialType'] == 'Incongruent':
                    nI_RT.append(line['key_resp_rt'])

                elif line['PrevTrialType'] == 'Incongruent' and line['CurrTrialType'] == 'Congruent':
                    iC_RT.append(line['key_resp_rt'])
                elif line['PrevTrialType'] == 'Incongruent' and line['CurrTrialType'] == 'Neutral':
                    iN_RT.append(line['key_resp_rt'])
                elif line['PrevTrialType'] == 'Incongruent' and line['CurrTrialType'] == 'Incongruent':
                    iI_RT.append(line['key_resp_rt'])


        elif current_errors == True: # Allows errors in current trial but only includes "Correct" and "Incorrect" current trials

            ER_responses = ('Correct', 'Incorrect')

            if line['PrevAcc'] == 'Correct' and line['CurrAcc'] in ER_responses: # ... and (line['CurrAcc'] == 'Correct' or line['CurrAcc'] == 'Incorrect')

                if line['PrevTrialType'] == 'Congruent' and line['CurrTrialType'] == 'Congruent':
                    cC_RT.append((line['CurrAcc'], line['key_resp_rt']))
                elif line['PrevTrialType'] == 'Congruent' and line['CurrTrialType'] == 'Neutral':
                    cN_RT.append((line['CurrAcc'], line['key_resp_rt']))
                elif line['PrevTrialType'] == 'Congruent' and line['CurrTrialType'] == 'Incongruent':
                    cI_RT.append((line['CurrAcc'], line['key_resp_rt']))

                elif line['PrevTrialType'] == 'Neutral' and line['CurrTrialType'] == 'Congruent':
                    nC_RT.append((line['CurrAcc'], line['key_resp_rt']))
                elif line['PrevTrialType'] == 'Neutral' and line['CurrTrialType'] == 'Neutral':
                    nN_RT.append((line['CurrAcc'], line['key_resp_rt']))
                elif line['PrevTrialType'] == 'Neutral' and line['CurrTrialType'] == 'Incongruent':
                    nI_RT.append((line['CurrAcc'], line['key_resp_rt']))

                elif line['PrevTrialType'] == 'Incongruent' and line['CurrTrialType'] == 'Congruent':
                    iC_RT.append((line['CurrAcc'], line['key_resp_rt']))
                elif line['PrevTrialType'] == 'Incongruent' and line['CurrTrialType'] == 'Neutral':
                    iN_RT.append((line['CurrAcc'], line['key_resp_rt']))
                elif line['PrevTrialType'] == 'Incongruent' and line['CurrTrialType'] == 'Incongruent':
                    iI_RT.append((line['CurrAcc'], line['key_resp_rt']))


    outliers_RT = {
        "cC_RT": cC_RT,
        'cN_RT': cN_RT,
        'cI_RT': cI_RT,
        'nC_RT': nC_RT,
        'nN_RT': nN_RT,
        'nI_RT': nI_RT,
        'iC_RT': iC_RT,
        'iN_RT': iN_RT,
        'iI_RT': iI_RT
    }

    return outliers_RT

def others_list(list, current_trial):

    next_trial = current_trial + 1

    others_list = []

    for previous_other in list[:current_trial]:
        others_list.append(previous_other)

    for next_other in list[next_trial:]:
        others_list.append(next_other)

    return others_list

def medians_sn(data):
    """First computes the median of the set of each RT's distance from all other RTs within a trial type. Then creates a set of each trial's median distance from all other RTs within a trial type.

    Parameters:
        data (dict): a dictionary representation of a participant's RT data sorted by trial type.

    Returns:
        medians (dict): a dictionary of each trial type's RTs' median distance from all other RTs within their respective trial type. To be used when computing sn.
    """

    current_trial = 0
    medians = {}

    for trial_type, list, in data.items():
        trial_type_medians = []
        for trial in list:
            diff_list = []
            other_list = others_list(list, current_trial)

            for other in other_list:

                try:
                    trial_RT = trial[1] # for accuracy RT nested in tuple
                    other_RT = other[1]
                except:
                    trial_RT = trial
                    other_RT = other

                diff = abs(trial_RT - other_RT)
                diff_list.append(diff)

            trial_median = statistics.median(diff_list)
            trial_type_medians.append(trial_median)
            current_trial += 1


        medians[f'{trial_type[:2]}_med'] = trial_type_medians
        current_trial = 0

    return medians

def compute_sn(medians_lists):
    """Computes Sn for each trial type.

    Parameters:
        medians_lists (dict): a dictionary of each trial type's RTs' median distance from all other RTs within their respective trial type (i.e., the output of the 'medians_sn' function)

    Returns:
        sn_dict (dict): a dictionary of each trial type's Sn value.
    """

    sn_dict = {}

    for trial_type, list in medians_lists.items():
        n = len(list)

        if n < 10:
            cc = [float('nan'), 0.743, 1.851, 0.954, 1.351, 0.993, 1.198, 1.005, 1.131] # Unsure if this line runs correctly. Run diagnostics!
            c = cc[n]

        elif n % 2 == 1:
            c = n/(n - 0.9)

        else:
            c = 1

        sn = statistics.median(list) * c
        sn_dict[f'{trial_type[:2]}_sn'] = sn

    return sn_dict

def identify_outliers_sn(medians, sn_dict):
    """Labels any value above 3 * Sn 'outlier'

    Parameters:
    medians (dict): a dictionary of each trial type's RTs' median distance from all other RTs within their respective trial type (i.e., the output of the 'medians_sn' function)
    sn (dict): a dictionary of each trial type's Sn value (i.e., the output of the 'compute_sn' function)

    Returns:
    outlier_ID_medians (dict): an updated median dictionary with outlier values labeled 'outlier'
    """

    outlier_ID_sn = {}

    for trial_type, list in medians.items():
        new_list = []
        sn = sn_dict[f'{trial_type[:2]}_sn']
        for median in list:
            if median > 3 * sn:
                median = 'outlier'
            new_list.append(median)
        outlier_ID_sn[trial_type] = new_list

    return outlier_ID_sn

def identify_outliers(data, outlier_ID_sn):
    """Uses the outlier labels from the list output of 'identify_outliers_median' to label respective RT's in the RT dictionary as 'outlier'

    Parameters:
    data (dict): RT data sorted by trial type
    outlier_ID_sn (dict): medians labeled 'outlier' if greater than 3 * sn

    Returns:
    no_outliers_RT (dict): a dictioanry of RT by trial type with outliers labeled 'outlier'
    """

    no_outliers = {}

    data_keys = []
    for key in data.keys():
        data_keys.append(key)
        break
    suffix = data_keys[0][2:]

    for trial_type, list in outlier_ID_sn.items():
        n = 0
        for trial in list:
            if trial == 'outlier':
                data[f'{trial_type[:2]}{suffix}'][n] = 'outlier'
                # OG line: data[trial_type][n] = 'outlier'; v2: data[f'{trial_type[:2]}_RT'][n] = 'outlier'
            n += 1

        no_outliers[f'{trial_type[:2]}{suffix}'] = data[f'{trial_type[:2]}{suffix}']
        # OG line: no_outliers[trial_type] = data[trial_type]; v2: no_outliers[f'{trial_type[:2]}_RT'] = data[f'{trial_type[:2]}_RT']

    return no_outliers


#def identify_outliers_RT(data, outlier_IDs):

    no_outliers = {}

    for trial_type, list in outlier_IDs.items():
        n = 0
        for trial in list:
            if trial == 'outlier':
                data[trial_type][n] = 'outlier'
            n += 1

        no_outliers[trial_type] = data[trial_type]

    return no_outliers

def get_means(data):
    """"Converts lists of RT/Accuracy by trial type into their mean

    Parameters:
    data (dictionary): a dictionary whose keys are trial types and whose values are lists of that trial type's RTs
    """

    means = {}

    for trial_type, list in data.items():
        no_outliers = []
        for trial in list:
            if trial != 'outlier':
                no_outliers.append(trial)
        mean = round(statistics.mean(no_outliers), 6)
        means[trial_type] = mean

    return means

def get_error_rate(acc_data):

    error_rate = {}

    for trial_type, list in acc_data.items():

        prefix = trial_type[:2]

        num_correct = 0
        total = 0

        for trial in list:
            if trial != "outlier":
                total += 1
                if trial[0] == "Correct":
                    num_correct += 1

        accuracy = num_correct/total
        ER = round(1 - accuracy, 6)

        error_rate[f'{prefix}_ER'] = ER

    return error_rate

def get_overall_accuracy(all_data):

    total = 0
    correct = 0

    for trial in all_data:
        total += 1
        if trial['CurrAcc'] == "Correct":
            correct += 1

    accuracy = round(correct/total, 6)
    return accuracy

def get_total_percent_outliers(file, data):

    total = len(file)
    outliers = 0


    for list in data.values():
        for trial in list:
            if trial == "outlier":
                outliers += 1

    percent_outliers = round(outliers/total, 6)

    return percent_outliers

def main():
    """Entry point for program.

    Parameters:
        None

    Returns:
        None
    """
    # TESTING (single subject)
    filepath = '/Users/Matthew/Dropbox (University of Michigan)/Experiments_ACC_LAB/2021_2022/Matt/Neutral/Analysis_Script/Working/Exp2_Logfiles/10_Prime-Probe_2022_Jan_26_1658.csv'

    # # Read Participant Data File
    sub = read_csv_to_dicts(filepath)
    write_json('../1_sub.json', sub)

    # # Reduce Data to Needed Info
    clean_sub = reduce_data(sub)
    write_json('../2_clean_sub.json', clean_sub)

    # # Add Previous Accuracy Data
    prev_acc = add_previous_accuracy(clean_sub)
    write_json('../3_prev_acc.json', prev_acc)



    # # Retrieve Data

    # # # RT Data by Trial Type (Previous and Current Trials are 'Correct')
    outliers_RT = get_RT(prev_acc)
    write_json('../4_outliers_RT.json', outliers_RT)
    print(f"\niI_RT n = {len(outliers_RT['iI_RT'])}")

    # # # Accuracy RT Data by Trial Type (Previous Trials are 'Correct')
    outliers_acc_RT = get_RT(prev_acc, current_errors=True)
    write_json('../5_outliers_accuracy_RT.json', outliers_acc_RT)
    print(f"\ncC_acc n = {len(outliers_acc_RT['cC_RT'])}")

    # # # Accuracy data (binary)
    # outliers_acc = get_accuracy(prev_acc)
    # write_json('../6_outliers_acc')



    # # Identify RT Outliers (flag as "outlier" if > 3*Sn)

    # # # Get RT Median Distance
    medians_RT = medians_sn(outliers_RT)
    write_json('../6_medians_RT.json', medians_RT)

    # # # Compute RT Sn
    sn_RT = compute_sn(medians_RT)
    write_json('../7_sn_RT.json', sn_RT)

    # # # Label RT Median Distance Outliers (> 3*Sn)
    outliers_ID_median_RT = identify_outliers_sn(medians_RT, sn_RT)
    write_json('../8_outliers_ID_median_RT.json', outliers_ID_median_RT)

    # # # Label RT Outliers (by Crossreferencing Median Distance Lists)
    outliers_ID_RT = identify_outliers(outliers_RT, outliers_ID_median_RT)
    write_json('../9_outliers_ID_RT.json', outliers_ID_RT)



    # # Identify Accuracy Outliers

    # # # Get Accuracy Median Distance
    medians_acc_RT = medians_sn(outliers_acc_RT)
    write_json('../10_medians_acc_RT.json', medians_acc_RT)

    # # # Compute Accuracy RT Sn
    sn_acc_RT = compute_sn(medians_acc_RT)
    write_json('../11_sn_acc_RT.json', sn_acc_RT)

    # # # Label Accuracy Median Distance Outliers (> 3*Sn)
    outliers_ID_med_acc_RT = identify_outliers_sn(medians_acc_RT, sn_acc_RT)
    write_json('../12_outliers_ID_med_acc_RT.json', outliers_ID_med_acc_RT)

    # # # Label RT Outliers (by Crossreferencing Median Distance Lists)
    outliers_ID_acc_RT = identify_outliers(outliers_acc_RT, outliers_ID_med_acc_RT)
    write_json('../13_outliers_ID_acc_RT.json', outliers_ID_acc_RT)


    # # Compute Stuff

    # # # Mean RT (Filters out Trials Labeled "outlier")

    no_outliers_mean_RT = get_means(outliers_ID_RT)
    write_json('../14_no_outliers_mean_RT.json', no_outliers_mean_RT)

    # # # Error Rate

    no_outliers_ER = get_error_rate(outliers_ID_acc_RT)
    write_json('../15_no_outliers_ER.json', no_outliers_ER)

    # # # Overall Accuracy

    overall_accuracy = get_overall_accuracy(prev_acc)
    print(f'\nOverall Accuracy = {overall_accuracy}')

    # # # Overall % Outliers

    overall_outliers = get_total_percent_outliers(prev_acc, outliers_ID_RT)
    print(f'\nOverall % Outliers = {overall_outliers}')




    # THE LOOP

    # # Which Experiment?
    exp = '1'

    # Create File List
    logfile_names = os.listdir(f'../EXP{exp}_Logfiles')
    logfile_names.sort()
    print(f"\nlogfile_names = \n{logfile_names}\n")

    number_of_files = len(logfile_names)
    print(f'\nnumber_of_files = {number_of_files}\n')

    data = []
    for name in logfile_names:
        sub = read_csv_to_dicts(f'../EXP{exp}_Logfiles/{name}')

        # Reduce Data/Add Previous Accuracy
        clean_sub = reduce_data(sub)
        prev_acc = add_previous_accuracy(clean_sub)


        # Get RT
        outliers_RT = get_RT(prev_acc)

        # Identify RT Outliers RT (> 3 * Sn)
        medians_RT = medians_sn(outliers_RT)
        sn_RT = compute_sn(medians_RT)
        outliers_ID_median_RT = identify_outliers_sn(medians_RT, sn_RT)
        outliers_ID_RT = identify_outliers(outliers_RT, outliers_ID_median_RT)

        # Compute Mean RT (see get_means function for outlier exclusion conditional)
        no_outliers_mean_RT = get_means(outliers_RT)



        # Get Accuracy RT
        outliers_acc_RT = get_RT(prev_acc, current_errors=True)

        # Identify Accuracy Outliers
        medians_acc_RT = medians_sn(outliers_acc_RT)
        sn_acc_RT = compute_sn(medians_acc_RT)
        outliers_ID_med_acc_RT = identify_outliers_sn(medians_acc_RT, sn_acc_RT)
        outliers_ID_acc_RT = identify_outliers(outliers_acc_RT, outliers_ID_med_acc_RT)

        # Get Error Rate
        no_outliers_ER = get_error_rate(outliers_ID_acc_RT)

        # Get Overall Accuracy
        overall_accuracy = get_overall_accuracy(prev_acc)

        # Get Overall % Outliers
        overall_outliers = get_total_percent_outliers(prev_acc, outliers_ID_RT)

        demo = get_demographics(sub)
        demo.update(no_outliers_mean_RT)
        demo.update(no_outliers_ER)
        demo['Overall_Accuracy'] = overall_accuracy
        demo['Total_Percent_Outliers'] = overall_outliers

        data.append(demo)

    ## Create CSV
    fieldnames = data[0].keys()
    write_dicts_to_csv(f'../data_exp{exp}.csv', data, fieldnames)


    # Format Matlab Output File for Comparison
    matlab_exp = read_csv_to_dicts(f'/Users/Matthew/Dropbox (University of Michigan)/Experiments_ACC_LAB/2021_2022/Matt/Neutral/Analysis_Script/Working/matlab_data/EXP{exp}_All_Data.csv')

    stripped_matlab_exp = []
    for line in matlab_exp:
        stripped_line = {}
        for key, val in line.items():

            if val == '0': # Matlab doesn't do 0.0 but Python does...
                mod_val = '0.0'
            else:
                mod_val = val

            stripped_key = key.strip()
            stripped_line[stripped_key] = mod_val.strip()
        stripped_matlab_exp.append(stripped_line)

    fieldnames = stripped_matlab_exp[0].keys()

    write_dicts_to_csv(f"../matlab_exp{exp}.csv", stripped_matlab_exp, fieldnames)


if __name__ == '__main__':
    main()