function [StimStartIndex, StimEndIndex, StimStartTimes, StimEndTimes, StimGap,...
    StimLengths, MaxStimLength, MinStimLength, MaxStimIndex, MinStimIndex, UTCStartTimes, NumStims]...
    = findStim(AllData, AllTime, varargin)
% findStim finds the Stimulation Group periods in Neuropace RNS timeseries data
%
%   To use default Channel=1 and Min=15
%
%   [StimStartIndex,StimEndIndex,StimStartTimes,StimEndTimes, StimGap,...
%   StimLengths,MaxStimLength, MinStimLength, MaxStimIndex, MinStimIndex, UTCStartTimes]=...
%   findStim(AllData, AllTime)
%
%   To use Channel 2 with a min of 3 points length
%
%   [StimStartIndex,StimEndIndex,StimStartTimes,StimEndTimes, StimGap,...
%   StimLengths,MaxStimLength, MinStimLength, MaxStimIndex, MinStimIndex, UTCStartTimes]=...
%   findStim(AllData,AllTime,'Min',3,'Channel',2)
%
% Inputs
%   AllData: A matrix in which each row contains Voltage data for a given
%   channel
%
%   AllTime: Corresponding Times to Data points in AllData
%
%   Min: The Minimum Number of consecutive 0 slope points to be considered
%   a Stimulation
%
%   Channel: The Channel in which you search for stimulations
%
% Outputs
%
%     StimStartIndex: Index of Stimulation Group Start Points
%     StimEndIndex: Index of Stimulation Group End Points
%     StimStartTimes: Start UTC Times of Stimulation Group
%     StimEndTimes: End UTC Times of Stimulation Group
%     StimGap: Time between each stimulation Group and the next one in Samples(1/250 s)
%     StimLengths: Length of each Stimulation Group measured in Samples(1/250 s)
%     MaxStimLength: Longest Stimulation Group Length in Samples
%     MinStimLength: Minimum Stimulation Group length in Samples
%     MaxStimIndex: Index of longest stimulation Group
%     MinStimIndex: Index of shortest stimulation Group
%     UTCStartTimes: The start times of each RNS recording
%     NumStims: The number of smaller stimulations per stim group
%
%   Arjun Ravi Shankar
%   Litt Lab July 2018

%% Variable Input Defaults
%Instantiate inputParser
p = inputParser;

%Define minimum number of consecutive 0 slope points to make up Stimulation
addRequired(p,'AllData')
addRequired(p,'AllTime')
addParameter(p, 'Min',15)
addParameter(p, 'Channel',1)

%Parse inputs
parse(p, AllData, AllTime, varargin{:})
Min=p.Results.Min;
Channel=p.Results.Channel;

%% Find UTC Start Times
Indeces=find(diff(AllTime)>4000);
UTCStartTimes=[AllTime(1),AllTime(Indeces+1)];

%% Find Stimulation Triggers

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

%Correct for Double Stimulation Error
StimGap=StimStartTimes(2:end)-StimEndTimes(1:end-1);
% Double=find(StimGap<=4000000);
% 
% %Count Number of Stimulation Groups
% 
% % First Assume Every Stimulation is a Single Stim
% NumStims=ones(1,length(StimStartTimes));
% 
% %Correct for the Stimulations which are consecutive
% NumStims(Double)=2;
% NumStims(Double+1)=2;
% 
% %Count number of stims in multiple stim chunks
% DiffDouble=diff(Double);
% DiffDouble(DiffDouble~=1)=0;
% DiffDouble=[0,DiffDouble,0];
% 
% MultipleStarts=find(diff(DiffDouble)==1);
% MultipleEnds=find(diff(DiffDouble)==-1);
% MultipleLengths=MultipleEnds-MultipleStarts;
% NumStims(Double(MultipleEnds)+1)=MultipleLengths+2;
% NumStims(Double)=[];
% 
% % Count Multiple Stims as one
% StimEndIndex(Double)=[];
% StimStartIndex(Double+1)=[];
% 
% %Find Stim Start and End Times
% StimStartTimes=AllTime(StimStartIndex);
% StimEndTimes=AllTime(StimEndIndex);
% 
% %Recalculate StimGap
% StimGap=StimStartTimes(2:end)-StimEndTimes(1:end-1);

%% Statistics

%Find Stimulation Lengths
StimLengths=StimEndIndex-StimStartIndex;

%Find Max Stim Length
MaxStimLength=max(StimLengths);
MaxStimIndex=find(StimLengths==MaxStimLength);

%Find Min Stim Length
MinStimLength=min(StimLengths);
MinStimIndex=find(StimLengths==MinStimLength);

%% Plot Statistics

%Plot Histogram of Stimulation Lengths
figure
histogram(StimLengths)
title('Histogram of Stimulation Lengths')
xlabel('Lengths of Stimulation')
ylabel('Occurences')
end
