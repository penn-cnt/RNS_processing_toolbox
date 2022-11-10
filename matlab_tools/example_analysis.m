% Example Data Analysis

% Add tools and read in config.JSON file

addpath(genpath('matlab_tools'))
rns_config = jsondecode(fileread('../config.JSON')); 
ptList = {rns_config.patients.ID}

%% Read in Patient Data

ptID = ptList{1};

[ecogT, ecogD, stims, histT, pdms] = loadRNSptData(ptID, rns_config, 'timeOffset', true);

AllData = ecogD.AllData;

%% Visualization Example

% Retrive indices of all scheduled events that include or exclude
% stimulation windows. Filter windows takes two sets of windows (or a set
% of windows and a vector of points), and returns indices of the first
% window set that completely include and completely exclude the windows or points in the second
% set.

% Get start and stop indices of all secheduled events
i_sched = find(strcmp(ecogT.ECoGTrigger, 'Scheduled'));
evntIdx= ecogT{i_sched, {'EventStartIdx', 'EventEndIdx'}};

[incl, excl] = filterWindows(evntIdx, stims.StimStartStopIndex); 

vis_event(AllData, ecogT, evntIdx(excl))

%% Feature Calculation Example

ptID = ptList{1}; 
ftList = {'ll', 'bp', 'plv'};   % feature list
wlen = 2;                       % windowLength, seconds
[fts, flabels, windows_info] = RNS_raw_feature_pipeline(ptID, rns_config,...
    'ftList', ftList, 'wlen', wlen);

