%Input to Mat

% load configuration settings
%cd '/Volumes/data/RNS_DataSharing/RNS_Processing_Toolbox'

config= jsondecode(fileread('./config.JSON')); 
nPts = length(config.patients); 

% add toolboxes
addpath(genpath('./conversion'))

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
   
   %[AllData, AllTime]= dat2vector(dataFolder, catalog_csv);
   
   csv_file = readtable(catalog_csv);
   TimeConversionMicroseconds = (posixtime(csv_file.RawUTCTimestamp)-posixtime(csv_file.RawLocalTimestamp))*10^6;
   StartTimes = posixtime(csv_file.Timestamp)*10^6 + TimeConversionMicroseconds; % Convert to UTC
   EcogLengths = csv_file.ECoGLength; % seconds
   EndTimes = StartTimes + EcogLengths*10^6;
       
   save(fullfile(config.paths.MAT_Folder, sprintf('%s.mat', config.patients{i_pt}.RNS_ID)),...
       'AllData', 'AllTime', 'StartTimes', 'EndTimes', 'TimeConversionMicroseconds')
    
end

% Read in Histogram data

% Read in Epoch Duration Data