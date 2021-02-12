function [StimStartStopIndex, StimStartStopTimes, StimGap, stats] = findStim(AllData, AllTime, varargin)
% findStim finds the Stimulation Group periods in Neuropace RNS timeseries data
%
%   To use default Channel=1 and Min=15
%
%   [StimStartStopIndex, StimStartStopTimes, StimGap, stats]= findStim(AllData, AllTime)
%
%   To use Channel 2 with a min of 3 points length
%
%   [StimStartStopIndex, StimStartStopTimes, StimGap, stats]= findStim(AllData, AllTime ,'Min',3,'Channel',2)
%
% Inputs
%   AllData: A matrix in which each row contains Voltage data for a given
%   channel
%
%   AllTime: Corresponding Times to Data points in AllData
%
%   Min (optional): The Minimum Number of consecutive 0 slope points to be considered
%   a Stimulation
%
%   Channel (optional): The Channel in which you search for stimulations
%
% Outputs
%
%     StimStartStopIndex: Index of Stimulation Group Start and End Points
%     StimStartStop[Times: Start and End UTC Times of Stimulation Group
%     StimGap: Time between each stimulation Group and the next one in Samples(1/250 s)
%     StimLengths: Length of each Stimulation Group measured in Samples(1/250 s)
%     stats
%       MaxStimLength: Longest Stimulation Group Length in Samples
%       MinStimLength: Minimum Stimulation Group length in Samples
%       MaxStimIndex: Index of longest stimulation Group
%       MinStimIndex: Index of shortest stimulation Group
%       NumStims: The number of smaller stimulations per stim group
%
%   Arjun Ravi Shankar
%   Litt Lab July 2018
%
%   Updated Brittany Scheid (bscheid@seas.upenn.edu) September 2020

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

AllTime= AllTime(:); 

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
StimStartStopIndex= [ZeroSlopeStarts(ZeroSlopeEnds-ZeroSlopeStarts>=Min)',...
                     ZeroSlopeEnds(ZeroSlopeEnds-ZeroSlopeStarts>=Min)'];

%Find Stim Start and End Times
StimStartStopTimes=[AllTime(StimStartStopIndex(:,1)), AllTime(StimStartStopIndex(:,2))];

%Correct for Double Stimulation Error
StimGap=StimStartStopTimes(2:end,1)-StimStartStopTimes(1:end-1,2);

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

stats = struct(); 
%Find Stimulation Lengths
stats.StimLengths= diff(StimStartStopIndex,[],2);

%Find Max Stim Length
stats.MaxStimLength=max(stats.StimLengths);
stats.MaxStimIndex=find(stats.StimLengths==stats.MaxStimLength);

%Find Min Stim Length
stats.MinStimLength=min(stats.StimLengths);
stats.MinStimIndex=find(stats.StimLengths==stats.MinStimLength);

%% Plot Statistics

%Plot Histogram of Stimulation Lengths
figure
histogram(stats.StimLengths)
title('Histogram of Stimulation Lengths')
xlabel('Lengths of Stimulation')
ylabel('Occurences')
end
