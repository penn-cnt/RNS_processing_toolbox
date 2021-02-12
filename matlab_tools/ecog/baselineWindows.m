function [baseline_windows] = baselineWindows(PatientID,varargin)
%baselineWindows Given RNS Data and Stim MAT Files, this function finds Stimulations of a
%given Trigger Type
% 
% Eg. 
%  [AllData,AllTime,PostStimStartIndex,PostStimEndIndex,...
%   PreStimStartIndex,PreStimEndIndex,StimStartIndex,...
%   StimEndIndex,StimStartTimes,StimEndTimes,StimLengths,...
%   NumStims,TriggerLabels] = findTrigger('RNS002','DesiredTrigger','Long_Episode','NumberofStims',1);
%
%   findTrigger(PatientID,'DesiredTrigger','Long_Episode','WindowLength',1000,'PostBuffer',200,'Fs',250)
%
% Inputs
%   NumberofStims: Number of sub-stimulations per therapy that you want
%   DesiredTrigger: One of the following Strings. Default 'All' will return
%   all Trigger Types
%
%       Long_Episode
%       Magnet
%       Real_Time
%       Saturation
%       Scheduled
%
%   WindowLength: Integer length of window in samples
%   PostBuffer: Length of signal to discard after stimulation in samples
%   Fs: Sampling Frequency
%
%
% Outputs
%
% Where n is the number of samples overall and t is number of therapies
%
%   AllData: 4 Channel by n Column Matrix with EcoG data for given patient
%   AllTime: 1 by n vector with corresponding Time in UTC microseconds
%   NumStims: 1 by t vector with the number of sub-stimulations per therapy
%   TriggerLabels: 1 by t vector with the Trigger Labels for each Stim
%
%   Indeces to find given periods in AllTime and AllData Vector
%       PostStimStartIndex
%       PostStimEndIndex
%       PreStimStartIndex
%       PreStimEndIndex
%       StimStartIndex
%       StimEndIndex
%
%   StimStartTimes
%   StimEndTimes
%   StimLengths


%% Variable Input Defaults

%Instantiate inputParser
p = inputParser;

%Define minimum number of consecutive 0 slope points to make up Stimulation
addRequired(p,'PatientID')
addParameter(p, 'DesiredTrigger','All')
addParameter(p, 'WindowLength',1000)
addParameter(p, 'PostBuffer',200)
addParameter(p, 'Fs',250)
addParameter(p, 'NumberofStims',200)


%Parse inputs
parse(p, PatientID, varargin{:});
WindowLength=p.Results.WindowLength;
PostBuffer=p.Results.PostBuffer;
Fs=p.Results.Fs;
DesiredTrigger=p.Results.DesiredTrigger;
NumberofStims=p.Results.NumberofStims;
%% Load Patient Data
load([PatientID,'Stim.mat']);
load('PatientTriggerTimes.mat');

%% Find Trigger Labels for Baseline Recordings
N=str2double(PatientID(4:end));

I=PatientTriggerTimes{N,1}.RawUTCTimestamp<StimStartTimes(1);
TriggerLabels=PatientTriggerTimes{N,1}.ECoGTrigger(I)
TriggerTimes=PatientTriggerTimes{N,1}.RawUTCTimestamp(I);

%% Filter for desired Trigger
LETriggerIndex = cellfun('length',regexp(TriggerLabels,'Long_Episode')) == 1;
LEwindow_endtimes=TriggerTimes(LETriggerIndex);
LEwindow_starttimes=LEwindow_endtimes-5e6;
LElabel=ones(length(LEwindow_starttimes),1);

ScheduledTriggerIndex = cellfun('length',regexp(TriggerLabels,'Scheduled')) == 1;
Scheduledwindow_endtimes=TriggerTimes(ScheduledTriggerIndex);
Scheduledwindow_starttimes=Scheduledwindow_endtimes-5e6;
Scheduledlabel=zeros(length(Scheduledwindow_starttimes),1);

baseline_windows=[LEwindow_starttimes,LEwindow_endtimes,LElabel;
    Scheduledwindow_starttimes,Scheduledwindow_endtimes,Scheduledlabel];

end
