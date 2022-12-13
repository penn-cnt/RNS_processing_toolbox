function recDetectT = getDetectionsInRecordedEvents(rns_config, ecogT)
% recDetectT = getDetectionsInRecordedEvents(rns_config, ecogT)
%
% Returns a table of recorded detections, captured in the ecog recordings.
%

ptID = ecogT.PatientID{1}; 

% Get Paths to all epDur Files
epfileFolder = dir(fullfile(ptPth(ptID, rns_config, 'episode durations'), [ptID '*']));
epDurPaths = string(fullfile({epfileFolder.folder}, {epfileFolder.name}));

% Get file start/stop times for each episode duration csv. 
pat = sprintf('%s_EpisodeDurations_(?<dt1>\\d*)T(?<t1>\\d*)_(?<dt2>\\d*)T(?<t2>\\d*).csv', ptID);
epNames = regexp({epfileFolder.name}, pat, 'names');
epNameStruct = [epNames{:}];
dt1 = datetime(strcat({epNameStruct.dt1}, {epNameStruct.t1}),'InputFormat', 'yyyyMMddHHmmss')'; 
dt2 = datetime(strcat({epNameStruct.dt2}, {epNameStruct.t2}),'InputFormat', 'yyyyMMddHHmmss')'; 
fileWins = [dt1, dt2];

% Get UTC start/stop times of all ecog events
ecogT_Starttimes = ecogT.RawUTCTimestamp - seconds(ecogT.ECoGPre_triggerLength);
ecogT_Endtimes = ecogT.RawUTCTimestamp - seconds(ecogT.ECoGPre_triggerLength) + seconds(ecogT.ECoGLength);
ecog_wins = [ecogT_Starttimes, ecogT_Endtimes];

% get only the epDur files that intersect with ecogs to save loading time
inclEcog = filterWindows(fileWins, ecog_wins)';

% Loop through EpisodeDuration csv files, pull lines that fall in ECoG events.
recDetectT = table(); 
ctr = 1; 
fprintf('Compiling detections from %d episode durations files, this may take a while...\n', sum(inclEcog));
for i_file = find(inclEcog)

    epDurFile = readtable(epDurPaths(i_file));

    % start/stop time windows of detections
    epDurFile.UTCEndTime =  epDurFile.UTCStartTime + seconds(epDurFile.Duration);
    durWins = [epDurFile.UTCStartTime, epDurFile.UTCEndTime];

    % Get EcoGs that contain detections in file
    ecogInclDur = filterWindows(ecog_wins, durWins);
    ecogInclDur = find(ecogInclDur)';

    % Add Info to Table
    for i_inclDur = ecogInclDur

        [~,~,inEcog] = filterWindows(ecog_wins(i_inclDur,:), durWins);

        detections = epDurFile(inEcog,:);
        detectStartIdx = seconds(detections.UTCStartTime - ecogT_Starttimes(i_inclDur))*250 + ecogT.EventStartIdx(i_inclDur);
        detectEndIdx = seconds(detections.UTCEndTime - ecogT_Starttimes(i_inclDur))*250 + ecogT.EventStartIdx(i_inclDur);

        tmp_tbl = epDurFile(inEcog,:);
        tmp_tbl(:,{'RegionDataRangeStart', 'RegionDataRangeEnd', 'TimezoneRegion'}) = [];
        tmp_tbl.evt_idx(:) = i_inclDur;
        tmp_tbl.EpisodeStartIdx = detectStartIdx;
        tmp_tbl.EpisodeEndIdx = detectEndIdx;

        recDetectT = [recDetectT; tmp_tbl];

    end

    if mod(ctr, 20) == 0
        fprintf('loaded %d / %d episodeDuration files \n', ctr, sum(inclEcog))
    end

    ctr = ctr + 1; 


end



end