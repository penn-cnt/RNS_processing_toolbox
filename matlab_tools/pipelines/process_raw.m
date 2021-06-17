% process_raw script
% ------------------------------------------------------
% Convert .DAT files to .MAT files, place in MAT_Folder
% ------------------------------------------------------

% load configuration settings
config= jsondecode(fileread('./config.JSON')); 
nPts = length(config.patients); 

% add toolboxes
addpath(genpath('./matlab_tools'))

if ~exist(config.paths.MAT_Folder, 'dir')
    mkdir(config.paths.MAT_Folder); 
end

%% Convert DAT files to MAT files

for i_pt = 1:nPts
    
   prefix = sprintf('%s_%s_%s', ...
       config.institution, config.patients(i_pt).Initials, ...
       config.patients(i_pt).PDMS_ID); 
    
   dataFolder = fullfile(config.paths.DAT_Folder, [prefix, ' EXTERNAL #PHI'], [prefix, ' Data EXTERNAL #PHI']);
   catalog_csv= fullfile(config.paths.DAT_Folder, [prefix, ' EXTERNAL #PHI'], [prefix, '_ECoG_Catalog.csv']);
   
   savepath = fullfile(config.paths.MAT_Folder, sprintf('%s.mat', config.patients(i_pt).RNS_ID));
   
   % Get converted Data and Time vectors 
   [AllData, AllTime, eventIdx]= dat2vector(dataFolder, catalog_csv);
   save(savepath, 'AllData', 'AllTime', 'eventIdx')
   
   % Get Stimulation times and Indices
   [StimStartStopIndex, StimStartStopTimes, StimGap, StimStats]= findStim(AllData, AllTime);
   save(savepath, 'StimStartStopIndex', 'StimStartStopTimes', 'StimStats', '-append')
   
   % Add in additional metadata
   Ecog_Events = readtable(catalog_csv);
   Ecog_Events = removevars(Ecog_Events, {'Initials', 'PatientID', 'DeviceID'});
   Ecog_Events.eventStartIdx = eventIdx(:,1); 
   Ecog_Events.eventEndIdx = eventIdx(:,2);
   save(savepath, Ecog_Events', '-append')
   
    
end

%% Get Stimulation Indices

i_pt = 5;

pt_path = fullfile(config.paths.MAT_Folder, sprintf('%s_py.mat', config.patients(i_pt).RNS_ID));

tic
load(pt_path)
toc
