
function [Starts, Ends] = baselineLE(PatientID)
%Find Baseline Long Episodes

%% Load Patient Data
load([PatientID,'Stim.mat']);
load('PatientTriggerAllTimes.mat');

%% Find Trigger Labels for Baseline Recordings
N=str2double(PatientID(4:end));

I=PatientTriggerAllTimes{N,1}.StartUTCTimestamp<StimStartTimes(1);
TriggerLabels=PatientTriggerAllTimes{N,1}.ECoGTrigger(I);
StartTimes=PatientTriggerAllTimes{N,1}.StartUTCTimestamp(I);
EndTimes=PatientTriggerAllTimes{N,1}.EndUTCTimestamp(I);

%% Filter for desired Trigger
LETriggerIndex = cellfun('length',regexp(TriggerLabels,'Long_Episode')) == 1;
Starts(1,:)=StartTimes(LETriggerIndex);
Ends(1,:)=EndTimes(LETriggerIndex);
end
