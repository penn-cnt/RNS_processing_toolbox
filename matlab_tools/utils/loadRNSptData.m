function [ecogT, ecogD, stims, histT, pdms, OFFSET] = loadRNSptData(ptID, rns_config, options)
% [ecogT, ecogD, stims, histT, pdms] = loadRNSptData(ptID, rns_config, options)
%  INPUT:
%       ptID (string): patient ID
%       rns_config (struct): rns config.JSON struct
%       options: 
%          - 'timeOffset' (true/false): sets all time to start on Jan 1st, 1970
%
    
    arguments
        ptID
        rns_config
        options.timeOffset logical = false
    end

    warning('off','all')
   
    ecogT = readtable(ptPth(ptID, rns_config, 'ecog catalog'));
    ecogD = matfile(ptPth(ptID, rns_config, 'device data'));
    stims = load(ptPth(ptID, rns_config, 'device stim'));
    histT = readtable(ptPth(ptID, rns_config, 'hourly histogram'));
    
    try
        pdmsPth = ptPth(ptID, rns_config, 'pdms');
        allpdms = readtable(pdmsPth);  
        pdms = allpdms(contains(allpdms.id_code, ptID),:); 
    catch
        warning('Could not find pdms data at %s',pdmsPth)
        pdms = [];
    end

    OFFSET = 0; 

    if options.timeOffset
        MINDATE = min([pdms.Programming_Date; ecogT.Timestamp; ecogT.RawLocalTimestamp;...
            ecogT.RawUTCTimestamp; histT.RegionStartTime; histT.UTCStartTime]);
        OFFSET = MINDATE - datetime(0, 'convertFrom', 'posixtime');
        
        % TimeShift all using OFFSET 
        pdms.Programming_Date = pdms.Programming_Date - OFFSET;
        ecogT.Timestamp = ecogT.Timestamp - OFFSET;
        ecogT.RawLocalTimestamp = ecogT.RawLocalTimestamp - OFFSET;
        ecogT.RawUTCTimestamp = ecogT.RawUTCTimestamp - OFFSET;
        histT.RegionStartTime = histT.RegionStartTime - OFFSET;
        histT.UTCStartTime = histT.UTCStartTime - OFFSET; 
        stims.StimStartStopTimes = stims.StimStartStopTimes - OFFSET;
        
    end
        
end