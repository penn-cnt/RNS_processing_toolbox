function vis_event(AllData, AllTime, Ecog_Events, datapoints)
% Display event clips containint data points in data points vector. 

% Example: 
% vis_event(AllData, AllTime, Ecog_Events, datapoints)  %datapoints are indices
% vis_event(--, 'Time')                                 %datapoints are timepoints

% Inputs: 
%   AllData- vector of data in microseconds
%   AllTime- vector of time in microseconds
%   Ecog_Events- table of patient events
%   datapoints - vector containing indices or timepoints (in uS) of interest

% Output: 
% returns a subplot of the data clip surrounding each datapoint. The datapoint
% and trigger point is marked


datapoints = datapoints(:);
ld = length(datapoints); 


StartIndices = Ecog_Events.eventStartIdx;
EndIndices = Ecog_Events.eventEndIdx;

[~, imin] = min(abs(StartIndices - datapoints'));

start_ind = StartIndices(imin);
end_ind = EndIndices(imin);
events = Ecog_Events.eventType;


figure(1); clf; hold on
for i_d = 1:ld
    subplot(ld,1,i_d); hold on;
    plot(datetime(AllTime(start_ind(i_d):end_ind(i_d))/10^6, 'ConvertFrom', 'Posixtime'),...
    AllData(:,start_ind(i_d):end_ind(i_d))'+[1:4]*100) 
    vline(datapoints(i_d)); 
    title(sprintf('Event: %s', events{i_d}))
end



end