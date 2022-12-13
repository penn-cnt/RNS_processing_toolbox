function [set1_inclusive_inds, set1_exclusive_inds, set2_included_inds]=filterWindows(windowsetOutside, windowsetInside)
% [set1_inclusive_inds, set1_exclusive_inds, set2_included_inds] = filterWindows(windowsetOutside, windowsetInside)
% Returns List where windowsetOutside _inculdes_ the entirety of
% windowsetInside, and where windowsetOutside excludes the entirety of
% windowsetInside.

% set1_inclusive_inds: indices of windows in windowsetOutside that overlap
% windows of windowsetInside
% set1_exclusive_inds: indices of windows in windowsetOutside that have no
% overlap with windowsetInside
% set2_included_inds: indices of windowsetInside that are fully contained
% by 

if isvector(windowsetInside)
    if length(windowsetInside) == 2 && isrow(windowsetInside)
        warning(['One window in windowsetInside found. Input a column vector if ' ...
            'windowsetInside should be interpreted as two individual datapoints.'])
    else
        windowsetInside = [windowsetInside(:), windowsetInside(:)];
    end
end

% window start is between stim bounds
noStim_inds1=arrayfun(@(x)sum((x >= windowsetInside(:,1)).* (x<= windowsetInside(:,2)))==0, windowsetOutside(:,1));

% window end is between stim bounds
noStim_inds2=arrayfun(@(x)sum((x >= windowsetInside(:,1)).* (x<= windowsetInside(:,2)))==0, windowsetOutside(:,2));

% window contains both stim bounds
noStim_inds3=arrayfun(@(i)sum((windowsetOutside(i,1) <= windowsetInside(:,1)).* (windowsetOutside(i,2) >= windowsetInside(:,2)))== 0, (1:size(windowsetOutside,1)));

set1_exclusive_inds = logical(noStim_inds1.*noStim_inds2.*noStim_inds3');
set1_inclusive_inds = ~set1_exclusive_inds;

set2_included_inds = arrayfun(@(i)sum((windowsetInside(i,1) >= windowsetOutside(:,1)).*...
    (windowsetInside(i,2) <= windowsetOutside(:,2)))==1, (1:size(windowsetInside,1)));


end