function usecTime = idx2time(ecogT, idx, options)
% usecTime = idx2time(ecogT, idx, options)
% USAGE: Convert AllTime indices to microsecond times (either UTC or local,
%        formatted as datetime objects or posixtime). 
% INPUTS:
%   ecogT (table): table from ecog_catalog.csv
%   idx (numeric): vector or matrix of AllData indices to convert to times
%   Options: 
%       'timezone': 'UTC' (default), 'local'
%       'format': 'datetime' (default), 'posixtime'
%
% OUTPUT: 
%   usecTime: vector or matrix with time output in same dimensions as idx
%
%  Example: 
%     ecogT = readtable(ptPth(ptID, config, 'ecog catalog'))
%     usecTime = idx2Time(ecogT, [20, 593, 60394], 'timezone', 'local')
%

arguments
    ecogT table
    idx {mustBeNumeric}
    options.timezone (1,1) string = 'UTC'
    options.format (1,1) string = 'datetime'
end

if isvector(idx) && ~iscolumn(idx)
    idx = idx';
end

if strcmp(options.timezone, 'UTC')
    timeconversion = ecogT.RawUTCTimestamp - ecogT.RawLocalTimestamp;
    times = ecogT.Timestamp + timeconversion;
else
    times = ecogT.Timestamp;
end

usecTime = NaT(size(idx), 'format','yyyy-MM-dd HH:mm:ss.SSS');
fs = ecogT.SamplingRate(1);

for i_col = (1:size(idx, 2))

   % Convoluted but computationaly fast, find 5 nearest start times to each index 
   [~,i] = pdist2(ecogT.EventStartIdx, idx(:,i_col),'euclidean', 'Smallest', 5);
   ds = idx(:,i_col)'-ecogT.EventStartIdx(i);
   
   % Get smallest non-zero index:
   ds(ds<0) = nan;
   [~, i_min]= min(ds, [], 1);
   sub= sub2ind(size(ds),i_min, [1:size(ds,2)]);
   usecTime(:,i_col) = times(i(sub))+seconds(ds(sub)/fs)';  
    
end

if strcmp(options.format, 'posixtime')
    usecTime = posixtime(usecTime)*10^6;
end

end
