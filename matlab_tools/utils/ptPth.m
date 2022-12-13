function path = ptPth(ptID, rns_config, dataName)
% INPUT:
%   ptID (string): patient ID
%   config (struct): config struct
%   dataName (string): root,
%                      ecog catalog,
%                      hourly histogram,
%                      daily histogram,
%                      device data,
%                      device stim,
%                      episode durations
% OUTPUT: filepath (string)

    arguments

        ptID
        rns_config
        dataName string {mustBeMember(dataName, {'root', 'ecog catalog', ...
            'hourly histogram', 'daily histogram', 'device data', ...
            'device stim', 'episode durations', 'recorded detections', ...
            'pdms', 'annotations'})}
    end

    prefix = fullfile(rns_config.paths.RNS_DATA_Folder, ptID);
    
    switch(lower(dataName))
        case {'root'}, path = prefix;
        case {'ecog catalog'}, path = fullfile(prefix,'ECoG_Catalog.csv');
        case {'hourly histogram'}, path = fullfile(prefix,'Histograms','Histogram_Hourly.csv');
        case {'daily histogram'}, path = fullfile(prefix,'Histograms','Histogram_Daily.csv'); 
        case {'device data'}, path = fullfile(prefix,'Device_Data.mat');
        case {'device stim'}, path = fullfile(prefix, 'Annotations', 'Device_Stim.mat');
        case {'episode durations'}, path = fullfile(prefix,'EpisodeDurations');
        case {'recorded detections'}, path = fullfile(prefix, 'recDetect.mat');
        case {'pdms'}, path= fullfile(rns_config.paths.RNS_DATA_Folder, 'PDMS.csv'); 
        case {'annotations'}, path = fullfile(prefix,'Annotations');
        otherwise, path = 'File/Folder not found'; disp(path);
    end
            
            

end
