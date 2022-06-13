function [ecogT, ecogD, stims, histT, pdms, OFFSET] = loadRNSptData(ptID, rns_config, options)
% [ecogT, ecogD, stims, histT, pdms] = loadRNSptData(ptID, rns_config, options)
% Outputs will be returned as empty vectors if they don't exist. 
%
%  INPUT:
%       ptID (string): patient ID
%       rns_config (struct): rns config.JSON struct
%       options: 
%          - 'timeOffset' (true/false): sets all time to start on Jan 1st, 1970
%
% OUTPUT:
    
    arguments
        ptID
        rns_config
        options.timeOffset logical = false
    end

    warning('off','MATLAB:table:ModifiedAndSavedVarnames')
   
    ecogT = readtable(ptPth(ptID, rns_config, 'ecog catalog'));
    ecogD = matfile(ptPth(ptID, rns_config, 'device data'));

    try
        stims = load(ptPth(ptID, rns_config, 'device stim'));
    catch
        warning('Could not find stim data at %s',ptPth(ptID, rns_config, 'device stim'))
        stims = [];
    end

    try
        histT = readtable(ptPth(ptID, rns_config, 'hourly histogram'));
        minHist = min(histT.RegionStartTime, histT.UTCStartTime);
    catch
        warning('Could not find stim data at %s',ptPth(ptID, rns_config, 'hourly histogram'))
        histT = [];
        minHist = datetime('now');
    end
    
    try
        pdmsPth = ptPth(ptID, rns_config, 'pdms');
        allpdms = readtable(pdmsPth);  
        pdms = allpdms(contains(allpdms.id_code, ptID),:);

        if any(year(pdms.Programming_Date) < 2000)
            pdms.Programming_Date = pdms.Programming_Date + calyears(2000);
        end

        minPDMS = min(pdms.Programming_Date);

    catch
        warning('Could not find pdms data at %s',pdmsPth)
        pdms = [];
        minPDMS= datetime('now'); 
    end

    OFFSET = 0; 

    if options.timeOffset
        MINDATE = min([minPDMS; ecogT.Timestamp; ecogT.RawLocalTimestamp;...
            ecogT.RawUTCTimestamp; minHist]);
        OFFSET = MINDATE - datetime(0, 'convertFrom', 'posixtime');
        
        % TimeShift all using OFFSET 
        ecogT.Timestamp = ecogT.Timestamp - OFFSET;
        ecogT.RawLocalTimestamp = ecogT.RawLocalTimestamp - OFFSET;
        ecogT.RawUTCTimestamp = ecogT.RawUTCTimestamp - OFFSET;
        if ~isempty(stims), stims.StimStartStopTimes = stims.StimStartStopTimes - OFFSET; end
        if ~isempty(pdms), pdms.Programming_Date = pdms.Programming_Date - OFFSET; end
        if ~isempty(histT)
            histT.RegionStartTime = histT.RegionStartTime - OFFSET;
            histT.UTCStartTime = histT.UTCStartTime - OFFSET; 
        end   
    end
        
end