function [AllData, AllTime_UTC, AllTime_Local] = dat2vector(dataFolder, catalog_csv)
% [AllData, AllTime] = dat2mat(DataPath, NumChannels, CSV
%
% INPUTS-
%   dataFolder: 'path/to/DAT/files/'
%   catlog_csv: 'path/to/ECoG_Catalog.csv'
%
% OUTPUTS-
%   AllData: channels x samples data array 
%   AllTime_UTC: padded time vector in UTC corresponding to AllData
%   AllTime_Local: padded time vector in Local time corresponding to AllData
%   


Folder = dir(fullfile(dataFolder, '*.dat'));
NumberOfFiles = size(Folder,1);

% Read the timestamps from the processed CSV file
csv_file = readtable(catalog_csv);

if height(csv_file) ~= NumberOfFiles
    error('Error: mismatched number of .dat files and ECoG catalog length')
end

if length(unique(csv_file.WaveformCount)) > 1
    error('Error: Multiple WaveformCounts in file')
end

if length(unique(csv_file.SamplingRate)) > 1
    error('Error: Multiple SamplingRates in file')
end

fs = csv_file.SamplingRate(1);
NumChannels = csv_file.WaveformCount(1);
    
% start times & end times in microseconds
startTime_rawUTC = posixtime(csv_file.RawUTCTimestamp)*10^6; 
startTime_rawLocal= posixtime(csv_file.RawLocalTimestamp)*10^6; 


%% Concatenate Data across all DAT files

% prepopulate with estimated size
AllData = NaN(NumChannels, round(sum(csv_file.ECoGLength)*fs));
AllTime_UTC = NaN(round(sum(csv_file.ECoGLength)*fs), 1);
AllTime_Local = NaN(round(sum(csv_file.ECoGLength)*fs), 1);
ctr = 0;

for i_file = 1:NumberOfFiles
    i_file
    % Read Dat File into DATA Variable
    FileIdentifier = fopen(fullfile(dataFolder,csv_file.Filename{i_file}));
    FileData = fread(FileIdentifier,[NumChannels, inf],'int16');
    fclose(FileIdentifier);
  
    dlen = size(FileData,2);
    AllData(:,ctr+(1:dlen)) = FileData;
    t_vec = (1:dlen)/fs - 1/fs;
    
    AllTime_UTC(ctr+(1:dlen)) = startTime_rawUTC(i_file) + t_vec*10^6;
    AllTime_Local(ctr+(1:dlen)) = startTime_rawLocal(i_file) + t_vec*10^6;
    
    ctr = ctr + dlen; 
end
    

end