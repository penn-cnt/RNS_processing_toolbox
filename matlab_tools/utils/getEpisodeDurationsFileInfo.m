function epDurFileInfo = getEpisodeDurationsFileInfo(rns_config, ecogT)
% epdurFileTbl = getEpisodeDurationsFileInfo(rns_config, ecogT)
% Returns table with episode Duration filepaths and file start/stop dates

ptID = ecogT.PatientID{1}; 

% Create table with paths to all Episode Duration files

pat = sprintf('%s_EpisodeDurations_(?<dt1>\\d*)T(?<t1>\\d*)_(?<dt2>\\d*)T(?<t2>\\d*).csv', ptID);
epfiles = dir(fullfile(ptPth(ptID, rns_config, 'episode durations'), [ptID '*']));

epNames = regexp({epfiles .name}, pat, 'names');
epNameStruct = [epNames{:}];
dt1 = datetime(strcat({epNameStruct.dt1}, {epNameStruct.t1}),'InputFormat', 'yyyyMMddHHmmss'); 
dt2 = datetime(strcat({epNameStruct.dt2}, {epNameStruct.t2}),'InputFormat', 'yyyyMMddHHmmss'); 
paths = string(fullfile({epfiles.folder}, {epfiles.name}));

epDurFileInfo = table(); 
epDurFileInfo.filePath = paths'; 
epDurFileInfo.fileStartUTC = dt1'; 
epDurFileInfo.fileEndUTC = dt2'; 

end