% Episode Detection Pipeline

% Compiles a table of all device detections that occur during EcoG recordings.
% Saves as recDetectT.mat in the patient's folder. 

% Note: run pipeline from the "RNS_processing_toolbox" folder
% Note: Only runs if patients have Episode Durations folder available.

% load configuration settings and toolboxes
addpath(genpath('matlab_tools'))
rns_config= jsondecode(fileread('config.JSON')); 

%% Get and Save Stimulation Indices

% List of patient IDs to find stims for
ptList = {rns_config.patients.ID};

for ptID = ptList

    ecogT = loadRNSptData(ptID{1}, rns_config);
    recDetectT = getDetectionsInRecordedEvents(rns_config, ecogT);
    save(ptPth(ptID{1}, rns_config, 'recorded detections'), 'recDetectT')

end

%% Visualize Detections

ptID = ptList{1}; 

[ecogT, ecogD, stims] = loadRNSptData(ptID, rns_config);
AllData = ecogD.AllData; 
load(ptPth(ptID, rns_config, 'recorded detections'));

detectTypes = {'A1Detect', 'A2Detect', 'B1Detect', 'B2Detect'}';
counts = recDetectT{:, detectTypes} * (1:4)';
labels = detectTypes(counts);


% Plot all detections
vis_event(AllData, ecogT, recDetectT.EpisodeStartIdx, 'labels',labels)
vis_event(AllData, ecogT, stims.StimStartStopIndex)


