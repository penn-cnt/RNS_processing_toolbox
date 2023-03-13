% Overview of Patient Data


% load configuration settings
clear;
rns_config= jsondecode(fileread('./config_backup_57160718022023.JSON')); 
nPts = length(rns_config.patients); 

% add toolboxes
addpath(genpath('./matlab_tools'))

ptList = {rns_config.patients.ID};

%% Read in Patient Data

ptID = ptList{1}; %ptList{1};
dateRange = datetime(rns_config.patients(1).UTC_date_range);

[ecogT, ecogD, stims, histT, pdms, OFFSET] = loadRNSptData(ptID, rns_config, 'timeOffset', false,'UTCdateRange', [NaT, dateRange(2)-years(2)]);
AllData = ecogD.AllData;

%% Patient Profile

i_sched = strcmp(ecogT.ECoGTrigger, 'Scheduled');
i_LE = strcmp(ecogT.ECoGTrigger, 'Long_Episode');
i_sat = strcmp(ecogT.ECoGTrigger, 'Saturation');
i_mag = strcmp(ecogT.ECoGTrigger, 'Magnet');

% %% RECORDINGS %% %

% Device Histogram counts over time
figure(10); clf; tiledlayout(2,1); 
nexttile; hold on;
scatter(histT.RegionStartTime, histT.EpisodeStarts, '.');
yyaxis right;
scatter(histT.RegionStartTime, histT.LongEpisodes, '.');
scatter(histT.RegionStartTime, histT.MagnetSwipes, '.');
xline(pdms.Programming_Date, '-.r', 'linewidth', 2)
title(sprintf('Hourly event counts, %s', ptID))
legend({'Episode Starts', 'Long Episode Counts', 'MagnetSwipes'}, 'Location', 'Best')

nexttile;
plot(histT.RegionStartTime, movmean(histT.EpisodeStarts, 100));
yyaxis right; hold on;
plot(histT.RegionStartTime, movmean(histT.LongEpisodes,100));
scatter(histT.RegionStartTime, movmean(histT.MagnetSwipes,100), 'g.');
xline(pdms.Programming_Date, '-.r', 'linewidth', 2)
title(sprintf('Smoothed, hourly event counts, %s', ptID))
legend({'Episode Starts', 'Long Episode Counts', 'MagnetSwipes'}, 'Location', 'Best')


% Recorded Counts over time
figure(4); clf; hold on;
subplot(2,1,1); hold on;
hrs_LE= tabulate(datestr(ecogT.RawLocalTimestamp(i_LE), 'yyyy-mm-dd hh:00:00'));
hrs_sched= tabulate(datestr(ecogT.RawLocalTimestamp(i_sched), 'yyyy-mm-dd hh:00:00'));
hrs_sat= tabulate(datestr(ecogT.RawLocalTimestamp(i_sat), 'yyyy-mm-dd hh:00:00'));
plot(datetime(hrs_LE(:,1)), [hrs_LE{:,2}], 'o')
plot(datetime(hrs_sched(:,1)), [hrs_sched{:,2}] ,'x')
plot(datetime(hrs_sat(:,1)), [hrs_sat{:,2}], '.')
xline(pdms.Programming_Date, '-.r', 'linewidth', 2)
title(sprintf('Recorded EEG events per hour, %s', ptID))
legend('LE', 'Sched', 'Saturations')

subplot(2,1,2); hold on;
hrs_LE= tabulate(datestr(ecogT.RawLocalTimestamp(i_LE), 'yyyy-mm-dd'));
hrs_sched= tabulate(datestr(ecogT.RawLocalTimestamp(i_sched), 'yyyy-mm-dd'));
hrs_sat= tabulate(datestr(ecogT.RawLocalTimestamp(i_sat), 'yyyy-mm-dd'));
plot (datetime(hrs_LE(:,1)), [hrs_LE{:,2}], 'o')
plot(datetime(hrs_sched(:,1)), [hrs_sched{:,2}], 'x')
plot(datetime(hrs_sat(:,1)), [hrs_sat{:,2}], '.')
xline(pdms.Programming_Date, '-.r', 'linewidth', 2)
title(sprintf('Recorded EEG events per day, %s', ptID))
legend('LE', 'Sched', 'Saturations')

days_all= tabulate(datestr(ecogT.RawLocalTimestamp, 'yyyy-mm-dd'));
hrs_all= tabulate(datestr(ecogT.RawLocalTimestamp, 'yyyy-mm-dd hh:00:00'));

fprintf('Max recordings/day: %d, max recordings/hour: %d \n', max([days_all{:,2}]), max([hrs_all{:,2}]))


% Recorded Events Distribution
figure(20); clf; 
subplot(121)
histogram(str2num(datestr(ecogT.Timestamp(i_sched), 'hh')), 24)
title('Scheduled Events 24 hr distribution')
xlabel('hours')
axis tight

subplot(122); hold on;
hrs= str2num(datestr(histT.RegionStartTime, 'hh'));
LE_counts = arrayfun(@(x) sum(histT.LongEpisodes(hrs == x), 'omitnan'), [0:23]);
bar([0:23], LE_counts)
histogram(str2num(datestr(ecogT.Timestamp(i_LE), 'hh')), 24)
title('Recorded Long Episodes 24 hr distribution')
legend('LE Counts', 'Recorded LE')
xlabel('hours')


%% %% STIMULATIONS %% %

figure(3); clf; hold on;
curr = numFromStr(pdms.Current_Tx1_B1); unique(curr)
freq = numFromStr(pdms.Freq_Tx1_B1); 
pw = numFromStr(pdms.PW_Tx1_B1);
dur = numFromStr(pdms.Duration_Tx1_B1);

fprintf('%d current value(s)\n', length(unique(curr(~isnan(curr)))))
fprintf('%d frequency value(s)\n', length(unique(freq(~isnan(freq)))))
fprintf('%d pulse width value(s)\n', length(unique(pw(~isnan(pw)))))
fprintf('%d burst duration value(s)\n', length(unique(dur(~isnan(dur)))))

scatter3(curr(~isnan(curr)), freq(~isnan(freq)), ...
    dur(~isnan(freq)), 50, rescale(posixtime(pdms.Programming_Date(~isnan(freq))))+1, ...
    'filled', 'YJitter', 'density', 'YJitterWidth', 5, 'XJitter', 'density', 'XJitterWidth', .1)
ylabel('Frequency (Hz)')
xlabel('Current (mA)')
zlabel('duration (s)')
ylim([max(freq,[], 'omitnan')/2,max(freq,[], 'omitnan')*1.5])
c = colorbar;
c.Label.String = 'programming date';
c.Ticks = [];

title('Stimulation Paramerers (with jitter)')


%% Group Level Stats

figure(4); clf; 
figure(5); clf;
ctr = 0; 
[yrsRNS, numRecordings, numRecordedDays] = deal(zeros(1, length(ptList))); 
timestamp = {}; 
nstims = {}; 
for ptID = sort(ptList)

ctr = ctr + 1; 

ind = strcmp({patients_Penn.ID}, ptID{1});
metadata = patients_Penn(ind);

[ecogT, ecogD, stims, histT, pdms, OFFSET] = loadRNSptData(ptID{1}, rns_config, 'timeOffset', true);

figure(4); hold on;
curr = numFromStr(pdms.Current_Tx1_B1); unique(curr)
freq = numFromStr(pdms.Freq_Tx1_B1); 
pw = numFromStr(pdms.PW_Tx1_B1);
dur = numFromStr(pdms.Duration_Tx1_B1);

fprintf('%d current value(s)\n', length(unique(curr(~isnan(curr)))))
fprintf('%d frequency value(s)\n', length(unique(freq(~isnan(freq)))))
fprintf('%d pulse width value(s)\n', length(unique(pw(~isnan(pw)))))
fprintf('%d burst duration value(s)\n', length(unique(dur(~isnan(dur)))))


scatter3(curr(~isnan(curr)), freq(~isnan(freq)), ...
    dur(~isnan(freq)), 50, days(pdms.Programming_Date(~isnan(freq))- min(pdms.Programming_Date)),...
    'filled', 'YJitter', 'density', 'YJitterWidth', 5, 'XJitter', 'density', 'XJitterWidth', .1)
ylabel('Frequency (Hz)')
xlabel('Current (mA)')
zlabel('duration')
c = colorbar;
c.Label.String = 'days since implant';


figure(5); hold on;
scatter(ecogT.Timestamp, ctr*ones(1,height(ecogT)), '.')


yrsRNS(ctr) = years(max(ecogT.Timestamp) - min(ecogT.Timestamp));
numRecordings(ctr) = height(ecogT);
numRecordedDays(ctr) = length(unique(string(datestr(ecogT.Timestamp, 'yyyy-mm-dd'))));

timestamp{ctr} = pdms.Programming_Date;
nstims{ctr} = pdms.Therapies_per_day;

end

figure(4); title(sprintf('Stim parameter sets across %d patients', length(ptList)))
figure(5); yticks([1:ctr]); yticklabels(sort(ptList)); title(sprintf('Data coverage in %d patients', ctr))
figure(6); clf;
nexttile; histogram(yrsRNS, 10); xlabel('years'); ylabel('# patients')
title(sprintf('Years with RNS (%0.1f ± %0.1f)', mean(yrsRNS), std(yrsRNS)))
nexttile; histogram(numRecordings, 10); xlabel('# clips')
title(sprintf('Total recorded clips (%0.1f ± %0.1f)', mean(numRecordings), std(numRecordings)))
nexttile; histogram(numRecordedDays, 10); xlabel('# clips')
title(sprintf('# days with recordings (%0.1f ± %0.1f)', mean(numRecordedDays), std(numRecordedDays)))
sgtitle('RNS Patient Data Record Summary')

pth = '/Users/bscheid/Documents/LittLab/PROJECTS/p06_RNS_IEEG_Biomarkers/RNS_Summary_Figs';

saveas(figure(4), fullfile(pth, 'groupLevel_stimParameters'), 'png')
saveas(figure(5), fullfile(pth, 'groupLevel_dataCoverage'), 'png')
saveas(figure(6), fullfile(pth, 'groupLevel_numEventSummary'), 'png')


