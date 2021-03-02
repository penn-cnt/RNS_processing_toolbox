function path = ptPth(ptID, config, dataName)
% INPUT:
%   dataName: ecog catalog, hourly histogram, daily histogram, device data,
%   device stim, episode durations
% OUTPUT: filepath (string)
    prefix = fullfile(config.paths.RNS_DATA_Folder, ptID);
    
    switch(lower(dataName))
        case {'root'}, path = prefix;
        case {'ecog catalog'}, path = fullfile(prefix,'ECoG_Catalog.csv');
        case {'hourly histogram'}, path = fullfile(prefix,'Histograms','Histogram_Hourly.csv');
        case {'daily histogram'}, path = fullfile(prefix,'Histograms','Histogram_Daily.csv'); 
        case {'device data'}, path = fullfile(prefix,'Device_Data.mat');
        case {'device stim'}, path = fullfile(prefix,'Device_Stim.mat');
        case {'episode durations'}, path = fullfile(prefix,'EpisodeDurations');
        case {'pdms'}, path= fullfile(config.paths.RNS_DATA_Folder, 'PDMS.csv'); 
        otherwise, path = 'File/Folder not found'; disp(path);
    end
            
            

end
