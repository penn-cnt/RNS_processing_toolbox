function [AllData, AllTime_UTC, eventIdx] = dat2vector(dataFolder, catalog_csv)
% [AllData, AllTime] = dat2mat(DataPath, NumChannels, CSV
%
% INPUTS-
%   dataFolder: 'path/to/DAT/files/'
%   catlog_csv: 'path/to/ECoG_Catalog.csv'
%
% OUTPUTS-
%   AllData: channels x samples data array 
%   AllTime_UTC: padded time vector in UTC corresponding to AllData
%   eventIdx: matrix with start and stop indices corresponding to each
%             event in the AllTime and AllData arrays. 


Folder = dir(fullfile(dataFolder, '*.dat'));
NumberOfFiles = size(Folder,1);

% Read the timestamps from the processed CSV file
csv_file = readtable(catalog_csv);

% Check for any errors before proceeding
if height(csv_file) ~= NumberOfFiles
    error('Error: mismatched number of .dat files and ECoG catalog length')
end

if length(unique(csv_file.SamplingRate)) > 1
    error('Error: Multiple SamplingRates in file')
end

if ~isempty(find(diff(csv_file.RawUTCTimestamp)<0))
    error('Error: RawUTCTimestamp is not chronological')
end

fs = csv_file.SamplingRate(1);
    
% start times & end times in microseconds
startTime_rawUTC = posixtime(csv_file.RawUTCTimestamp)*10^6; 


%% Concatenate Data across all DAT files

% prepopulate with estimated size
AllData = NaN(4, round(sum(csv_file.ECoGLength)*fs));
AllTime_UTC = NaN(round(sum(csv_file.ECoGLength)*fs), 1);
eventIdx = zeros(NumberOfFiles,2); 
ctr = 0;

for i_file = 1:NumberOfFiles
    
    disp(i_file)
    
    cse = csv_file(i_file,:);
    % Read Dat File into DATA Variable
    FileIdentifier = fopen(fullfile(dataFolder,cse.Filename{1}));
    NumChannels = cse.WaveformCount;
    FileData = fread(FileIdentifier,[NumChannels, inf],'int16');
    fclose(FileIdentifier);
    
    % Pad channels with zeros if they are turned off
    isoff= [strcmp(cse.Ch1Enabled, 'Off'), strcmp(cse.Ch2Enabled, 'Off'),...
    strcmp(cse.Ch3Enabled, 'Off'), strcmp(cse.Ch4Enabled, 'Off')];
    FileData(isoff,:) = zeros(sum(isoff),size(FileData,2)); 
    
    % add to AllData and AllTime vectors
    dlen = size(FileData,2);
    AllData(:,ctr+(1:dlen)) = FileData;
    t_vec = (1:dlen)/fs - 1/fs;
    
    AllTime_UTC(ctr+(1:dlen)) = startTime_rawUTC(i_file) + t_vec*10^6;
    
    eventIdx(i_file,:) = ctr+[1, dlen]; % 
    ctr = ctr + dlen; 
end
    

end