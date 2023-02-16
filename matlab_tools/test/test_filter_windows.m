
win1 = [[1,3];
        [6,7];
        [10,12];
        [13,16];
        [18,21];
        [24,26];
        [25,27];
        [31,32]];

win2 = [[2,4];
        [5,8];
        [9,11];
        [14,15];
        [17,20];
        [19,22];
        [23,28];
        [29, 30];
        [33,34]];

[incl1, excl1, set2] = filterWindows(win1, win2);
[incl2, excl2, set1] = filterWindows(win2, win1);


figure(1); clf; hold on;
plot(win1', ones(length(win1), 2)', 'red')
scatter(mean(win1(incl1,:),2), ones(sum(incl1),1)*1.2, 'green', 'filled')
scatter(mean(win1(excl1,:),2), ones(sum(excl1),1)*1.3, 'red', 'filled')
plot(win2', 2.*ones(length(win2), 2)', 'blue')
scatter(mean(win2(incl2,:),2), ones(sum(incl2),1)*2.2, 'green', 'filled')
scatter(mean(win2(excl2,:),2), ones(sum(excl2),1)*2.3, 'red', 'filled')
scatter(mean(win2(set2,:),2), ones(sum(set2),1)*1.9, 'black', 'filled')
yticks([1,2]); yticklabels({'win1', 'win2'})
ylim([0, 3])


