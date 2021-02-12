%Define Path to CSV File
EcoGCatalogPath='/Volumes/data/RNS_DataSharing/UPenn_ECog_Catalog.csv';

% Read the CSV file
EcoGCatalog = readtable(EcoGCatalogPath);

%Convert the Datetime String Columns to Matlab Datetime columns
EcoGCatalog.RawLocalTimestamp = datetime(EcoGCatalog.RawLocalTimestamp,'InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
EcoGCatalog.RawUTCTimestamp = datetime(EcoGCatalog.RawUTCTimestamp,'InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
EcoGCatalog.Timestamp = datetime(EcoGCatalog.Timestamp,'InputFormat','yyyy-MM-dd HH:mm:ss.SSS');
EcoGCatalog.Timestamp=posixtime(EcoGCatalog.Timestamp)+posixtime(EcoGCatalog.RawUTCTimestamp)-posixtime(EcoGCatalog.RawLocalTimestamp);
EcoGCatalog.Timestamp=EcoGCatalog.Timestamp*1e6;

%Make New Columns
EcoGCatalog.StartUTCTimestamp=EcoGCatalog.Timestamp;
EcoGCatalog.TriggerUTCTimestamp=posixtime(EcoGCatalog.RawUTCTimestamp)*1e6;
EcoGCatalog.EndUTCTimestamp=EcoGCatalog.StartUTCTimestamp+EcoGCatalog.ECoGLength*1e6;

% Unique Patient Initials
PatientInitials=unique(EcoGCatalog.Initials);

%Pull Patient Specific Ecog Triggers
Triggers=cell(length(PatientInitials),1);
for n=1:length(PatientInitials)
Triggers{n}=EcoGCatalog(strcmp(EcoGCatalog.Initials,PatientInitials{n}),{'ECoGTrigger','StartUTCTimestamp','TriggerUTCTimestamp','EndUTCTimestamp','ECoGLength'});
end

%Reorder the Labels
PatientTriggerAllTimes([1,3,7,10,5,15,14,18,11,9,16,8,2],1)=Triggers(1:end,1);