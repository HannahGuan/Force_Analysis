%clear all variables
clear all;
warning('off')

%Choose outlier method
prompt1 = 'Hi! For the analysis, SD = 1, SN = 2. Please enter your selection here:';
y = input(prompt1);

if y == 1
    
    outlier_method = 1; %1 for SD, 2 for SN
    NameOutput = 'Action_Effect_Results_Exp1_SD_2017b.txt';
    
elseif y == 2
    
    outlier_method = 2; %1 for SD, 2 for SN
    NameOutput = 'Action_Effect_Results_Exp1_SN_2017b.txt';
    
end

%Indicate number of force samples to include in time-locked average force responses
%Let's choose 440 samples, which is 900 ms at a sampling rate of 500 Hz.
Num_Force_Samples = 1500;

%Let's indicate when the action effect repetition/alternation and DRS occurred
AE_time = 1.5;
DRS_time = 1.8;

%get path to specific folder, number of files, and start counter
addpath ('Logfiles/')
Logfile_Names = dir(fullfile(('Logfiles/'), '*.csv*'));

if exist(NameOutput, 'file') == 2
    
    delete(NameOutput);
    
end

numberOfFiles = numel(Logfile_Names);
file_position = 0;

%initialize variables
filename1 = cell(1, length(Logfile_Names));
filename2 = cell(1, length(Logfile_Names));

%read in each of these file names by position with counter
for i = 1:numberOfFiles
    
    file_position = file_position + 1;
    
    filename1(file_position) = {Logfile_Names(file_position).name};
    
    filename2(file_position) = filename1(file_position);
end

%switch from columns to rows to create a vertical vector
filename = filename2;
DataFile1 = filename';

%start at row 4 because of headings in file
DataFile = DataFile1(1:end, :);

%h12e table to check work
x = table(DataFile1);

%Let's also figure out the forcefile name for each subject
addpath ('Forcefiles/')
Forcefile_Names = dir(fullfile(('Forcefiles/'), '*.csv*'));

numberOfFiles = numel(Forcefile_Names);
file_position = 0;

%initialize variables
filename1 = cell(1, length(Forcefile_Names));
filename2 = cell(1, length(Forcefile_Names));

%read in each of these file names by position with counter
for i = 1:numberOfFiles
    
    file_position = file_position + 1;
    
    filename1(file_position) = {Forcefile_Names(file_position).name};
    
    filename2(file_position) = filename1(file_position);
end

%switch from columns to rows to create a vertical vector
filename = filename2;
ForceFile1 = filename';

%start at row 4 because of headings in file
ForceFile = ForceFile1(1:end, :);

%h12e table to check work
y = table(ForceFile1);

%Initialize the variable that will hold each subjects two time-locked average force responses
SubjectForceCurves = zeros(length(DataFile), 6*Num_Force_Samples);

for Subjects = 1:length(DataFile)
    
    %MATLAB's attempt at R's version of a dataframe
    T = readtable(DataFile{Subjects},'HeaderLines',0,'ReadVariableNames',true);
    
    %Rename the first column of T just in case it comes in incorrectly
    T.Properties.VariableNames(1) = {'Block'};
    
    %Get the name of the computer on which this subject was run
    Computer_Name = char(T.Computer_Name(1));
    
    %uncomment line below to see participant data file name
    DataFile{Subjects};
    
    %create loading bar
    fprintf('Loading %d out of %d data files.\n', [Subjects, length(DataFile)])
    
    %get only Test trials
    data = T(strcmp(T.Block, 'Test'), :);
    
    %Let's get the columns we need
    data = table(data.expName, data.participant, data.HowOldAreYou_inYears__, data.AreYouMaleOrFemale_MOrF__, data.DoYouHaveNormalVisionAndHearing_, data.date, data.Block, data.Feedback_1, data.Feedback_2, data.DiscriminationResponseStimulusArduinoResponseTime_ms_, data.Freq_Rep, data.Response_Rep, data.Discrimination_Response_Stimulus_Onset_Arduino_ms_, data.Cued_R1_Arduino_Analog_Column, data.Uncued_R1_Arduino_Analog_Column, data.Signaled_R2_Arduino_Analog_Column, data.Unsignaled_R2_Arduino_Analog_Column, data.Cued_R1_Arduino_Digital_Column, data.Uncued_R1_Arduino_Digital_Column, data.Signaled_R2_Arduino_Digital_Column, data.Unsignaled_R2_Arduino_Digital_Column, 'VariableNames',{'ExpName','PsNum','Age', 'Sex', 'Vision', 'Date','Block','Feedback_1','Feedback_2','RT2','Freq_Rep','Response_Rep', 'DRS_Onset_Time_Arduino', 'Cued_R1_Arduino_Analog_Column', 'Uncued_R1_Arduino_Analog_Column', 'Signaled_R2_Arduino_Analog_Column', 'Unsignaled_R2_Arduino_Analog_Column', 'Cued_R1_Arduino_Digital_Column', 'Uncued_R1_Arduino_Digital_Column', 'Signaled_R2_Arduino_Digital_Column', 'Unsignaled_R2_Arduino_Digital_Column'});
    
    %If no age entered, set to 999
    if strcmp(num2str(data.Age(1)), 'NaN');
        data.Age(1:end) = 999;
    end
    
    %if sex is entered correctly as 'M' or 'F', do nothing
    if strcmp(data.Sex(1), 'M') | strcmp(data.Sex(1), 'F') | strcmp(data.Sex(1), 'm') | strcmp(data.Sex(1), 'f')
        
        %Otherwise replace with '999'
    elseif strcmp(num2str(data.Sex(1)), 'NaN')
        data.Sex(1:end) = 999;
        data.Sex = num2str(data.Sex);
    end
    
    %I. Congruency sequence effects in RT for correct trials preceded by correct trials
    
    %Columns AE, AF, and AG have the relevant trial codes to analyze the RT and Error Rate data in a 3-way ANOVA
    %The factors are:
    %Frequency (L) repetition (repeat, alternate)
    %Response (R) repetition (repeat, alternate) 
    %Frequency Repetition is in Column N
    %Response Repetition is in Column O
    
    %now find the different trial types
    %We will always require the cued response and the discrimination response to be correct for the RT analyses
    %For the error rate and force analyses, we will only required the cued response to be correct
    %In the realm of force, we want to examine changes in force PRIOR to an error (i.e., prior to the Discrimination Response Stimulus)
    
    %Freq rep, response rep
    colorR_locR_respR = data(strcmp(data.Freq_Rep, 'Rep') & strcmp(data.Response_Rep, 'Rep') & strcmp(data.Feedback_1,'Correct') & strcmp(data.Feedback_2,'Correct'),:);
    
    %Freq rep, response alt
    colorR_locR_respA = data(strcmp(data.Freq_Rep, 'Rep') & strcmp(data.Response_Rep, 'Alt') & strcmp(data.Feedback_1,'Correct') & strcmp(data.Feedback_2,'Correct'),:);
    
    %Freq alt, response rep
    colorR_locA_respR = data(strcmp(data.Freq_Rep, 'Alt') & strcmp(data.Response_Rep, 'Rep') & strcmp(data.Feedback_1,'Correct') & strcmp(data.Feedback_2,'Correct'),:);
    
    %Freq alt, response alt
    colorR_locA_respA = data(strcmp(data.Freq_Rep, 'Alt') & strcmp(data.Response_Rep, 'Alt') & strcmp(data.Feedback_1,'Correct') & strcmp(data.Feedback_2,'Correct'),:);
    
    
    if outlier_method == 1
        
        %Color rep, loc rep, response rep
        colorR_locR_respR_RTs_Trimmed = colorR_locR_respR.RT2;
        colorR_locR_respR_RTs_Trimmed(find(  (colorR_locR_respR.RT2 < mean(colorR_locR_respR.RT2) - 3*std(colorR_locR_respR.RT2)) | (colorR_locR_respR.RT2 > mean(colorR_locR_respR.RT2) + 3*std(colorR_locR_respR.RT2))   )  ) = [];
        Num_colorR_locR_respR_Outliers = length(colorR_locR_respR.RT2) - length(colorR_locR_respR_RTs_Trimmed);
        
        %Color rep, loc rep, response alt
        colorR_locR_respA_RTs_Trimmed = colorR_locR_respA.RT2;
        colorR_locR_respA_RTs_Trimmed(find(  (colorR_locR_respA.RT2 < mean(colorR_locR_respA.RT2) - 3*std(colorR_locR_respA.RT2)) | (colorR_locR_respA.RT2 > mean(colorR_locR_respA.RT2) + 3*std(colorR_locR_respA.RT2))   )  ) = [];
        Num_colorR_locR_respA_Outliers = length(colorR_locR_respA.RT2) - length(colorR_locR_respA_RTs_Trimmed);
        
        %Color rep, loc alt, response rep
        colorR_locA_respR_RTs_Trimmed = colorR_locA_respR.RT2;
        colorR_locA_respR_RTs_Trimmed(find(  (colorR_locA_respR.RT2 < mean(colorR_locA_respR.RT2) - 3*std(colorR_locA_respR.RT2)) | (colorR_locA_respR.RT2 > mean(colorR_locA_respR.RT2) + 3*std(colorR_locA_respR.RT2))   )  ) = [];
        Num_colorR_locA_respR_Outliers = length(colorR_locA_respR.RT2) - length(colorR_locA_respR_RTs_Trimmed);
        
        %Color rep, loc alt, response alt
        colorR_locA_respA_RTs_Trimmed = colorR_locA_respA.RT2;
        colorR_locA_respA_RTs_Trimmed(find(  (colorR_locA_respA.RT2 < mean(colorR_locA_respA.RT2) - 3*std(colorR_locA_respA.RT2)) | (colorR_locA_respA.RT2 > mean(colorR_locA_respA.RT2) + 3*std(colorR_locA_respA.RT2))   )  ) = [];
        Num_colorR_locA_respA_Outliers = length(colorR_locA_respA.RT2) - length(colorR_locA_respA_RTs_Trimmed);
        
        
        %Calculate the total number of outliers
        Total_Num_Outliers = ...
            Num_colorR_locR_respR_Outliers + ...
            Num_colorR_locR_respA_Outliers + ...
            Num_colorR_locA_respR_Outliers + ...
            Num_colorR_locA_respA_Outliers;
        
        Total_Percent_Outliers = Total_Num_Outliers/(size(data,1));
        
        %Calculate mean RTs for each condition after removing outliers
        
        colorR_locR_respR_meanRT = mean(colorR_locR_respR_RTs_Trimmed);
        colorR_locR_respA_meanRT = mean(colorR_locR_respA_RTs_Trimmed);
        
        colorR_locA_respR_meanRT = mean(colorR_locA_respR_RTs_Trimmed);
        colorR_locA_respA_meanRT = mean(colorR_locA_respA_RTs_Trimmed);
        
        
        %How many trials were correct overall?
        Num_correct_trials = size(data(strcmp(data.Feedback_1,'Correct') & strcmp(data.Feedback_2,'Correct'),:), 1);
        Num_all_trials = size(data, 1);
        Overall_Accuracy = Num_correct_trials/Num_all_trials;
        
        %Accuracy
        %Get all trials in each condition that were preceded by a correct
        %S1 response
        %Color rep, loc rep, response rep
        colorR_locR_respRa = data(strcmp(data.Freq_Rep, 'Rep') & strcmp(data.Response_Rep, 'Rep') & strcmp(data.Feedback_1,'Correct'),:);
        
        %Color rep, loc rep, response alt
        colorR_locR_respAa = data(strcmp(data.Freq_Rep, 'Rep') & strcmp(data.Response_Rep, 'Alt') & strcmp(data.Feedback_1,'Correct'),:);
        
        %Color rep, loc alt, response rep
        colorR_locA_respRa = data(strcmp(data.Freq_Rep, 'Alt') & strcmp(data.Response_Rep, 'Rep') & strcmp(data.Feedback_1,'Correct'),:);
        
        %Color rep, loc alt, response alt
        colorR_locA_respAa = data(strcmp(data.Freq_Rep, 'Alt') & strcmp(data.Response_Rep, 'Alt') & strcmp(data.Feedback_1,'Correct'),:);
        
        
        %only include correct and incorrect trials - that's all there is
        colorR_locR_respRa = colorR_locR_respRa(strcmp(colorR_locR_respRa.data.Feedback_2, 'Correct') | strcmp(colorR_locR_respRa.Feedback_2, 'Error'),:);
        colorR_locR_respAa = colorR_locR_respAa(strcmp(colorR_locR_respAa.data.Feedback_2, 'Correct') | strcmp(colorR_locR_respAa.Feedback_2, 'Error'),:);
        colorR_locA_respRa = colorR_locA_respRa(strcmp(colorR_locA_respRa.data.Feedback_2, 'Correct') | strcmp(colorR_locA_respRa.Feedback_2, 'Error'),:);
        colorR_locA_respAa = colorR_locA_respAa(strcmp(colorR_locA_respAa.data.Feedback_2, 'Correct') | strcmp(colorR_locA_respAa.Feedback_2, 'Error'),:);
        
        
        %Exclude the outliers
        
        colorR_locR_respRa_Trimmeda = colorR_locR_respRa.RT2;
        colorR_locR_respRa_Trimmeda(find(  (colorR_locR_respRa.RT2 < mean(colorR_locR_respRa.RT2) - 3*std(colorR_locR_respRa.RT2)) | (colorR_locR_respRa.RT2 > mean(colorR_locR_respRa.RT2) + 3*std(colorR_locR_respRa.RT2))   )  ) = [-700];
        
        colorR_locR_respAa_Trimmeda = colorR_locR_respAa.RT2;
        colorR_locR_respAa_Trimmeda(find(  (colorR_locR_respAa.RT2 < mean(colorR_locR_respAa.RT2) - 3*std(colorR_locR_respAa.RT2)) | (colorR_locR_respAa.RT2 > mean(colorR_locR_respAa.RT2) + 3*std(colorR_locR_respAa.RT2))   )  ) = [-700];
        
        colorR_locA_respRa_Trimmeda = colorR_locA_respRa.RT2;
        colorR_locA_respRa_Trimmeda(find(  (colorR_locA_respRa.RT2 < mean(colorR_locA_respRa.RT2) - 3*std(colorR_locA_respRa.RT2)) | (colorR_locA_respRa.RT2 > mean(colorR_locA_respRa.RT2) + 3*std(colorR_locA_respRa.RT2))   )  ) = [-700];
        
        colorR_locA_respAa_Trimmeda = colorR_locA_respAa.RT2;
        colorR_locA_respAa_Trimmeda(find(  (colorR_locA_respAa.RT2 < mean(colorR_locA_respAa.RT2) - 3*std(colorR_locA_respAa.RT2)) | (colorR_locA_respAa.RT2 > mean(colorR_locA_respAa.RT2) + 3*std(colorR_locA_respAa.RT2))   )  ) = [-700];
        
        %now get rows that don't have the flagged number
        colorR_locR_respRa_acc_noout = colorR_locR_respRa(find(colorR_locR_respRa_Trimmeda > 0), :);
        colorR_locR_respAa_acc_noout = colorR_locR_respAa(find(colorR_locR_respAa_Trimmeda > 0), :);
        colorR_locA_respRa_acc_noout = colorR_locA_respRa(find(colorR_locA_respRa_Trimmeda > 0), :);
        colorR_locA_respAa_acc_noout = colorR_locA_respAa(find(colorR_locA_respAa_Trimmeda > 0), :);
        
        
        %Calculate the number of correct trials in each condition above
        Num_Correct_colorR_locR_respRa = size(colorR_locR_respRa_acc_noout(strcmp(colorR_locR_respRa_acc_noout.Feedback_2, 'Correct'),:), 1);
        Num_Correct_colorR_locR_respAa = size(colorR_locR_respAa_acc_noout(strcmp(colorR_locR_respAa_acc_noout.Feedback_2, 'Correct'),:), 1);
        Num_Correct_colorR_locA_respRa = size(colorR_locA_respRa_acc_noout(strcmp(colorR_locA_respRa_acc_noout.Feedback_2, 'Correct'),:), 1);
        Num_Correct_colorR_locA_respAa = size(colorR_locA_respAa_acc_noout(strcmp(colorR_locA_respAa_acc_noout.Feedback_2, 'Correct'),:), 1);
        
        
        
        %Calculate error rate in each condition
        colorR_locR_respRa_ER = 1 - (Num_Correct_colorR_locR_respRa)/size(colorR_locR_respRa_acc_noout, 1);
        colorR_locR_respAa_ER = 1 - (Num_Correct_colorR_locR_respAa)/size(colorR_locR_respAa_acc_noout, 1);
        colorR_locA_respRa_ER = 1 - (Num_Correct_colorR_locA_respRa)/size(colorR_locA_respRa_acc_noout, 1);
        colorR_locA_respAa_ER = 1 - (Num_Correct_colorR_locA_respAa)/size(colorR_locA_respAa_acc_noout, 1);
        
        
    elseif outlier_method == 2
        
        %Get Sn values
        
        [colorR_locR_respR_Sn, colorR_locR_respR_x] = Sn(colorR_locR_respR.RT2);
        [colorR_locR_respA_Sn, colorR_locR_respA_x] = Sn(colorR_locR_respA.RT2);
        
        [colorR_locA_respR_Sn, colorR_locA_respR_x] = Sn(colorR_locA_respR.RT2);
        [colorR_locA_respA_Sn, colorR_locA_respA_x] = Sn(colorR_locA_respA.RT2);
        
        
        %find the outliers
        
        colorR_locR_respR_out = (colorR_locR_respR_x/colorR_locR_respR_Sn > 3);
        colorR_locR_respA_out = (colorR_locR_respA_x/colorR_locR_respA_Sn > 3);
        
        colorR_locA_respR_out = (colorR_locA_respR_x/colorR_locA_respR_Sn > 3);
        colorR_locA_respA_out = (colorR_locA_respA_x/colorR_locA_respA_Sn > 3);
        
        %take out the outliers
        colorR_locR_respR_RTs_Trimmed = colorR_locR_respR.RT2;
        colorR_locR_respR_RTs_Trimmed(colorR_locR_respR_out) = [];
        Num_colorR_locR_respR_Outliers = length(colorR_locR_respR.RT2) - length(colorR_locR_respR_RTs_Trimmed);
        
        colorR_locR_respA_RTs_Trimmed = colorR_locR_respA.RT2;
        colorR_locR_respA_RTs_Trimmed(colorR_locR_respA_out) = [];
        Num_colorR_locR_respA_Outliers = length(colorR_locR_respA.RT2) - length(colorR_locR_respA_RTs_Trimmed);
        
        colorR_locA_respR_RTs_Trimmed = colorR_locA_respR.RT2;
        colorR_locA_respR_RTs_Trimmed(colorR_locA_respR_out) = [];
        Num_colorR_locA_respR_Outliers = length(colorR_locA_respR.RT2) - length(colorR_locA_respR_RTs_Trimmed);
        
        colorR_locA_respA_RTs_Trimmed = colorR_locA_respA.RT2;
        colorR_locA_respA_RTs_Trimmed(colorR_locA_respA_out) = [];
        Num_colorR_locA_respA_Outliers = length(colorR_locA_respA.RT2) - length(colorR_locA_respA_RTs_Trimmed);
        
        
        %Calculate the total number of outliers
        Total_Num_Outliers = ...
            Num_colorR_locR_respR_Outliers + ...
            Num_colorR_locR_respA_Outliers + ...
            Num_colorR_locA_respR_Outliers + ...
            Num_colorR_locA_respA_Outliers;
        
        Total_Percent_Outliers = Total_Num_Outliers/(size(data,1));
        
        %Calculate mean RTs for each condition after removing outliers
        
        colorR_locR_respR_meanRT = mean(colorR_locR_respR_RTs_Trimmed);
        colorR_locR_respA_meanRT = mean(colorR_locR_respA_RTs_Trimmed);
        
        colorR_locA_respR_meanRT = mean(colorR_locA_respR_RTs_Trimmed);
        colorR_locA_respA_meanRT = mean(colorR_locA_respA_RTs_Trimmed);
        
        
        %How many trials were correct overall?
        Num_correct_trials = size(data(strcmp(data.Feedback_1,'Correct') & strcmp(data.Feedback_2,'Correct'),:), 1);
        Num_all_trials = size(data, 1);
        Overall_Accuracy = Num_correct_trials/Num_all_trials;
        
        %Accuracy
        %Get all S2 responses in each condition that were preceded by a correct S1 response
        %Color rep, loc rep, response rep
        colorR_locR_respRa = data(strcmp(data.Freq_Rep, 'Rep') & strcmp(data.Response_Rep, 'Rep') & strcmp(data.Feedback_1,'Correct'),:);
        
        %Color rep, loc rep, response alt
        colorR_locR_respAa = data(strcmp(data.Freq_Rep, 'Rep') & strcmp(data.Response_Rep, 'Alt') & strcmp(data.Feedback_1,'Correct'),:);
        
        
        %Color rep, loc alt, response rep
        colorR_locA_respRa = data(strcmp(data.Freq_Rep, 'Alt') & strcmp(data.Response_Rep, 'Rep') & strcmp(data.Feedback_1,'Correct'),:);
        
        %Color rep, loc alt, response alt
        colorR_locA_respAa = data(strcmp(data.Freq_Rep, 'Alt') & strcmp(data.Response_Rep, 'Alt') & strcmp(data.Feedback_1,'Correct'),:);
        
        
        %only include correct and incorrect trials
        colorR_locR_respRa = colorR_locR_respRa(strcmp(colorR_locR_respRa.Feedback_2, 'Correct') | strcmp(colorR_locR_respRa.Feedback_2, 'Error'),:);
        colorR_locR_respAa = colorR_locR_respAa(strcmp(colorR_locR_respAa.Feedback_2, 'Correct') | strcmp(colorR_locR_respAa.Feedback_2, 'Error'),:);
        colorR_locA_respRa = colorR_locA_respRa(strcmp(colorR_locA_respRa.Feedback_2, 'Correct') | strcmp(colorR_locA_respRa.Feedback_2, 'Error'),:);
        colorR_locA_respAa = colorR_locA_respAa(strcmp(colorR_locA_respAa.Feedback_2, 'Correct') | strcmp(colorR_locA_respAa.Feedback_2, 'Error'),:);
        
        %Get Sn values
        [colorR_locR_respRa_Sn, colorR_locR_respRa_x] = Sn(colorR_locR_respRa.RT2);
        [colorR_locR_respAa_Sn, colorR_locR_respAa_x] = Sn(colorR_locR_respAa.RT2);
        [colorR_locA_respRa_Sn, colorR_locA_respRa_x] = Sn(colorR_locA_respRa.RT2);
        [colorR_locA_respAa_Sn, colorR_locA_respAa_x] = Sn(colorR_locA_respAa.RT2);
        
        %find the outliers
        colorR_locR_respRa_out = (colorR_locR_respRa_x/colorR_locR_respRa_Sn > 3);
        colorR_locR_respAa_out = (colorR_locR_respAa_x/colorR_locR_respAa_Sn > 3);
        colorR_locA_respRa_out = (colorR_locA_respRa_x/colorR_locA_respRa_Sn > 3);
        colorR_locA_respAa_out = (colorR_locA_respAa_x/colorR_locA_respAa_Sn > 3);
        
        %take out the outliers by first flagging them with a crazy, unrealistic number
        colorR_locR_respRa_Trimmeda = colorR_locR_respRa.RT2;
        colorR_locR_respRa_Trimmeda(colorR_locR_respRa_out) = [-700];
        
        colorR_locR_respAa_Trimmeda = colorR_locR_respAa.RT2;
        colorR_locR_respAa_Trimmeda(colorR_locR_respAa_out) = [-700];
        
        colorR_locA_respRa_Trimmeda = colorR_locA_respRa.RT2;
        colorR_locA_respRa_Trimmeda(colorR_locA_respRa_out) = [-700];
        
        colorR_locA_respAa_Trimmeda = colorR_locA_respAa.RT2;
        colorR_locA_respAa_Trimmeda(colorR_locA_respAa_out) = [-700];
        
        
        %now get rows that don't have the flagged number
        colorR_locR_respRa_acc_noout = colorR_locR_respRa(find(colorR_locR_respRa_Trimmeda > 0), :);
        colorR_locR_respAa_acc_noout = colorR_locR_respAa(find(colorR_locR_respAa_Trimmeda > 0), :);
        colorR_locA_respRa_acc_noout = colorR_locA_respRa(find(colorR_locA_respRa_Trimmeda > 0), :);
        colorR_locA_respAa_acc_noout = colorR_locA_respAa(find(colorR_locA_respAa_Trimmeda > 0), :);
        
        
        
        %Calculate the number of correct trials in each condition above
        Num_Correct_colorR_locR_respRa = size(colorR_locR_respRa_acc_noout(strcmp(colorR_locR_respRa_acc_noout.Feedback_2, 'Correct'),:), 1);
        Num_Correct_colorR_locR_respAa = size(colorR_locR_respAa_acc_noout(strcmp(colorR_locR_respAa_acc_noout.Feedback_2, 'Correct'),:), 1);
        Num_Correct_colorR_locA_respRa = size(colorR_locA_respRa_acc_noout(strcmp(colorR_locA_respRa_acc_noout.Feedback_2, 'Correct'),:), 1);
        Num_Correct_colorR_locA_respAa = size(colorR_locA_respAa_acc_noout(strcmp(colorR_locA_respAa_acc_noout.Feedback_2, 'Correct'),:), 1);
        
        
        %Calculate error rate in each condition
        colorR_locR_respRa_ER = 1 - (Num_Correct_colorR_locR_respRa)/size(colorR_locR_respRa_acc_noout, 1);
        colorR_locR_respAa_ER = 1 - (Num_Correct_colorR_locR_respAa)/size(colorR_locR_respAa_acc_noout, 1);
        colorR_locA_respRa_ER = 1 - (Num_Correct_colorR_locA_respRa)/size(colorR_locA_respRa_acc_noout, 1);
        colorR_locA_respAa_ER = 1 - (Num_Correct_colorR_locA_respAa)/size(colorR_locA_respAa_acc_noout, 1);
        
        
    end
    
    %%%%%%%Force Analyses%%%%%%
    
    %Calculate the time-locked average force responses
    
    %1. Load this subject's force data file
    
    %MATLAB's attempt at R's version of a dataframe
    ForceTable = readtable(ForceFile{Subjects});
    
    ForceTable = table2array(ForceTable);
    
    %create loading bar
    fprintf('Loading %d out of %d force data files.\n', [Subjects, length(DataFile)])
    
    %1.5 Convert the raw numerical values in Columns 1-5 to force in centinewtons
    
    %Start by calculating the mean baseline value on each key during the first 500 samples
    Mean_Baseline_5_Keys = mean(ForceTable(1:500,1:5));
    
    %Next, subtract the Mean_Baseline_Value for each key from all the values
    %This adjusts for a small change in baseline from the initial calibration
    %However, it does not adjust for any changes in "gain" (i.e., how a pressure value increases with force)
    %I assume that the "slope" relating pressure value to force remains the same as during the initial calibration
    ForceTable(:,1:5) = ForceTable(:,1:5)-Mean_Baseline_5_Keys;
   
    %Box 1 - left room
    if strcmpi (Computer_Name, 'PSYC-DANWEISS23')
            
            Calibration_Matrix = [1.0000    1.9493    1.6587    2.2420    1.7540    1.9193
    2.0000    3.6907    3.5587    3.9753    3.4786    3.8687
    5.0000    8.8000    9.3114    9.2673    8.4786    9.5333
   10.0000   17.5027   18.9934   17.9506   16.8893   19.2387
   20.0000   34.3767   38.4054   35.0546   33.5433   38.1693
   50.0000   86.1053   95.7240   87.9353   83.9440   95.6927];
            
    %Box 2 - middle room
    elseif strcmpi (Computer_Name, 'PSYC-DANWEISS25')
            
            Calibration_Matrix = [1.0000    1.6638    1.9447    1.8651    1.9108    1.4993
    2.0000    3.2618    3.8481    3.7791    3.7948    3.2386
    5.0000    8.2305    9.4354    9.3625    9.5075    7.8660
   10.0000   16.6231   19.0834   18.6811   18.8928   16.0100
   20.0000   33.2878   38.1934   37.3471   37.7435   32.0826
   50.0000   83.6805   95.5994   93.2598   94.5148   81.3853];
            
    %Box 3 - right room
    elseif strcmpi (Computer_Name, 'PSYC-DANWEISS24')
            
            Calibration_Matrix = [1.0000    1.9564    1.9894    1.9617    1.9434    1.7588
    2.0000    3.4971    3.8274    3.8237    3.6300    3.5828
    5.0000    8.5471    9.4460    9.1737    9.4027    8.5048
   10.0000   17.2671   18.8220   18.6490   19.0007   16.7115
   20.0000   34.1691   37.7080   36.9123   38.1627   33.3355
   50.0000   85.0704   94.4140   92.2503   96.4520   83.2661];
            
    end
    
    %B. Convert the mass values in column 1 from grams to kg
        Calibration_Matrix(:,1) = Calibration_Matrix(:,1)/1000;
        
        %C. Multiply the kg values by 9.8 m/s squared to get Newtons
        %because force (N) = mass (kg) x 9.8 m/s squared (accel)
        Calibration_Matrix(:,1) = Calibration_Matrix(:,1)*9.8;
        
        %D. Multiply the Newton values by 100 to get centinewtons
        Calibration_Matrix(:,1) = Calibration_Matrix(:,1)*100;
        
        %E. Create the design matrix
        DM = [Calibration_Matrix(:,1), repmat([1],6,1)];
        
        %F. Come up with the regression coefficients for each key
        %These reveal how to go from centinewtons (x) to force sensor readings (y)
        Key_1_coeffs = regress(Calibration_Matrix(:,2), DM);
        Key_2_coeffs = regress(Calibration_Matrix(:,3), DM);
        Key_3_coeffs = regress(Calibration_Matrix(:,4), DM);
        Key_4_coeffs = regress(Calibration_Matrix(:,5), DM);
        Key_5_coeffs = regress(Calibration_Matrix(:,6), DM);
        
        %G. Convert each force sensor reading to centinewtons using the coefficients above
        %Y = B1x + b0 is the regression equation
        %Use this equation to convert each force sensor reading (i.e., each Y value)to force in centinewtons (i.e., a particular x value)
        %More specifically, x = (y - B0)/B1
        ForceTable(:,1) = (ForceTable(:,1) - Key_1_coeffs(2))/Key_1_coeffs(1);
        ForceTable(:,2) = (ForceTable(:,2) - Key_2_coeffs(2))/Key_2_coeffs(1);
        ForceTable(:,3) = (ForceTable(:,3) - Key_3_coeffs(2))/Key_3_coeffs(1);
        ForceTable(:,4) = (ForceTable(:,4) - Key_4_coeffs(2))/Key_4_coeffs(1);
        ForceTable(:,5) = (ForceTable(:,5) - Key_5_coeffs(2))/Key_5_coeffs(1);
        
     
    %2. Start out with the same trials as for the Accuracy analysis above
    %The logic is that we don't need to exclude based on R2, which has not yet occurred
    %Indeed, retrieval/signaling could lead to errors and outliers
    %Could re-think this and exclude later, though.
    %For now, get all trials in each condition that were preceded by a correct S1 response
    %This just redefines the same variables we used for the accuracy analysis above
    %Freq is not frequency but, rather, Word
    
   %Freq rep, response rep
    colorR_locR_respRa = data(strcmp(data.Freq_Rep, 'Rep') & strcmp(data.Response_Rep, 'Rep') & strcmp(data.Feedback_1,'Correct'),:);
    
    %Freq rep, response alt
    colorR_locR_respAa = data(strcmp(data.Freq_Rep, 'Rep') & strcmp(data.Response_Rep, 'Alt') & strcmp(data.Feedback_1,'Correct'),:);
    
    %Freq alt, response rep
    colorR_locA_respRa = data(strcmp(data.Freq_Rep, 'Alt') & strcmp(data.Response_Rep, 'Rep') & strcmp(data.Feedback_1,'Correct'),:);
    
    %Freq alt, response alt
    colorR_locA_respAa = data(strcmp(data.Freq_Rep, 'Alt') & strcmp(data.Response_Rep, 'Alt') & strcmp(data.Feedback_1,'Correct'),:);
   
    %3. Collect the time course of force in each trial for the signaled and unsignaled R2 response keys
    %I think we can collect the force data 500-0 ms before the distractor response stimulus (DRS) onsets
    
    %First, we need to collect the DRS onset times and columns of the force file containing the analog force data 
    
    %Column 13 contains the DRS onset times
    DRS_Onset_Times_colorR_locR_respRa = table2array(colorR_locR_respRa(:,13));
    DRS_Onset_Times_colorR_locR_respAa = table2array(colorR_locR_respAa(:,13));
    DRS_Onset_Times_colorR_locA_respRa = table2array(colorR_locA_respRa(:,13));
    DRS_Onset_Times_colorR_locA_respAa = table2array(colorR_locA_respAa(:,13));
    
    %Column 16 indicates which column of ForceTable contains the analog force data for the signaled R2 response
    Signaled_R2_Analog_Response_Column_colorR_locR_respRa = table2array(colorR_locR_respRa(:, 16));
    Signaled_R2_Analog_Response_Column_colorR_locR_respAa = table2array(colorR_locR_respAa(:, 16));
    Signaled_R2_Analog_Response_Column_colorR_locA_respRa = table2array(colorR_locA_respRa(:, 16));
    Signaled_R2_Analog_Response_Column_colorR_locA_respAa = table2array(colorR_locA_respAa(:, 16));
    
    %Column 17 indicates which column of ForceTable contains the analog force data for the unsignaled R2 response
    Unsignaled_R2_Analog_Response_Column_colorR_locR_respRa = table2array(colorR_locR_respRa(:, 17));
    Unsignaled_R2_Analog_Response_Column_colorR_locR_respAa = table2array(colorR_locR_respAa(:, 17));
    Unsignaled_R2_Analog_Response_Column_colorR_locA_respRa = table2array(colorR_locA_respRa(:, 17));
    Unsignaled_R2_Analog_Response_Column_colorR_locA_respAa = table2array(colorR_locA_respAa(:, 17));
    
    %Second, we need to collect the force data for Num_Force_Samples BEFORE the DRS appears in each trial
    %We need to do this separately for each condition, I guess
    %Start with the onset time and end Num_Force_Samples later
    %Simultaneously extract the force at these time points
    %Loop through each trial, separately for each condition
    
    %Condition 1 - colorR_locR_respRa
    for i = 1:size(DRS_Onset_Times_colorR_locR_respRa,1)
        %Let's find the row of the force table corresponding to the ith onset time
        ThisForceRow = find(ForceTable(:,15) == DRS_Onset_Times_colorR_locR_respRa(i,1));
        if ThisForceRow == 1%The DRS never onset because the subject made an error in the first part of the trial
            Signaled_Force_colorR_locR_respRa(i,1:Num_Force_Samples) = zeros(1, length(1:Num_Force_Samples));
            Unsignaled_Force_colorR_locR_respRa(i,1:Num_Force_Samples) = zeros(1, length(1:Num_Force_Samples));
        else
            %Now extract the analog force across time in each trial on the signaled and unsignaled response key
            Signaled_Force_colorR_locR_respRa(i,1:Num_Force_Samples) = ForceTable(ThisForceRow - (Num_Force_Samples -1):ThisForceRow, Signaled_R2_Analog_Response_Column_colorR_locR_respRa(i,1));% - mean(ForceTable((ThisForceRow - 1000*(DRS_time- AE_time)/2 - 249):ThisForceRow - 150, Signaled_R2_Analog_Response_Column_colorR_locR_respRa(i,1)), 1);
            Unsignaled_Force_colorR_locR_respRa(i,1:Num_Force_Samples) = ForceTable(ThisForceRow - (Num_Force_Samples -1):ThisForceRow, Unsignaled_R2_Analog_Response_Column_colorR_locR_respRa(i,1));% - mean(ForceTable((ThisForceRow - 1000*(DRS_time- AE_time)/2 - 249):ThisForceRow - 150, Unsignaled_R2_Analog_Response_Column_colorR_locR_respRa(i,1)), 1);
        end
    end
    
    %Now, we need to delete any rows containing all 0s that we inserted above
    Signaled_Force_colorR_locR_respRa = Signaled_Force_colorR_locR_respRa(any(Signaled_Force_colorR_locR_respRa,2),:);
    Unsignaled_Force_colorR_locR_respRa = Unsignaled_Force_colorR_locR_respRa(any(Unsignaled_Force_colorR_locR_respRa,2),:);

    %Calculate the mean force across trials for this condition
    mean_Signaled_Force_colorR_locR_respRa = mean(Signaled_Force_colorR_locR_respRa, 1);
    mean_Unsignaled_Force_colorR_locR_respRa = mean(Unsignaled_Force_colorR_locR_respRa, 1);
    
    %Condition 2 - colorR_locR_respAa
    for i = 1:size(DRS_Onset_Times_colorR_locR_respAa,1)
        %Let's find the row of the force table corresponding to the ith onset time
        ThisForceRow = find(ForceTable(:,15) == DRS_Onset_Times_colorR_locR_respAa(i,1));
        if ThisForceRow == 1%The DRS never onset because the subject made an error in the first part of the trial
            Signaled_Force_colorR_locR_respAa(i,1:Num_Force_Samples) = zeros(1, length(1:Num_Force_Samples));
            Unsignaled_Force_colorR_locR_respAa(i,1:Num_Force_Samples) = zeros(1, length(1:Num_Force_Samples));
        else
            %Now extract the analog force across time in each trial on the signaled and unsignaled response keys
            Signaled_Force_colorR_locR_respAa(i,1:Num_Force_Samples) = ForceTable(ThisForceRow - (Num_Force_Samples -1):ThisForceRow, Signaled_R2_Analog_Response_Column_colorR_locR_respAa(i,1));% - mean(ForceTable((ThisForceRow - 1000*(DRS_time- AE_time)/2 - 249):ThisForceRow - 150, Signaled_R2_Analog_Response_Column_colorR_locR_respAa(i,1)), 1);
            Unsignaled_Force_colorR_locR_respAa(i,1:Num_Force_Samples) = ForceTable(ThisForceRow - (Num_Force_Samples -1):ThisForceRow, Unsignaled_R2_Analog_Response_Column_colorR_locR_respAa(i,1));% - mean(ForceTable((ThisForceRow - 1000*(DRS_time- AE_time)/2 - 249):ThisForceRow - 150, Unsignaled_R2_Analog_Response_Column_colorR_locR_respAa(i,1)), 1);
        end
    end
    
    %Now, we need to delete any rows containing all 0s that we inserted above
    Signaled_Force_colorR_locR_respAa = Signaled_Force_colorR_locR_respAa(any(Signaled_Force_colorR_locR_respAa,2),:);
    Unsignaled_Force_colorR_locR_respAa = Unsignaled_Force_colorR_locR_respAa(any(Unsignaled_Force_colorR_locR_respAa,2),:);

    %Calculate the mean force across trials for this condition
    mean_Signaled_Force_colorR_locR_respAa = mean(Signaled_Force_colorR_locR_respAa, 1);
    mean_Unsignaled_Force_colorR_locR_respAa = mean(Unsignaled_Force_colorR_locR_respAa, 1);
    
    %Condition 3 - colorR_locA_respRa
    for i = 1:size(DRS_Onset_Times_colorR_locA_respRa,1)
        %Let's find the row of the force table corresponding to the ith onset time
        ThisForceRow = find(ForceTable(:,15) == DRS_Onset_Times_colorR_locA_respRa(i,1));
        if ThisForceRow == 1%The DRS never onset because the subject made an error in the first part of the trial
            Signaled_Force_colorR_locA_respRa(i,1:Num_Force_Samples) = zeros(1, length(1:Num_Force_Samples));
            Unsignaled_Force_colorR_locA_respRa(i,1:Num_Force_Samples) = zeros(1, length(1:Num_Force_Samples));
        else
            %Now extract the analog force across time in each trial on the signaled and unsignaled response keys
            Signaled_Force_colorR_locA_respRa(i,1:Num_Force_Samples) = ForceTable(ThisForceRow - (Num_Force_Samples -1):ThisForceRow, Signaled_R2_Analog_Response_Column_colorR_locA_respRa(i,1));% - mean(ForceTable((ThisForceRow - 1000*(DRS_time- AE_time)/2 - 249):ThisForceRow - 150, Signaled_R2_Analog_Response_Column_colorR_locA_respRa(i,1)), 1);;
            Unsignaled_Force_colorR_locA_respRa(i,1:Num_Force_Samples) = ForceTable(ThisForceRow - (Num_Force_Samples -1):ThisForceRow, Unsignaled_R2_Analog_Response_Column_colorR_locA_respRa(i,1));% - mean(ForceTable((ThisForceRow - 1000*(DRS_time- AE_time)/2 - 249):ThisForceRow - 150, Unsignaled_R2_Analog_Response_Column_colorR_locA_respRa(i,1)), 1);;
        end
    end
    
    %Now, we need to delete any rows containing all 0s that we inserted above
    Signaled_Force_colorR_locA_respRa = Signaled_Force_colorR_locA_respRa(any(Signaled_Force_colorR_locA_respRa,2),:);
    Unsignaled_Force_colorR_locA_respRa = Unsignaled_Force_colorR_locA_respRa(any(Unsignaled_Force_colorR_locA_respRa,2),:);
    
    %Calculate the mean force across trials for this condition
    mean_Signaled_Force_colorR_locA_respRa = mean(Signaled_Force_colorR_locA_respRa, 1);
    mean_Unsignaled_Force_colorR_locA_respRa = mean(Unsignaled_Force_colorR_locA_respRa, 1);
    
    %Condition 4 - colorR_locA_respAa
    for i = 1:size(DRS_Onset_Times_colorR_locA_respAa,1)
        %Let's find the row of the force table corresponding to the ith onset time
        ThisForceRow = find(ForceTable(:,15) == DRS_Onset_Times_colorR_locA_respAa(i,1));
        if ThisForceRow == 1%The DRS never onset because the subject made an error in the first part of the trial
            Signaled_Force_colorR_locA_respAa(i,1:Num_Force_Samples) = zeros(1, length(1:Num_Force_Samples));
            Unsignaled_Force_colorR_locA_respAa(i,1:Num_Force_Samples) = zeros(1, length(1:Num_Force_Samples));
        else
            %Now extract the analog force across time in each trial on the signaled and unsignaled response keys
            Signaled_Force_colorR_locA_respAa(i,1:Num_Force_Samples) = ForceTable(ThisForceRow - (Num_Force_Samples -1):ThisForceRow, Signaled_R2_Analog_Response_Column_colorR_locA_respAa(i,1));%- mean(ForceTable((ThisForceRow - 1000*(DRS_time- AE_time)/2 - 249):ThisForceRow - 150, Signaled_R2_Analog_Response_Column_colorR_locA_respAa(i,1)), 1);
            Unsignaled_Force_colorR_locA_respAa(i,1:Num_Force_Samples) = ForceTable(ThisForceRow - (Num_Force_Samples -1):ThisForceRow, Unsignaled_R2_Analog_Response_Column_colorR_locA_respAa(i,1));%- mean(ForceTable((ThisForceRow - 1000*(DRS_time- AE_time)/2 - 249):ThisForceRow - 150, Unsignaled_R2_Analog_Response_Column_colorR_locA_respAa(i,1)), 1);
        end
    end
    
    %Now, we need to delete any rows containing all 0s that we inserted above
    Signaled_Force_colorR_locA_respAa = Signaled_Force_colorR_locA_respAa(any(Signaled_Force_colorR_locA_respAa,2),:);
    Unsignaled_Force_colorR_locA_respAa = Unsignaled_Force_colorR_locA_respAa(any(Unsignaled_Force_colorR_locA_respAa,2),:);
    
    %Calculate the mean force across trials for this condition
    mean_Signaled_Force_colorR_locA_respAa = mean(Signaled_Force_colorR_locA_respAa, 1);
    mean_Unsignaled_Force_colorR_locA_respAa = mean(Unsignaled_Force_colorR_locA_respAa, 1);
   
    
    %Now, let's create an array to hold the mean_Signaled_Response_Force and mean_Unsignaled_Response_Force data averaged across all 4 conditions
    mean_Signaled_Response_Force = mean ([mean_Signaled_Force_colorR_locR_respRa; mean_Signaled_Force_colorR_locR_respAa; mean_Signaled_Force_colorR_locA_respRa; mean_Signaled_Force_colorR_locA_respAa], 1); 
    mean_Unsignaled_Response_Force = mean ([mean_Unsignaled_Force_colorR_locR_respRa; mean_Unsignaled_Force_colorR_locR_respAa; mean_Unsignaled_Force_colorR_locA_respRa; mean_Unsignaled_Force_colorR_locA_respAa], 1); 
    
    %Also distinguish between frequency repetition and frequency alternation trials.
    mean_Signaled_Response_Force_Freq_Rep = mean ([mean_Signaled_Force_colorR_locR_respRa; mean_Signaled_Force_colorR_locR_respAa], 1); 
    mean_Signaled_Response_Force_Freq_Alt = mean ([mean_Signaled_Force_colorR_locA_respRa; mean_Signaled_Force_colorR_locA_respAa], 1);

    mean_Unsignaled_Response_Force_Freq_Rep = mean ([mean_Unsignaled_Force_colorR_locR_respRa; mean_Unsignaled_Force_colorR_locR_respAa], 1); 
    mean_Unsignaled_Response_Force_Freq_Alt = mean ([mean_Unsignaled_Force_colorR_locA_respRa; mean_Unsignaled_Force_colorR_locA_respAa], 1); 
    
    
    %Next, let's create a variable to hold this data for each subject
    ThisSubjectForceData = [mean_Signaled_Response_Force   mean_Unsignaled_Response_Force   mean_Signaled_Response_Force_Freq_Rep   mean_Unsignaled_Response_Force_Freq_Rep   mean_Signaled_Response_Force_Freq_Alt   mean_Unsignaled_Response_Force_Freq_Alt];
    SubjectForceCurves(Subjects, :) = ThisSubjectForceData; 
    
    
    
    %====================Output this subject's results============%
    
    %Check whether a logfile with the same name already exists
    switch (exist(NameOutput, 'file'))
        
        case 0% the file does not exist so create it
            
            logFileName = NameOutput;
            fid = fopen(logFileName,'w+');
            fprintf(fid,'ExpName\t PsNum\t Age\t Sex\t Vision\t Date\t freqR_respR\t freqR_respA\t freqA_respR\t freqA_respA\t freqR_respR_ER\t freqR_respA_ER\t freqA_respR_ER\t freqA_respA_ER\t Overall_Accuracy_R2\t Total_Percent_Outliers\n');
            fprintf(fid, '%s\t %d\t %d\t %s\t %s\t %s\t %f\t %f\t %f\t %f\t %f\t %f\t %f\t %f\t %f\t %f\t', char(data.ExpName(1)), unique(data.PsNum), unique(data.Age), unique(char(data.Sex)), char(data.Vision{1}), char(data.Date(1)), colorR_locR_respR_meanRT, colorR_locR_respA_meanRT, colorR_locA_respR_meanRT,colorR_locA_respA_meanRT, colorR_locR_respRa_ER, colorR_locR_respAa_ER, colorR_locA_respRa_ER, colorR_locA_respAa_ER, Overall_Accuracy, Total_Percent_Outliers);
            
        case 2% the file already exists so append this subject's data to the next row
            
            logFileName = NameOutput;
            fid = fopen(logFileName,'a');
            fprintf(fid, '\n');
            %Overall Analysis
            fprintf(fid, '%s\t %d\t %d\t %s\t %s\t %s\t %f\t %f\t %f\t %f\t %f\t %f\t %f\t %f\t %f\t %f\t', char(data.ExpName(1)), unique(data.PsNum), unique(data.Age), unique(char(data.Sex)), char(data.Vision{1}), char(data.Date(1)), colorR_locR_respR_meanRT, colorR_locR_respA_meanRT, colorR_locA_respR_meanRT,colorR_locA_respA_meanRT, colorR_locR_respRa_ER, colorR_locR_respAa_ER, colorR_locA_respRa_ER, colorR_locA_respAa_ER, Overall_Accuracy, Total_Percent_Outliers);
            
    end %switch
    
    %Close the file
    fclose(fid);
    
    
end

%After calculating each subject's force curves, save all subjects force curces to a .mat file 
save ('Force_Curves.mat', 'SubjectForceCurves');

function [Sn_output, x_j] = Sn(X)

%Compute the measure of scale 'Sn', from Rousseeuw & Croux (1993)

%X should be an Nx1 column vector, or an NxM matrix, where M is the number
%of data dimensions (e.g., Nx@ for xy data).

%A robust alternative to MAD for statistical outlier identification. Unlike
%MAD, Sn does not make an assumption of symmetry, so in principle should be
%more robust to skewed distributions.

%The outputs of this function have been validated against equivalent
%function in MAPLE(tm).

%Example:

%basic example
%X = [1 5 2 2 7 4 1 6]';
%Sn = RousseuwCrouxSn(X) %should give 3.015

%Use Sn to identify statistical outliers
%X = [1 5 2 2 7 50 1 5]';
%[Sn, x_j] = RousseeuwCrouxSn(X);
%outliers = X(x_j/Sn > 3) % NB: typical criterion 2 or 3

%See also: mad.m [Statistics Toolbox]

%Author(s): Pete R Jones <petejonze@gmail.com>

%Copyright 2019: P R Jones

%************************************************************************

% (defensive) convert row vector to column
if size(X,1) == 1, X = X';end

%get number of elements
n = size(X,1);

%Set c: bias correction factor for finite sample size. NB: the value
%used here match those used in the MAPLE implementation of Sn. For
%more regarding the computation of the finite sample correction
%factors, see Pison, Aelst, & Willems (2002), Metrika, 55(1), 111-123.

if n < 10
    
    cc = [NaN 0.743 1.851 0.954 1.351 0.993 1.198 1.005 1.131];
    c = cc(n);
    
elseif mod(n,2)==1 % n is odd
    
    c = n/(n-.9);
    
else % n is even
    
    c = 1;
    
end

%compute median distance of each element to all other elements
x_j = nan(n,1);
for i = 1:n
    X_other = X([1:i-1 i+1:end], :); %get all values except current
    d = sqrt(sum(bsxfun(@minus, X_other, X(i,:)).^2, 2));%comp dist
    x_j(i) = median(d);%compute median distance
end

%compute median of all median differences, and apply correction
Sn_output = c * median(x_j);
end


