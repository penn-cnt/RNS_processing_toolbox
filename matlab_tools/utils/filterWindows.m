function [inclusive_inds, exclusive_inds]=filterWindows(windowsetOutside, windowsetInside)
% Returns List where windowsetOutside _inculdes_ the entirety of
% windowsetInside, and where windowsetOutside excludes the entirety of
% windowsetInside.

% window start is between stim bounds
noStim_inds1=arrayfun(@(x)sum((x >= windowsetInside(:,1)).* (x<= windowsetInside(:,2)))==0, windowsetOutside(:,1));

% window end is between stim bounds
noStim_inds2=arrayfun(@(x)sum((x >= windowsetInside(:,1)).* (x<= windowsetInside(:,2)))==0, windowsetOutside(:,2));

% window contains both stim bounds
noStim_inds3=arrayfun(@(i)sum((windowsetOutside(i,1) <= windowsetInside(:,1)).* (windowsetOutside(i,2) >= windowsetInside(:,2)))== 0, (1:size(windowsetOutside,1)));

exclusive_inds = logical(noStim_inds1.*noStim_inds2.*noStim_inds3');
inclusive_inds = ~exclusive_inds;

% wind_no_stim= windowsetOutside(all_no_stim_inds,:);
% wind_stim= windowsetOutside(~all_no_stim_inds,:);

end