% Stim Detection Pipeline

% Note: run pipeline from the "RNS_processing_toolbox" folder

% load configuration settings and toolboxes
clear;
addpath(genpath('matlab_tools'))
rns_config= jsondecode(fileread('config.JSON')); 
nPts = length(rns_config.patients);

%% Get and Save Stimulation Indices

% List of patient IDs to find stims for
ptList = {rns_config.patients.ID};

% Loop finds stimulation start and stop indices and timepoints for all
% patients, then saves result in Device_Stim.mat in the patient's root
% folder if Device_Stim.mat doesn't already exist. 

for ptID = ptList
    
    savepath = ptPth(ptID{1}, rns_config, 'device stim');
   % if exist(savepath, 'file'), continue, end % Skip if already exists

   % Create annotations folder
   if ~exist(ptPth(ptID{1}, rns_config, 'annotations'), 'dir')
       mkdir(ptPth(ptID{1}, rns_config, 'annotations'))
   end
    
    disp(ptID) 
    
    % load patient specific info:
    ecogT = readtable(ptPth(ptID{1}, rns_config, 'ecog catalog'));
    ecogD = matfile(ptPth(ptID{1}, rns_config, 'device data'));
    
   % Get Stimulation times and Indices
   [StimStartStopIndex, StimStats]= findStim(ecogD.AllData, ecogT);
   StimStartStopTimes = idx2time(ecogT, StimStartStopIndex);
   annots = posixtime(StimStartStopTimes) *10^6;
   
   save(savepath, 'annots', 'StimStartStopIndex', 'StimStartStopTimes', 'StimStats')
        
end

%% Check Stim Indices

% Visually check that stimulations are being detected
ptID = ptList{1};
[ecogT, ecogD, stims, ~, pdms] = loadRNSptData(ptID, rns_config);

AllData = ecogD.AllData;

vis_event(AllData, ecogT, stims.StimStartStopIndex)



