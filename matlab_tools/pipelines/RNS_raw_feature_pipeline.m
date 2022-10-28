function [fts, flabels, windows_info] = RNS_raw_feature_pipeline(ptID, rns_config, options)
% RNS_RAW_FEATURE_PIPELINE Calculate features in windows on raw RNS data for ptID.
%
% [fts, flabels, windows_info] = RNS_RAW_FEATURE_PIPELINE(ptID, rns_config, options)
%
%   ptID: patient ID
%   rns_config: rns_config file
%   options: 
%       ftlist: cell array of 'll' (line length), 'bp' (bandpower), 'plv' (phase locking value)
%       wlen: window length (in seconds) to calculate features over
%


arguments
    ptID string
    rns_config
    options.ftlist = {'ll', 'bp', 'plv'}; % Features to calculate
    options.wlen = 2                      % window length in seconds

end


fs = 250;
wlen_samp = fs * options.wlen;

[ecogT, ecogD] = loadRNSptData(ptID, rns_config, "timeOffset", true);

% Compute window Indices 
nwind = floor((ecogT.EventEndIdx- ecogT.EventStartIdx)/wlen_samp);
windows_idx = arrayfun(@(x) [ecogT.EventStartIdx(x)+[0:nwind(x)-1]'*wlen_samp, ...
                         ecogT.EventStartIdx(x)+[1:nwind(x)]'*wlen_samp-1], ...
                         [1:length(nwind)], 'Uni',0);
windows_idx(cellfun(@isempty, windows_idx)) = []; nwind = length(windows_idx);
assert(any(arrayfun(@(x) ecogT.EventEndIdx(x) < windows_idx{x}(end), [1:length(nwind)])') == 0)
windows_idx = cell2mat(windows_idx'); 
windows_posixtime = idx2time(ecogT, windows_idx, 'format', 'posixtime');
event_idx = idx2event(ecogT, windows_idx(:,1));

windows_info.data_idx = windows_idx;
windows_info.posixtime = windows_posixtime; 
windows_info.event_idx = event_idx;

% Compute Features
fprintf('computing features for %s \n', ptID)
[fts, flabels] = getFeatures(windows_idx, ecogD.AllData, fs, options.ftlist);



end


