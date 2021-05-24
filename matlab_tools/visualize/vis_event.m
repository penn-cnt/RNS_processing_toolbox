function vis_event(AllData, ecogT, datapoints, options)
% Display event clips containint data points in data points vector. 
%
% Example: 
% vis_event(AllData, Ecog_Events, datapoints)  %datapoints are indices
% vis_event(--, 'Time')                                 %datapoints are timepoints
%
% Inputs: 
%   AllData- vector of data in microseconds
%   Ecog_Events- table of patient events
%   datapoints - vector containing indices of interest, or Nx2 matrix of
%   data windows to view
%
% Output: 
% returns a subplot of the data clip surrounding each datapoint. The datapoint
% and trigger point is marked

arguments
    AllData double
    ecogT table
    datapoints double
    options.Spacing (1,1) double = 300
end

if size(AllData,1) ~= 4
    AllData = AllData';
end

if isvector(datapoints)
    datapoints = datapoints(:);
    windowSetInside = [datapoints, datapoints];
else
    windowSetInside = datapoints;
end

start_ind = ecogT.EventStartIdx;
end_ind = ecogT.EventEndIdx;
windowsetOutside = [start_ind, end_ind];

[incl_inds] = filterWindows(windowsetOutside, windowSetInside); 
alldp = datapoints(:);

disp('Press any key to cycle through visuals')
for i_d = find(incl_inds)'
    figure(1); clf;
    plot(idx2time(ecogT, start_ind(i_d):end_ind(i_d)),...
    AllData(:,start_ind(i_d):end_ind(i_d))'+[1:4]*options.Spacing) 
    dp = logical((alldp >= start_ind(i_d)).*(alldp <= end_ind(i_d)));
    vline(idx2time(ecogT, alldp(dp))); 
    title(sprintf('Event: %s, (%d)', ecogT.ECoGTrigger{i_d}, i_d))
    pause
end



end