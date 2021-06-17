function eventIdx = idx2event(ecogT, idx)
% eventIdx = idx2event(ecogT, idx)
%
% USAGE: Get event index from index into allData. Note, events may overlap
% but a single allData index corresponds to a single event
% INPUTS:
%   ecogT (table): table from ecog_catalog.csv
%   idx (numeric): vector or matrix of indices into the data matrix, to map
%   to events in ecogT
%   Options: 
%
% OUTPUT: 
%   eventIdx: array or vector with corresponding eventIndices 
%
%  Example: 
%     ecogT = readtable(ptPth(ptID, config, 'ecog catalog'))
%     eventIdx= idx2Tevent(ecogT, [20, 593, 60394])
%

arguments
    ecogT table
    idx {mustBeNumeric}
end

if isvector(idx) && ~iscolumn(idx)
    idx = idx';
end

evntIdx = nan(size(idx));

for i_col = (1:size(idx, 2))

   % Convoluted but computationaly fast, find 5 nearest start times to each index 
   [~,i] = pdist2(ecogT.EventStartIdx, idx(:,i_col),'euclidean', 'Smallest', 5);
   ds = idx(:,i_col)'-ecogT.EventStartIdx(i);
   
   % Get smallest non-zero index:
   ds(ds<0) = nan;
   [~, i_min]= min(ds, [], 1);
   sub= sub2ind(size(ds),i_min, [1:size(ds,2)]);
   eventIdx(:,i_col) = i(sub);  
    
end

end