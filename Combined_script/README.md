# Intro to Python version of Force-sensitive Keyboard Experiment Data Analysis Script

----

*November, 2023*

*By Hannah Guan; rjguan@umich.edu*

**Objectives**: To convert the force data and create the force curves based on the onsets of prime and probe

**Contents**: Necessary: processor.py & force_analyzer.py. 

Analysis example: analysis_driver.ipynb

# How to use it: Input & Output

Input: psychopy data in the folder "Data" (just example; could self define), force data in the folder "Forcefiles" (could self define). The two folders should be in the same directory as the code files mentioned above

Requirement: the files should start with the subject number

Output: stored in the folder 'Converted_force' and "Figures". 


# To run analysis on all files in the selected folder
Import processor.py & force_analyzer.py (as fa)

Option 1. call fa.folder_select() <--automatically run analysis on all files in folder "Data" and "Forcefiles"

Option 2. call fa.folder_select(psych_folder, force_folder) <--run analysis on all files in the selected folders

In this process, there might be some warning message. Please ignore it 

# To run analysis on selected files

Import processor.py & force_analyzer.py (as fa)

call fa.multiple_files_select([] (a list of psychopy file names), [] (a list of force file names), name (example, "test2")) 

Requirement: 1. psychopy data in the folder "Data", force data in the folder "Forcefiles" 2. the names should be in accordance and in order

In this process, there might be some warning message. Please ignore it
