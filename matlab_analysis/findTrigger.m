function [AllData,AllTime,PostStimStartIndex,PostStimEndIndex,...
    PreStimStartIndex,PreStimEndIndex,StimStartIndex,...
    StimEndIndex,StimStartTimes,StimEndTimes,StimLengths,...
    NumStims,TriggerLabels] = findTrigger(PatientID,varargin)
%findTrigger Given RNS Data and Stim MAT Files, this function finds Stimulations of a
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
addParameter(p, 'WindowLength',1250)
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
load([PatientID,'.mat']);
load([PatientID,'Stim.mat']);

%% Calcualte Indeces of Pre/Post Stim Windows
PostStimStartIndex=StimEndIndex+PostBuffer;
PostStimEndIndex=StimEndIndex+PostBuffer+WindowLength;
PreStimStartIndex=StimStartIndex-1-WindowLength;
PreStimEndIndex=StimStartIndex-1; % Pre Stim Window ends 1 sample before stimultion


%% Delete Windows with other Stimulations in them
WindowsWithStim=find(StimGap<(WindowLength*1e6/250));
WindowsWithStim=[WindowsWithStim,WindowsWithStim+1];

PostStimStartIndex(WindowsWithStim)=[];
PostStimEndIndex(WindowsWithStim)=[];
PreStimStartIndex(WindowsWithStim)=[];
PreStimEndIndex(WindowsWithStim)=[];

StimStartIndex(WindowsWithStim)=[];
StimEndIndex(WindowsWithStim)=[];
StimStartTimes(WindowsWithStim)=[];
StimEndTimes(WindowsWithStim)=[];
StimLengths(WindowsWithStim)=[];
NumStims(WindowsWithStim)=[];
% StimGap(WindowsWithStim(1:end-1))=[];

%% Delete Stimulation Windows in which there is missing post stimulation

MissingPost=find((AllTime(PostStimEndIndex)-StimEndTimes)>(PostBuffer/Fs*10^6+WindowLength/Fs*10^6));

PostStimStartIndex(MissingPost)=[];
PostStimEndIndex(MissingPost)=[];
PreStimStartIndex(MissingPost)=[];
PreStimEndIndex(MissingPost)=[];

StimStartIndex(MissingPost)=[];
StimEndIndex(MissingPost)=[];
StimStartTimes(MissingPost)=[];
StimEndTimes(MissingPost)=[];
StimLengths(MissingPost)=[];
NumStims(MissingPost)=[];
% StimGap(MissingPost)=[];

%% Delete Stimulation Windows in which there is missing pre stimulation
MissingPre=find((StimStartTimes-AllTime(PreStimStartIndex))>(1/Fs*10^6+WindowLength/Fs*10^6));

PostStimStartIndex(MissingPre)=[];
PostStimEndIndex(MissingPre)=[];
PreStimStartIndex(MissingPre)=[];
PreStimEndIndex(MissingPre)=[];

StimStartIndex(MissingPre)=[];
StimEndIndex(MissingPre)=[];
StimStartTimes(MissingPre)=[];
StimEndTimes(MissingPre)=[];
StimLengths(MissingPre)=[];
NumStims(MissingPre)=[];
% StimGap(MissingPre)=[];

%% Find Trigger Labels for each Stimulation
PatientTriggerLabels=load('PatientTriggerLabels.mat');
PatientTriggerLabels=PatientTriggerLabels.PatientTriggerLabels;
N=str2double(PatientID(4:end));

[~,I]=min(abs((repmat(PatientTriggerLabels{N,1}.Timestamp,1,length(StimStartTimes))-repmat(StimStartTimes,length(PatientTriggerLabels{N,1}.Timestamp),1))));
TriggerLabels=PatientTriggerLabels{N,1}.ECoGTrigger(I);

%% Filter for desired Trigger
if ~strcmp(DesiredTrigger,'All')
    DesiredTriggerIndex = find(cellfun('length',regexp(TriggerLabels,DesiredTrigger)) == 1);
    
    PostStimStartIndex=PostStimStartIndex(DesiredTriggerIndex);
    PostStimEndIndex=PostStimEndIndex(DesiredTriggerIndex);
    PreStimStartIndex=PreStimStartIndex(DesiredTriggerIndex);
    PreStimEndIndex=PreStimEndIndex(DesiredTriggerIndex);
    
    StimStartIndex=StimStartIndex(DesiredTriggerIndex);
    StimEndIndex=StimEndIndex(DesiredTriggerIndex);
    StimStartTimes=StimStartTimes(DesiredTriggerIndex);
    StimEndTimes=StimEndTimes(DesiredTriggerIndex);
    StimLengths=StimLengths(DesiredTriggerIndex);
    NumStims=NumStims(DesiredTriggerIndex);
    
    TriggerLabels=TriggerLabels(DesiredTriggerIndex);
end

%% Filter for Number of Stimulations
if NumberofStims ~=200
    PostStimStartIndex=PostStimStartIndex(NumStims==NumberofStims);
    PostStimEndIndex=PostStimEndIndex(NumStims==NumberofStims);
    PreStimStartIndex=PreStimStartIndex(NumStims==NumberofStims);
    PreStimEndIndex=PreStimEndIndex(NumStims==NumberofStims);
    
    StimStartIndex=StimStartIndex(NumStims==NumberofStims);
    StimEndIndex=StimEndIndex(NumStims==NumberofStims);
    StimStartTimes=StimStartTimes(NumStims==NumberofStims);
    StimEndTimes=StimEndTimes(NumStims==NumberofStims);
    StimLengths=StimLengths(NumStims==NumberofStims);
    
    TriggerLabels=TriggerLabels(NumStims==NumberofStims);
    
    NumStims=NumStims(NumStims==NumberofStims);
end

end

