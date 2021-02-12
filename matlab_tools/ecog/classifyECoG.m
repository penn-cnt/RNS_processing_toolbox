function [ECoGsWithStim,ECoGsWithoutStim]= classifyECoG(PatientID, varargin)
% classifyECoG returns a list of ECoGs With Stimulation and ECoGs Without
% Stimulation for a given patient
%
%   To use default Channel=1 and Min=15 and All Trigger Labels
%
%   [ECoGsWithStim,ECoGsWithoutStim]= classifyECoG('RNS002')
%
%   To use Channel 2 with a min of 3 points length and Scheduled Trigger
%   Labels
%
%   [ECoGsWithStim,ECoGsWithoutStim]=classifyECoG('RNS002','Min',3,'Channel',2,'DesiredTrigger','Scheduled')
%
% Inputs
%   PatientID: A string like 'RNS002'
%
%   Min: The Minimum Number of consecutive 0 slope points to be considered
%   a Stimulation
%
%   Channel: The Channel in which you search for stimulations
%
%   DesiredTrigger: One of the following Strings. Default 'All' will return
%   all Trigger Types
%
%       Long_Episode
%       Magnet
%       Real_Time
%       Saturation
%       Scheduled
%
% Outputs
%
%     ECoGsWithStim: Table of ECoGs With Stim with Timestamps and Trigger
%     Labels
%     ECoGsWithoutStim: Table of ECoGs without Stim with Timestamps and Trigger
%     Labels
%
%   Arjun Ravi Shankar
%   Litt Lab November 2018

%% Variable Input Defaults
%Instantiate inputParser
p = inputParser;

%Define minimum number of consecutive 0 slope points to make up Stimulation
addRequired(p,'PatientID')
addParameter(p, 'Min',15)
addParameter(p, 'Channel',1)
addParameter(p, 'DesiredTrigger','All')

%Parse inputs
parse(p, PatientID, varargin{:})
Min=p.Results.Min;
Channel=p.Results.Channel;
DesiredTrigger=p.Results.DesiredTrigger;

%% Load Patient Data
load([PatientID,'.mat']);

%% Find Individual Stimulations

%Find Slope of Data
Slope=diff(AllData,1,2)./4000;

%Correct for max and min flatlines and analog to digital conversion
%artifacts
Slope(Channel,AllData(Channel,:)<200)=1;
Slope(Channel,AllData(Channel,:)>800)=1;

%Find Start and End Locations of Regions with Zero Slope 
ZeroSlopeInflections=diff(Slope(Channel,:)==0);
ZeroSlopeStarts=find(ZeroSlopeInflections==1)+1;
ZeroSlopeEnds=find(ZeroSlopeInflections==-1)+1;

%Find Indices of Stimulation Start and End Points
StimStartIndex=ZeroSlopeStarts(ZeroSlopeEnds-ZeroSlopeStarts>=Min);
StimEndIndex=ZeroSlopeEnds(ZeroSlopeEnds-ZeroSlopeStarts>=Min);

%Find Stim Start and End Times
StimStartTimes=AllTime(StimStartIndex);
StimEndTimes=AllTime(StimEndIndex);

%% Find which ECoG files each Stimulation belongs to
PatientTriggerLabels=load('PatientTriggerLabels.mat');
PatientTriggerLabels=PatientTriggerLabels.PatientTriggerLabels;

PatientTriggerTimes=load('PatientTriggerTimes.mat');
PatientTriggerTimes=PatientTriggerTimes.PatientTriggerTimes;

N=str2double(PatientID(4:end));

[~,I]=min(abs((repmat(PatientTriggerLabels{N,1}.Timestamp,1,length(StimStartTimes))-repmat(StimStartTimes,length(PatientTriggerLabels{N,1}.Timestamp),1))));

%% Classify ECoGs as With Stimulation or Without Stimulation

%Calculate the ECoGs With Stimulation In Them
ECoGsWithStim=[PatientTriggerLabels{N,1}(unique(I),:),PatientTriggerTimes{N,1}(unique(I),'RawUTCTimestamp')];

%Calculate the ECoGs Without Stimulation 
Index=~ismember(1:length(PatientTriggerLabels{N,1}.Timestamp),unique(I));
ECoGsWithoutStim=[PatientTriggerLabels{N,1}(Index,:),PatientTriggerTimes{N,1}(Index,'RawUTCTimestamp')];

%% Filter for desired Trigger
if ~strcmp(DesiredTrigger,'All')
    DesiredTriggerIndex = find(cellfun('length',regexp(ECoGsWithStim.ECoGTrigger(:),DesiredTrigger)) == 1);
    ECoGsWithStim=ECoGsWithStim(DesiredTriggerIndex,:);

    DesiredTriggerIndex = find(cellfun('length',regexp(ECoGsWithoutStim.ECoGTrigger(:),DesiredTrigger)) == 1);
    ECoGsWithoutStim=ECoGsWithoutStim(DesiredTriggerIndex,:);
end

end