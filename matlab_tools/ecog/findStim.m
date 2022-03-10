function [StimStartStopIndex, stats] = findStim(AllData, Min, Channel, show)
% findStim finds the Stimulation Group periods in Neuropace RNS timeseries data
%
%   To use default Channel=1, Min=15, show = false
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
%   Updated Brittany Scheid (bscheid@seas.upenn.edu) February 2021

%% Variable Input Defaults
arguments
    AllData
    Min = 15     % min # of consecutive 0 slope points to make up Stimulation
    Channel = 1  % channel to make detections on
    show = false
end

AllData = AllData+512; % Make sure it is all positive

if size(AllData,1) ~= 4
    AllData = AllData'; %  
end

%% Find Stimulation Triggers

%Find Slope of Data
Slope=diff(AllData,1,2); %./4000;

%Correct for max and min flatlines and analog to digital conversion
%artifacts
Slope(Channel,AllData(Channel,:)<100)=1;
Slope(Channel,AllData(Channel,:)>900)=1;

%Find Start and End Locations of Regions with Zero Slope 
ZeroSlopeInflections=diff(Slope(Channel,:)==0);
ZeroSlopeStarts=find(ZeroSlopeInflections==1)+1;
ZeroSlopeEnds=find(ZeroSlopeInflections==-1)+1;

% If more starts then ends, ignore last one
if find(ZeroSlopeInflections== -1,1, 'last') < find(ZeroSlopeInflections== 1,1, 'last')
    ZeroSlopeStarts = ZeroSlopeStarts(1:end-1);
end

%Find Indices of Stimulation Start and End Points
StimStartStopIndex= [ZeroSlopeStarts(ZeroSlopeEnds-ZeroSlopeStarts>=Min)',...
                     ZeroSlopeEnds(ZeroSlopeEnds-ZeroSlopeStarts>=Min)'];

%Find Stim Start and End Times

%Correct for Double Stimulation Error
% StimGap= StimStartStopTimes(2:end,1)-StimStartStopTimes(1:end-1,2);

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
if show
    figure
    histogram(stats.StimLengths)
    title('Histogram of Stimulation Lengths')
    xlabel('Lengths of Stimulation')
    ylabel('Occurences')
end

end
