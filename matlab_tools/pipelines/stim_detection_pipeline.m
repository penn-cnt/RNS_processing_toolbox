% Stim Detection Pipeline

% Note: run pipeline from the "RNS_processing_toolbox" folder

% load configuration settings and toolboxes
addpath(genpath('matlab_tools'))
config= jsondecode(fileread('config.JSON')); 
nPts = length(config.patients);

%% Get and Save Stimulation Indices

% List of patient IDs to find stims for
ptList = {config.patients.ID};

% Loop finds stimulation start and stop indices and timepoints for all
% patients, then saves result in Device_Stim.mat in the patient's root
% folder if Device_Stim.mat doesn't already exist. 

for ptID = ptList
    
    savepath = ptPth(ptID{1}, config, 'device stim');
    if exist(savepath, 'file'), continue, end % Skip if already exists
    
    disp(ptID) 
    
    % load patient specific info:
    ecogT = readtable(ptPth(ptID{1}, config, 'ecog catalog'));
    ecogD = matfile(ptPth(ptID{1}, config, 'device data'));
    
   % Get Stimulation times and Indices
   [StimStartStopIndex, StimStats]= findStim(ecogD.AllData);
   StimStartStopTimes = idx2time(ecogT, StimStartStopIndex);
   
   save(savepath, 'StimStartStopIndex', 'StimStartStopTimes', 'StimStats')
        
end

%% Check Stim Indices

% Visually check that stimulations are being detected
ptID = {'HUP096'};
ecogT = readtable(ptPth(ptID{1}, config, 'ecog catalog'));
ecogD = matfile(ptPth(ptID{1}, config, 'device data'));
load(fullfile(ptPth(ptID{1}, config, 'root'), 'Device_Stim.mat'));

AllData = ecogD.AllData;

vis_event(AllData, ecogT, StimStartStopIndex)

%% Example

% Retrive indices of all scheduled events that include or exclude
% stimulation windows. Filter windows takes two sets of windows (or a set
% of windows and a vector of points), and returns indices of the first
% window set that include and exclude the windows or points in the second
% set.

% Get start and stop indices of all secheduled events
i_sched = find(strcmp(ecogT.ECoGTrigger, 'Scheduled'));
evntIdx= ecogT{i_sched, {'EventStartIdx', 'EventEndIdx'}};

[incl, excl] = filterWindows(evntIdx, StimStartStopIndex); 

vis_event(AllData, ecogT, evntIdx(excl))


