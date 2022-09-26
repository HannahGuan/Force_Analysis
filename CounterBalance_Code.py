x = 1 #placeholder
NameOfFile = str(int(expInfo['participant'])) + '_Conditions_Test1.csv'
NameOfBlock = 'Test'

if x == 1:

    nTrials = 72
    nTestTrials = 72
    nTrialTypes = 3
    nUniqueStimuli = 12
    nTrialsPerRun = nTrials
    nStimsPerBlock = nTrialsPerRun

    #initialize variables
    nTrialsPerBlock = int(nTrials)
    nBlocks = int(nTrials / nTrialsPerBlock)

    #Allows us to start over if the program gets stuck
    repeatvar = 1

    #Sequence =[];

    for thisBlock in range(0, nBlocks):
        
        while repeatvar == 1:

            #First, we define an n by n matrix, where n=# of trial types to be randomized.
            #Each number in the matrix indicates how many times each trial type is to be followed and preceded by every trial type in the design.
            matrix = np.array(((int((nTrialsPerBlock / (nTrialTypes * nTrialTypes) / 2)) * np.ones([nTrialTypes, nTrialTypes], dtype = int)),(int((nTrialsPerBlock / (nTrialTypes * nTrialTypes) / 2)) * np.ones([nTrialTypes, nTrialTypes], dtype = int)) ))

            repeatvar = 0

            #Calculate first trial. Trial starts at point 0 (vs 1 in MATLAB)
            a = int(np.floor(np.random.random() * nTrialTypes))

            #OK- let's pretend that the first trial really did follow another trial type.
            #Randomly pick the previous trial type.
            prev_trial_type = int(np.floor(np.random.random() * nTrialTypes))

            #Also, since this is the first trial (i.e., trial 1), it's odd. Odd = 0, Even = 1 for python
            current_odd_even = 0
    
            #Decrement the appropropriate counter
            matrix[current_odd_even, prev_trial_type,a] = matrix[current_odd_even, prev_trial_type,a] - 1

            #create a counter for the a variable. Will try to "append" the post value to this list
            b = [a]

            #Create the rest of the trial sequence
            for counter in range(0, nTrialsPerBlock-1):

                if counter % 2:
                    current_odd_even = 0#odd-numbered trial
        
                else:
                    current_odd_even = 1#even-numbered trial

                post = int(np.floor(np.random.random() * nTrialTypes))
    
                #check sum across the third dimension ("prev trial") to see if there are any remaining positions.
                if np.sum(matrix[current_odd_even, :,b[counter]]) == 0:

                    print('WE HAVE TO REPEAT BECAUSE WE GOT STUCK!')
                    counter=nTrials-1
                    repeatvar=1
                    break
            
                else:

                    while matrix[current_odd_even,post, b[counter]] == 0:
                        post = int(np.floor(np.random.random() * nTrialTypes))
                    
                matrix[current_odd_even, post, b[counter]] = matrix[current_odd_even, post, b[counter]]- 1
                b.append(post)
                
    TrialSequence = b

    OddCongTrials = np.concatenate([1 * np.ones([int((nTrialsPerRun / nUniqueStimuli))], dtype = int), 2 * 1 * np.ones([int((nTrialsPerRun / nUniqueStimuli))], dtype = int)])
    np.random.shuffle(OddCongTrials)

    EvenCongTrials = np.concatenate([3 * np.ones([int((nTrialsPerRun / nUniqueStimuli))], dtype = int), 4 * 1 * np.ones([int((nTrialsPerRun / nUniqueStimuli))], dtype = int)])
    np.random.shuffle(EvenCongTrials)

    OddIncongTrials = np.concatenate([5 * np.ones([int((nTrialsPerRun / nUniqueStimuli))], dtype = int), 6 * 1 * np.ones([int((nTrialsPerRun / nUniqueStimuli))], dtype = int)])
    np.random.shuffle(OddIncongTrials)

    EvenIncongTrials = np.concatenate([7 * np.ones([int((nTrialsPerRun / nUniqueStimuli))], dtype = int), 8 * 1 * np.ones([int((nTrialsPerRun / nUniqueStimuli))], dtype = int)])
    np.random.shuffle(EvenIncongTrials)
    
    OddNeutTrials = np.concatenate([9 * np.ones([int((nTrialsPerRun / nUniqueStimuli))], dtype = int), 10 * 1 * np.ones([int((nTrialsPerRun / nUniqueStimuli))], dtype = int)])
    np.random.shuffle(OddNeutTrials)

    EvenNeutTrials = np.concatenate([11 * np.ones([int((nTrialsPerRun / nUniqueStimuli))], dtype = int), 12 * 1 * np.ones([int((nTrialsPerRun / nUniqueStimuli))], dtype = int)])
    np.random.shuffle(EvenNeutTrials)


    StimulusSequence = 10 * np.ones(nTrialsPerRun, dtype = int)

    for ThisTrial in range(0,nTrialsPerRun):

        if (ThisTrial) % 2:

            if TrialSequence[ThisTrial] == 0:

                StimulusSequence[ThisTrial] = OddCongTrials[0]

                OddCongTrials = OddCongTrials[1:]


            elif TrialSequence[ThisTrial] == 1:

                StimulusSequence[ThisTrial] = OddIncongTrials[0]

                OddIncongTrials = OddIncongTrials[1:]
                
                
            elif TrialSequence[ThisTrial] == 2:

                StimulusSequence[ThisTrial] = OddNeutTrials[0]

                OddNeutTrials = OddNeutTrials[1:]

        else:

                if TrialSequence[ThisTrial] == 0:

                    StimulusSequence[ThisTrial] = EvenCongTrials[0]

                    EvenCongTrials = EvenCongTrials[1:]


                elif TrialSequence[ThisTrial] == 1:

                    StimulusSequence[ThisTrial] = EvenIncongTrials[0]

                    EvenIncongTrials = EvenIncongTrials[1:]
                    
                    
                elif TrialSequence[ThisTrial] == 2:

                    StimulusSequence[ThisTrial] = EvenNeutTrials[0]

                    EvenNeutTrials = EvenNeutTrials[1:]


    RunType = str(np.ones(nTrialsPerRun, dtype = int))
    RunType = RunType.split(' ')
                
    CurrTrialType = str(np.ones(nTrialsPerRun, dtype = int))
    CurrTrialType = CurrTrialType.split(' ')
                
    PrevTrialType = str(np.ones(nTrialsPerRun, dtype = int))
    PrevTrialType = PrevTrialType.split(' ')
                

    for ThisTrial in range(0,nTrialsPerRun):

        RunType[ThisTrial]= NameOfBlock
    
        if (StimulusSequence[ThisTrial] < 5):
            CurrTrialType[ThisTrial] = 'Congruent'
                        
        elif (StimulusSequence[ThisTrial] > 4) and (StimulusSequence[ThisTrial] < 9):     
            CurrTrialType[ThisTrial] = 'Incongruent'
            
        else:
            CurrTrialType[ThisTrial] = 'Neutral'

        if (ThisTrial == 0):
            PrevTrialType[ThisTrial] = 'None'
                        
        else:
            PrevTrialType[ThisTrial] = CurrTrialType[ThisTrial - 1]
                        

    Distractor = str(np.ones(nTrialsPerRun, dtype = int))
    Distractor = Distractor.split(' ')
                    
    Target = str(np.ones(nTrialsPerRun, dtype = int))
    Target = Target.split(' ')
                    
    CorrectAnswer = str(np.ones(nTrialsPerRun, dtype = int))
    CorrectAnswer = CorrectAnswer.split(' ')
    
    Orientation_Prime = str(np.ones(nTrialsPerRun, dtype = int))
    Orientation_Prime = Orientation_Prime.split(' ')
    
    Orientation_Probe = str(np.ones(nTrialsPerRun, dtype = int))
    Orientation_Probe = Orientation_Probe.split(' ')
    
    
    

    for jjj in range(0,nTrialsPerRun):

        if StimulusSequence[jjj] == 1:

            Distractor[jjj] = 'Visual_Stimuli/D_Up.png'
            Target[jjj] = 'Visual_Stimuli/T_Up.png'
            CorrectAnswer[jjj] = 'j'

        elif StimulusSequence[jjj] == 2:

            Distractor[jjj] = 'Visual_Stimuli/D_Down.png'
            Target[jjj] = 'Visual_Stimuli/T_Down.png'
            CorrectAnswer[jjj] = 'n'

        elif StimulusSequence[jjj] == 3:
        
            Distractor[jjj] = 'Visual_Stimuli/D_Left.png'
            Target[jjj]= 'Visual_Stimuli/T_Left.png'
            CorrectAnswer[jjj] = 'f'
                        
        elif StimulusSequence[jjj] == 4:

            Distractor[jjj] = 'Visual_Stimuli/D_Right.png'
            Target[jjj] = 'Visual_Stimuli/T_Right.png'
            CorrectAnswer[jjj] = 'g'

        elif StimulusSequence[jjj] == 5:

            Distractor[jjj] = 'Visual_Stimuli/D_Down.png'
            Target[jjj] = 'Visual_Stimuli/T_Up.png'
            CorrectAnswer[jjj] = 'j'

        elif StimulusSequence[jjj] == 6:

            Distractor[jjj] = 'Visual_Stimuli/D_Up.png'
            Target[jjj] = 'Visual_Stimuli/T_Down.png'
            CorrectAnswer[jjj] = 'n'

        elif StimulusSequence[jjj] == 7:

            Distractor[jjj] = 'Visual_Stimuli/D_Right.png'
            Target[jjj] = 'Visual_Stimuli/T_Left.png'
            CorrectAnswer[jjj] = 'f'

        elif StimulusSequence[jjj] == 8:

            Distractor[jjj] = 'Visual_Stimuli/D_Left.png'
            Target[jjj]= 'Visual_Stimuli/T_Right.png'
            CorrectAnswer[jjj] ='g'
            
        elif StimulusSequence[jjj] == 9:

            Distractor[jjj] = 'Visual_Stimuli/N_Vert.png'
            Target[jjj] = 'Visual_Stimuli/T_Up.png'
            CorrectAnswer[jjj] = 'j'

        elif StimulusSequence[jjj] == 10:

            Distractor[jjj] = 'Visual_Stimuli/N_Vert.png'
            Target[jjj] = 'Visual_Stimuli/T_Down.png'
            CorrectAnswer[jjj] = 'n'

        elif StimulusSequence[jjj] == 11:

            Distractor[jjj] = 'Visual_Stimuli/N_Horiz.png'
            Target[jjj] = 'Visual_Stimuli/T_Left.png'
            CorrectAnswer[jjj] = 'f'

        elif StimulusSequence[jjj] == 12:

            Distractor[jjj] = 'Visual_Stimuli/N_Horiz.png'
            Target[jjj]= 'Visual_Stimuli/T_Right.png'
            CorrectAnswer[jjj] ='g'
    
    
        #The routine below checks if the counterbalancing worked.
        #To see CheckMatrix, uncomment "print(CheckMatrix)"
        #initialization (top) and final value at the end.
        #This allows one to see the initial and final values of each cell of the counterbalancing matrix, which should be 
        #Initial: nTrials/(nTrialTypes*nTrialTypes)/2
        #Final: 0

        #Create a matrix of previous and current trial combinations, with separate
        #identical holders for odd and even trials like above
        #CheckMatrix = np.array(((int((nTrialsPerBlock / (nTrialTypes * nTrialTypes) / 2)) * np.ones([nTrialTypes, nTrialTypes], dtype = int)),(int((nTrialsPerBlock / (nTrialTypes * nTrialTypes) / 2)) * np.ones([nTrialTypes, nTrialTypes], dtype = int)) ))
        
        for i in range(1, nTrialsPerBlock):

            #Establish whether this is an odd or even trial
            if i % 2:#odd
        
                Odd_or_Even = 0
        
            else: #even
    
                Odd_or_Even = 1

        #Decrement the appropriate cell of check matrix
        #CheckMatrix[b[i-1], b[i], Odd_or_Even] = CheckMatrix[b[i-1], b[i], Odd_or_Even] - 1

        #Finally decremement the "imaginary previous trial type" that we created
        #for the first, odd (Odd_Or_Even =1) trial
        #CheckMatrix[prev_trial_type, b[1], 1] = CheckMatrix[prev_trial_type, b[1], 1]-1 

        #print(CheckMatrix)         
    
    #delete conditions file if it already exists
    if os.path.isfile(NameOfFile) == 1:
        os.remove(NameOfFile)
       
    Info = {'RunType': '', 'Distractor': '','Target': '', 'corrAns': '', 'CurrTrialType': '', 'PrevTrialType': ''}# -*- coding: utf-8 -*-

    # An ExperimentHandler isn't essential but helps with data saving
    thisExample = data.ExperimentHandler(name='', version='',
    extraInfo=Info, runtimeInfo=None,
    savePickle=True, saveWideText=True)

    for i in range(0, nTrials):
        Info['RunType'] = RunType[i]
        Info['Distractor'] = Distractor[i]
        Info['Target'] = Target[i]
        Info['corrAns'] = CorrectAnswer[i]
        Info['CurrTrialType'] = CurrTrialType[i]
        Info['PrevTrialType'] = PrevTrialType[i]
        thisExample.nextEntry()
        
    thisExample.saveAsWideText(NameOfFile)