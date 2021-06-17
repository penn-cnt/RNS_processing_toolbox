% Example Data Analysis

% Add tools and read in config.JSON file

addpath(genpath('matlab_tools'))
rns_config = jsondecode(fileread('../config.JSON')); 
ptList = {config.patients.ID}

%% Read in Patient Data

ptID = ptList{1};

[ecogT, ecogD, stims, histT, pdms] = loadRNSptData(ptID, rns_config);

AllData = ecogD.AllData;

%% Example

% Retrive indices of all scheduled events that include or exclude
% stimulation windows. Filter windows takes two sets of windows (or a set
% of windows and a vector of points), and returns indices of the first
% window set that completely include and completely exclude the windows or points in the second
% set.

% Get start and stop indices of all secheduled events
i_sched = find(strcmp(ecogT.ECoGTrigger, 'Scheduled'));
evntIdx= ecogT{i_sched, {'EventStartIdx', 'EventEndIdx'}};

[incl, excl] = filterWindows(evntIdx, StimStartStopIndex); 

vis_event(AllData, ecogT, evntIdx(excl))
