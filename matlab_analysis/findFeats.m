%% Calculate the Features

%% Find the Stimulations
[StimStartIndex,StimEndIndex,StimStartTimes,StimEndTimes, StimGap,...
StimLengths,MaxStimLength, MinStimLength, MaxStimIndex, MinStimIndex, UTCStartTimes, NumStims]=...
findStim(AllData, AllTime);

%% Calculate Post Stim Start Times
%Load the Clinical Reprogramming Dates
load('AAClinicalReprogramming.mat')

% Define amount of time after stim discarded because of artifacts
PostBuffer=200;
%Sampling Frequency
Fs=250;

%Define length of stimulation window in Units
WindowLength=1000;

%Calcualte Indeces of Post Stim
PostStimStartIndex=StimEndIndex+PostBuffer;
PostStimEndIndex=StimEndIndex+PostBuffer+WindowLength;
PreStimStartIndex=StimStartIndex-1-WindowLength;
PreStimEndIndex=StimStartIndex-1; % Pre Stim Window ends 1 sample before stimultion


%% Delete Windows with other Stimulations in them
WindowsWithStim=find(StimGap<(WindowLength*1e6/250));
WindowsWithStim=[WindowsWithStim,WindowsWithStim+1];

PostStimStartIndex(WindowsWithStim)=[];
PostStimEndIndex(WindowsWithStim)=[];
PreStimStartIndex(WindowsWithStim)=[];
PreStimEndIndex(WindowsWithStim)=[];

StimStartIndex(WindowsWithStim)=[];
StimEndIndex(WindowsWithStim)=[];
StimStartTimes(WindowsWithStim)=[];
StimEndTimes(WindowsWithStim)=[];
StimLengths(WindowsWithStim)=[];
NumStims(WindowsWithStim)=[];
% StimGap(WindowsWithStim(1:end-1))=[];

%% Delete Stimulation Windows in which there is missing post stimulation

MissingPost=find((AllTime(PostStimEndIndex)-StimEndTimes)>(PostBuffer/Fs*10^6+WindowLength/Fs*10^6));

PostStimStartIndex(MissingPost)=[];
PostStimEndIndex(MissingPost)=[];
PreStimStartIndex(MissingPost)=[];
PreStimEndIndex(MissingPost)=[];

StimStartIndex(MissingPost)=[];
StimEndIndex(MissingPost)=[];
StimStartTimes(MissingPost)=[];
StimEndTimes(MissingPost)=[];
StimLengths(MissingPost)=[];
NumStims(MissingPost)=[];
% StimGap(MissingPost)=[];

%% Delete Stimulation Windows in which there is missing pre stimulation
MissingPre=find((StimStartTimes-AllTime(PreStimStartIndex))>(1/Fs*10^6+WindowLength/Fs*10^6));

PostStimStartIndex(MissingPre)=[];
PostStimEndIndex(MissingPre)=[];
PreStimStartIndex(MissingPre)=[];
PreStimEndIndex(MissingPre)=[];

StimStartIndex(MissingPre)=[];
StimEndIndex(MissingPre)=[];
StimStartTimes(MissingPre)=[];
StimEndTimes(MissingPre)=[];
StimLengths(MissingPre)=[];
NumStims(MissingPre)=[];
% StimGap(MissingPre)=[];

%% Create Pre/Post Window Cell Array

%Create Cell Arrays for Features
NumFeats=3;
NumChannels=4;
preStimFeats=cell(NumChannels,length(PostStimStartIndex),NumFeats);
postStimFeats=cell(NumChannels,length(PostStimStartIndex),NumFeats);

%Define Feature Calculation Functions
LL = @(x) sum(abs(diff(x)));
A = @(x) sum(abs(x));
Energy= @(x) sum(x.^2);
ZX = @(x) sum(((x(2:end) > mean(x)) & (diff(x) > (x(2:end) - mean(x)))) | ...
    ((x(2:end) < mean(x)) & (diff(x) < (x(2:end) - mean(x)))));

%Calculate Features for preStim and postStim
for Channel =1:NumChannels;
for StimNumber=1:length(PostStimStartIndex);
    %Find PostStimulation Features
    postStimFeats{Channel,StimNumber,1}=LL(AllData(Channel,PostStimStartIndex(StimNumber):PostStimEndIndex(StimNumber)));
    postStimFeats{Channel,StimNumber,2}=A(AllData(Channel,PostStimStartIndex(StimNumber):PostStimEndIndex(StimNumber)));
    postStimFeats{Channel,StimNumber,3}=Energy(AllData(Channel,PostStimStartIndex(StimNumber):PostStimEndIndex(StimNumber)));
    postStimFeats{Channel,StimNumber,4}=ZX(AllData(Channel,PostStimStartIndex(StimNumber):PostStimEndIndex(StimNumber)));
    postStimFeats{Channel,StimNumber,5}=singleSidedFFT(AllData(Channel,PostStimStartIndex(StimNumber):PostStimEndIndex(StimNumber)),WindowLength);

    %Find PreStimulation Features
    preStimFeats{Channel,StimNumber,1}=LL(AllData(Channel,PreStimStartIndex(StimNumber):PreStimEndIndex(StimNumber)));
    preStimFeats{Channel,StimNumber,2}=A(AllData(Channel,PreStimStartIndex(StimNumber):PreStimEndIndex(StimNumber)));
    preStimFeats{Channel,StimNumber,3}=Energy(AllData(Channel,PreStimStartIndex(StimNumber):PreStimEndIndex(StimNumber)));
    preStimFeats{Channel,StimNumber,4}=ZX(AllData(Channel,PreStimStartIndex(StimNumber):PreStimEndIndex(StimNumber)));
    preStimFeats{Channel,StimNumber,5}=singleSidedFFT(AllData(Channel,PreStimStartIndex(StimNumber):PreStimEndIndex(StimNumber)),WindowLength);
    
end
end

%Calculate Ratios of Post to Pre
postPreRatios=cell2mat(postStimFeats(:,:,1:4))./cell2mat(preStimFeats(:,:,1:4));

%% Make the Feature Table for Classification Learner App
FeatMatrix=[postStimFeats(:,:,1)',postStimFeats(:,:,2)',postStimFeats(:,:,3)',postStimFeats(:,:,4)'];
FeatMatrix=FeatMatrix(1:length(StimLabels),:);
FeatMatrix=[FeatMatrix,num2cell(StimLabels)];
FeatTable=cell2table(FeatMatrix,'VariableNames',{'C1LL' 'C2LL' 'C3LL' 'C4LL'...
    'C1A' 'C2A' 'C3A' 'C4A' 'C1E' 'C2E' 'C3E' 'C4E'...
    'C1ZX' 'C2ZX' 'C3ZX' 'C4ZX' 'LEReduction'});
%% Histogram of Line Length Ratios

figure('Name','Histograms of Line Length Ratios')

subplot(2,2,1)
hold on
histogram(postPreRatios(1,:,1),50);
histogram(postPreRatios(1,NumStims==1,1),50)
histogram(postPreRatios(1,NumStims==5,1),50)
title('Channel 1 LL Ratio (Post-Stim/Pre-Stim)');
xlabel('Binned Ratio');
ylabel('Count');
legend('All Stim','1 Stim','5 Stim')
hold off

subplot(2,2,2)
hold on
histogram(postPreRatios(2,:,1),50);
histogram(postPreRatios(2,NumStims==1,1),50)
histogram(postPreRatios(2,NumStims==5,1),50)
title('Channel 2 LL Ratio (Post-Stim/Pre-Stim)');
xlabel('Binned Ratio');
ylabel('Count');
hold off

subplot(2,2,3)
hold on
histogram(postPreRatios(3,:,1),50);
histogram(postPreRatios(3,NumStims==1,1),50)
histogram(postPreRatios(3,NumStims==5,1),50)
title('Channel 3 LL Ratio (Post-Stim/Pre-Stim)');
xlabel('Binned Ratio');
ylabel('Count');
hold off

subplot(2,2,4)
hold on
histogram(postPreRatios(4,:,1),50);
histogram(postPreRatios(4,NumStims==1,1),50)
histogram(postPreRatios(4,NumStims==5,1),50)
title('Channel 4 LL Ratio (Post-Stim/Pre-Stim)');
xlabel('Binned Ratio');
ylabel('Count');
hold off

%% Histogram of Area Ratios

figure('Name','Histograms of Area Ratios')

subplot(2,2,1)
hold on
histogram(postPreRatios(1,:,2),50);
histogram(postPreRatios(1,NumStims==1,2),50)
histogram(postPreRatios(1,NumStims==5,2),50)
title('Channel 1 Area Ratio (Post-Stim/Pre-Stim)');
xlabel('Binned Ratio');
ylabel('Count');
legend('All Stim','1 Stim','5 Stim')
hold off

subplot(2,2,2)
hold on
histogram(postPreRatios(2,:,2),50);
histogram(postPreRatios(2,NumStims==1,2),50)
histogram(postPreRatios(2,NumStims==5,2),50)
title('Channel 2 Area Ratio (Post-Stim/Pre-Stim)');
xlabel('Binned Ratio');
ylabel('Count');
hold off


subplot(2,2,3)
hold on
histogram(postPreRatios(3,:,2),50);
histogram(postPreRatios(3,NumStims==1,2),50)
histogram(postPreRatios(3,NumStims==5,2),50)
title('Channel 3 Area Ratio (Post-Stim/Pre-Stim)');
xlabel('Binned Ratio');
ylabel('Count');
hold off


subplot(2,2,4)
hold on
histogram(postPreRatios(4,:,2),50);
histogram(postPreRatios(4,NumStims==1,2),50)
histogram(postPreRatios(4,NumStims==5,2),50)
title('Channel 4 Area Ratio (Post-Stim/Pre-Stim)');
xlabel('Binned Ratio');
ylabel('Count');
hold off

%% Plot Line Length Post/Pre Ratio over time
figure('Name','Line Length Post/Pre Ratio over Time')
title('Patient 1 Line Length Post/Pre Ratio All Stim over Time')

%Set Up the y limits
ylim([0.5,4])
y=ylim;

%Set up the Reprogramming Date Lines
ReprogrammingDates=datetime(ClinicalReprogramming/1e6,'ConvertFrom','posixtime');
tx=[ReprogrammingDates;ReprogrammingDates];
ty=repmat(ylim',1,size(ReprogrammingDates,2));


subplot(4,1,1)
hold on
ylim(y)
%Plot Reprogramming Dates
plot(tx,ty,'Color',[0.8,0.8,0.8])
%Plot Feature
plot(datetime(StimStartTimes/1e6,'ConvertFrom','posixtime'),postPreRatios(1,:,1),'.','DisplayName','RNS Data')
xlim=[datetime(StimStartTimes(1)/1e6,'ConvertFrom','posixtime'),datetime(StimStartTimes(end)/1e6,'ConvertFrom','posixtime')];
%Plot Reference Line
plot(xlim,ones(size(xlim)),'LineWidth',3,'Color',[255/255,51/255,51/255])
title('Channel 1');
xlabel('Date');
ylabel('Post LL/Pre LL');
legend('Clinical Reprogramming Dates')
hold off

subplot(4,1,2)
hold on
ylim(y)
plot(tx,ty,'Color',[0.8,0.8,0.8])
plot(datetime(StimStartTimes/1e6,'ConvertFrom','posixtime'),postPreRatios(2,:,1),'.')
xlim=[datetime(StimStartTimes(1)/1e6,'ConvertFrom','posixtime'),datetime(StimStartTimes(end)/1e6,'ConvertFrom','posixtime')];
plot(xlim,ones(size(xlim)),'LineWidth',3,'Color',[255/255,51/255,51/255])
title('Channel 2');
xlabel('Date');
ylabel('Post LL/Pre LL');
hold off

subplot(4,1,3)
hold on
ylim(y)
plot(tx,ty,'Color',[0.8,0.8,0.8])
plot(datetime(StimStartTimes/1e6,'ConvertFrom','posixtime'),postPreRatios(3,:,1),'.')
xlim=[datetime(StimStartTimes(1)/1e6,'ConvertFrom','posixtime'),datetime(StimStartTimes(end)/1e6,'ConvertFrom','posixtime')];
plot(xlim,ones(size(xlim)),'LineWidth',3,'Color',[255/255,51/255,51/255])
title('Channel 3');
xlabel('Date');
ylabel('Post LL/Pre LL');
hold off

subplot(4,1,4)
hold on
ylim(y)
plot(tx,ty,'Color',[0.8,0.8,0.8])
plot(datetime(StimStartTimes/1e6,'ConvertFrom','posixtime'),postPreRatios(4,:,1),'.')
xlim=[datetime(StimStartTimes(1)/1e6,'ConvertFrom','posixtime'),datetime(StimStartTimes(end)/1e6,'ConvertFrom','posixtime')];
plot(xlim,ones(size(xlim)),'LineWidth',3,'Color',[255/255,51/255,51/255])
title('Channel 4');
xlabel('Date');
ylabel('Post LL/Pre LL');
hold off

annotation('textbox', [0 0.9 1 0.1], ...
    'String', 'Line Length Post/Pre Ratio over Time', ...
    'EdgeColor', 'none', ...
    'HorizontalAlignment', 'center','FontSize',14, ...
    'FontWeight','bold')

%% Plot Line Length Post Stim over time
figure('Name','Line Length Post Stim over Time')
title('Line Length Post Stim over Time')

%Set Up the y limits
ylim([5000,35000])
y=ylim;

%Set up the Reprogramming Date Lines
ReprogrammingDates=datetime(ClinicalReprogramming/1e6,'ConvertFrom','posixtime');
tx=[ReprogrammingDates;ReprogrammingDates];
ty=repmat(ylim',1,size(ReprogrammingDates,2));

subplot(4,1,1)
hold on
ylim(y)
plot(tx,ty,'Color',[0.8,0.8,0.8])
plot(datetime(StimStartTimes/1e6,'ConvertFrom','posixtime'), cell2mat(postStimFeats(1,:,1)),'.','DisplayName','RNS Data')
title('Channel 1');
xlabel('Date');
ylabel('Post LL');
legend('Clinical Reprogramming Dates')
hold off

subplot(4,1,2)
hold on
ylim(y)
plot(tx,ty,'Color',[0.8,0.8,0.8])
plot(datetime(StimStartTimes/1e6,'ConvertFrom','posixtime'), cell2mat(postStimFeats(2,:,1)),'.')
title('Channel 2');
xlabel('Date');
ylabel('Post LL');
hold off

subplot(4,1,3)
hold on
ylim(y)
plot(tx,ty,'Color',[0.8,0.8,0.8])
plot(datetime(StimStartTimes/1e6,'ConvertFrom','posixtime'), cell2mat(postStimFeats(3,:,1)),'.')
title('Channel 3');
xlabel('Date');
ylabel('Post LL');
hold off

subplot(4,1,4)
hold on
ylim(y)
plot(tx,ty,'Color',[0.8,0.8,0.8])
plot(datetime(StimStartTimes/1e6,'ConvertFrom','posixtime'), cell2mat(postStimFeats(4,:,1)),'.')
title('Channel 4');
xlabel('Date');
ylabel('Post LL');
hold off

annotation('textbox', [0 0.9 1 0.1], ...
    'String', 'Line Length Post Stim over Time', ...
    'EdgeColor', 'none', ...
    'HorizontalAlignment', 'center','FontSize',14, ...
    'FontWeight','bold')

%% Plot Line Length Pre Stim over time
figure('Name','Line Length Pre Stim over Time')
title('Line Length Pre Stim over Time')

%Set Up the y limits
ylim([5000,35000])
y=ylim;

%Set up the Reprogramming Date Lines
ReprogrammingDates=datetime(ClinicalReprogramming/1e6,'ConvertFrom','posixtime');
tx=[ReprogrammingDates;ReprogrammingDates];
ty=repmat(ylim',1,size(ReprogrammingDates,2));

subplot(4,1,1)
hold on
ylim(y)
d=plot(tx,ty,'Color',[0.8,0.8,0.8]);
s=plot(datetime(StimStartTimes/1e6,'ConvertFrom','posixtime'), cell2mat(preStimFeats(1,:,1)),'.','DisplayName','RNS Data');
title('Channel 1');
xlabel('Date');
ylabel('Post LL');
legend([d(1) s],{'Clinical Reprogramming Dates','PreStimFeat'})
hold off

subplot(4,1,2)
hold on
ylim(y)
plot(tx,ty,'Color',[0.8,0.8,0.8])
plot(datetime(StimStartTimes/1e6,'ConvertFrom','posixtime'), cell2mat(preStimFeats(2,:,1)),'.')
title('Channel 2');
xlabel('Date');
ylabel('Post LL');
hold off

subplot(4,1,3)
hold on
ylim(y)
plot(tx,ty,'Color',[0.8,0.8,0.8])
plot(datetime(StimStartTimes/1e6,'ConvertFrom','posixtime'), cell2mat(preStimFeats(3,:,1)),'.')
title('Channel 3');
xlabel('Date');
ylabel('Post LL');
hold off

subplot(4,1,4)
hold on
ylim(y)
plot(tx,ty,'Color',[0.8,0.8,0.8])
plot(datetime(StimStartTimes/1e6,'ConvertFrom','posixtime'), cell2mat(preStimFeats(4,:,1)),'.')
title('Channel 4');
xlabel('Date');
ylabel('Post LL');
hold off

annotation('textbox', [0 0.9 1 0.1], ...
    'String', 'Line Length Pre Stim over Time', ...
    'EdgeColor', 'none', ...
    'HorizontalAlignment', 'center','FontSize',14, ...
    'FontWeight','bold')

%% Plot Area Post/Pre Ratio over time
figure('Name','Area Post/Pre Ratio over Time')

subplot(4,1,1)
hold on
ReprogrammingDates=datetime(ClinicalReprogramming/1e6,'ConvertFrom','posixtime');
y=[0.5,1.5];
for n=1:length(ReprogrammingDates)
plot([ReprogrammingDates(n),ReprogrammingDates(n)],y,'k');
end
ylim([0.5,1.5])
plot(datetime(StimStartTimes/1e6,'ConvertFrom','posixtime'),postPreRatios(1,:,2),'.','DisplayName','RNS Data')
title('Channel 1');
xlabel('Date');
ylabel('Post A/Pre A');
legend('Clinical Reprogramming Dates')
hold off

subplot(4,1,2)
hold on
ReprogrammingDates=datetime(ClinicalReprogramming/1e6,'ConvertFrom','posixtime');
y=[0.5,1.5];
for n=1:length(ReprogrammingDates)
plot([ReprogrammingDates(n),ReprogrammingDates(n)],y,'k');
end
ylim([0.5,1.5])
plot(datetime(StimStartTimes/1e6,'ConvertFrom','posixtime'),postPreRatios(2,:,2),'.')
title('Channel 2');
xlabel('Date');
ylabel('Post A/Pre A');
hold off

subplot(4,1,3)
hold on
ReprogrammingDates=datetime(ClinicalReprogramming/1e6,'ConvertFrom','posixtime');
y=[0.5,1.5];
for n=1:length(ReprogrammingDates)
plot([ReprogrammingDates(n),ReprogrammingDates(n)],y,'k');
end
ylim([0.5,1.5])
plot(datetime(StimStartTimes/1e6,'ConvertFrom','posixtime'),postPreRatios(3,:,2),'.')
title('Channel 3');
xlabel('Date');
ylabel('Post A/Pre A');
hold off

subplot(4,1,4)
hold on
ReprogrammingDates=datetime(ClinicalReprogramming/1e6,'ConvertFrom','posixtime');
y=[0.5,1.5];
for n=1:length(ReprogrammingDates)
plot([ReprogrammingDates(n),ReprogrammingDates(n)],y,'k');
end
ylim([0.5,1.5])
plot(datetime(StimStartTimes/1e6,'ConvertFrom','posixtime'),postPreRatios(4,:,2),'.')
title('Channel 4');
xlabel('Date');
ylabel('Post A/Pre A');
hold off

annotation('textbox', [0 0.9 1 0.1], ...
    'String', 'RNS Signal Area Post/Pre Ratio over Time', ...
    'EdgeColor', 'none', ...
    'HorizontalAlignment', 'center','FontSize',14, ...
    'FontWeight','bold')

%% Calculate FFT Correlation across Channels

%Calculate Cross Channel FFT Correlation Post Stim
postStimFFTCorrs=[];
for StimNumber=1:length(PostStimStartIndex)
    [cr,lgs]=xcorr(cell2mat(postStimFeats(:,StimNumber,3))','coeff');
    [Y,I] = max(cr,[],1);
    %       Autocorrelations=NumChannels^0+(NumChannels+1)*(0:(NumChannels-1));
    %Find the mean of the correlations between different channels
    MeanCorr=(sum(Y)- NumChannels)/(length(Y)-NumChannels);
    postStimFFTCorrs=[postStimFFTCorrs,MeanCorr];
end

%Calculate Cross Channel FFT Correlation Pre Stim
preStimFFTCorrs=[];
for StimNumber=1:length(PostStimStartIndex)
    [cr,lgs]=xcorr(cell2mat(postStimFeats(:,StimNumber,3))','coeff');
    [Y,I] = max(cr,[],1);
    %       Autocorrelations=NumChannels^0+(NumChannels+1)*(0:(NumChannels-1));
    %Find the mean of the correlations between different channels
    MeanCorr=(sum(Y)- NumChannels)/(length(Y)-NumChannels);
    preStimFFTCorrs=[preStimFFTCorrs,MeanCorr];
end

postPreFFTCorrRatio=postStimFFTCorrs./preStimFFTCorrs;
%% Calculate TimeSeries Correlation across Channels

%Calculate Cross Channel TimeSeries Correlation Post Stim
postStimCorrs=[];
for StimNumber=1:length(PostStimStartIndex)
    [cr,lgs]=xcorr(AllData(:,PostStimStartIndex(StimNumber):PostStimEndIndex(StimNumber))','coeff');
    [Y,I] = max(cr,[],1);
    %       Autocorrelations=NumChannels^0+(NumChannels+1)*(0:(NumChannels-1));
    %Find the mean of the correlations between different channels
    MeanCorr=(sum(Y)- NumChannels)/(length(Y)-NumChannels);
    postStimCorrs=[postStimCorrs,MeanCorr];
end

%Calculate Cross Channel TimeSeries Correlation Pre Stim
preStimCorrs=[];
for StimNumber=1:length(PostStimStartIndex)
    [cr,lgs]=xcorr(AllData(:,PreStimStartIndex(StimNumber):PreStimEndIndex(StimNumber))','coeff');
    [Y,I] = max(cr,[],1);
    %       Autocorrelations=NumChannels^0+(NumChannels+1)*(0:(NumChannels-1));
    %Find the mean of the correlations between different channels
    MeanCorr=(sum(Y)- NumChannels)/(length(Y)-NumChannels);
    preStimCorrs=[preStimCorrs,MeanCorr];
end

postPreCorrRatio=postStimCorrs./preStimCorrs;
postPreCorrDiff=postStimCorrs-preStimCorrs;

%% Plot the Correlation Ratio and Difference over Time
figure('Name','Channel Signal Correlation Post/Pre Ratio over Time')

subplot(2,1,1)
hold on
ReprogrammingDates=datetime(ClinicalReprogramming/1e6,'ConvertFrom','posixtime');
y=[0.5,1.5];
for n=1:length(ReprogrammingDates)
plot([ReprogrammingDates(n),ReprogrammingDates(n)],y,'k');
end
ylim([0.8,1.25])
plot(datetime(StimStartTimes/1e6,'ConvertFrom','posixtime'),postPreCorrRatio,'.','DisplayName','RNS Data')
title('Post/Pre Ratio over Time');
xlabel('Date');
ylabel('Post Corr/Pre Corr');
legend('Clinical Reprogramming Dates')
hold off

subplot(2,1,2)
hold on
ReprogrammingDates=datetime(ClinicalReprogramming/1e6,'ConvertFrom','posixtime');
y=[-0.3,0.3];
for n=1:length(ReprogrammingDates)
plot([ReprogrammingDates(n),ReprogrammingDates(n)],y,'k');
end
ylim([-0.2,0.2])
plot(datetime(StimStartTimes/1e6,'ConvertFrom','posixtime'),postPreCorrDiff,'.')
title('Post-Pre Difference over Time');
xlabel('Time (HH:MM:SS)');
ylabel('Date');
hold off

annotation('textbox', [0 0.9 1 0.1], ...
    'String', 'Cross Channel Signal Correlation', ...
    'EdgeColor', 'none', ...
    'HorizontalAlignment', 'center','FontSize',14, ...
    'FontWeight','bold')

%% Plot the correlations of 4 channels one stim
for row = 1:4
    for col = 1:4
        nm = 4*(row-1)+col;
        subplot(4,4,nm)
        stem(lgs,cr(:,nm),'.')
        title(sprintf('c_{%d%d}',row,col))
        ylim([0 1])
    end
end

%% Plot the FFT
figure
Fs=250; %Sampling Frequency
f=Fs*(0:(WindowLength/2))/WindowLength;
plot(f,cell2mat(postStimFeats(Channel,StimNumber,3)))
title('Single-Sided Amplitude Spectrum of X(t)')
xlabel('f (Hz)')
ylabel('|P1(f)|')

