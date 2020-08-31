function RNShistogram(PatientID,DesiredTrigger)
%Load Patient Trigger Labels
load('PatientTriggerLabels.mat')

%Find Patient Number
N=str2double(PatientID(4:end));

%Find Trigger Labels for Patient
TriggerLabels=PatientTriggerLabels{N,1}.ECoGTrigger;

%Find index of desired trigger label
DesiredTriggerIndex = find(cellfun('length',regexp(TriggerLabels,DesiredTrigger)) == 1);

%Plot 
PatientTriggerLabels{N,1}.Timestamp(DesiredTriggerIndex);

figure
histogram(datetime(PatientTriggerLabels{N,1}.Timestamp(DesiredTriggerIndex)/10^6,'ConvertFrom','posixtime'),'BinWidth',calmonths(1))
title([PatientID,' Histogram'])
ylabel(['Number of ',DesiredTrigger]) 
xlabel('Unix Time')
end



