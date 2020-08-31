%Input to Mat

% load configuration settings
%cd '/Volumes/data/RNS_DataSharing/RNS_Processing_Toolbox'

config= jsondecode(fileread('../config_mounted.JSON')); 
nPts = length(config.patients); 

% add toolboxes
addpath(genpath('../conversion'))

% ------------------------------------------------------
% Convert .DAT files to .MAT files, place in MAT_Folder
% ------------------------------------------------------

if ~exist(config.paths.MAT_Folder, 'dir')
    mkdir(config.paths.MAT_Folder); 
end


for i_pt = 1:nPts
    
   prefix = sprintf('%s_%s_%s', ...
       config.institution, config.patients{i_pt}.Initials, ...
       config.patients{i_pt}.PDMS_ID); 
    
   dataFolder = fullfile(config.paths.DAT_Folder, [prefix, ' EXTERNAL #PHI'], [prefix, ' Data EXTERNAL #PHI']);
   catalog_csv= fullfile(config.paths.DAT_Folder, [prefix, ' EXTERNAL #PHI'], [prefix, '_ECoG_Catalog.csv']);
   
   [AllData, AllTime]= dat2vector(dataFolder, catalog_csv); 
    
    
    
    
end

% Read in Histogram data

% Read in Epoch Duration Data