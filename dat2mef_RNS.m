%% Description

% This function converts DAT files to MEF files. Each DAT file will
% result in 4 MEF files: one for each channel contained in the DAT file.
% Each channel must be uploaded individually to Blackfynn.

% Jessica Herrmann, Litt Lab 2018
% The MefWriter components of the code were written by John.

% The function will take in the path to a single folder (dataPath) 
% containing multiple DAT files associated with an individual patient. 

% The function will output, within that dataPath folder, a subfolder for 
% each individual DAT file that has been converted to MEF. The subfolder 
% will have the same name as the DAT file. Within each subfolder, there 
% will be four MEF files: one for each of the four channels. The four MEF 
% files will have the same name as the subfolder, plus 1 of 4 unique
% channel identifiers.

% INPUT: Folder --> File_1.dat, File_2.dat 
% OUTPUT: Folder --> File_1 --> File_1.mef, File_2.mef, File_3.mef, File_4.mef
%                --> File_2 --> File_1.mef, File_2.mef, File_3.mef, File_4.mef

% Using the same name for the MEF files is intentional. This permits
% appending of the MEF files to the same 4 channels in Blackfynn. If
% different names were used for the 8 files, 8 separate channels would be
% created in Blackfynn. The first set of files has different timestamp
% information than the second set of files, so they will append
% chronologically in Blackfynn.

%% Function

function [data] = dat2mef_RNS(server, dataPath, csv, numChan, U24id, inst)
%   This is a generic wrapper for the readPersystLay function for reading
%   header information in *.lay files and converting the *.dat files to MEF
%
%   INPUT:
%       server    = vault or fourier
%       dataPath  = path to folder containing .dat and .lay files
%       DATfile   = dat file name for subject to be processed
%       numChan   = number of channels in record (manual read from .lay file)
%       csv       = path to csv file
%       U24id     = Portal ID for subject
%       inst      = Institution/Organization name
%
%   OUTPUT:
%       MEF files are written to separate folder in dataPath 
%
%   USAGE:
%       dat2mef_RNS('LittLab_Mac',...
%       '/Volumes/data/RNS_DataSharing/processed_RNS/AA',...
%       '/Volumes/data/RNS_DataSharing/processed_RNS/AA_Catalog.csv'...
%           4, 'RNS_001', 'UPenn');

%   example dataPath: dataPath = '/Volumes/data/RNS_DataSharing/processed_20180711/AA_copy'
%   example csv:      csv      = '/Volumes/data/RNS_DataSharing/processed_20180711/UPenn_ECoG_Catalog_new.csv'
%                     csv      = '/Volumes/data/RNS_DataSharing/processed_20180815/output.csv'


    % Add MEF_writer to the dynamic Java path (change this path to point to the MEF_writer.jar file)
    javaaddpath('/Volumes/data/RNS_DataSharing/RNS_DataConversion/DAT to MEF/MEF_writer.jar');

    % Read the timestamps from the processed CSV file    
    csv_file = readtable(csv);
    
    % Set the server
    if strcmpi(server,'vault')
        rootPath='\\Fourier.seas.upenn.edu\g\public';
            addpath(fullfile(rootPath,'USERS','anani','PORTAL','Tools'))

    elseif strcmpi(server,'fourier')
        rootPath='/mnt/local/gdrive/public';
            addpath(fullfile(rootPath,'USERS','anani','PORTAL','Tools'))

    elseif strcmpi(server,'LittLab_Mac')
        %rootPath='/Users/littlabadmin/Documents/MATLAB/RNS_Data_Conversion';
        rootPath = '/Volumes/data/RNS_DataSharing/RNS_DataConversion/DAT to MEF';
            addpath(fullfile(rootPath,'Tools'))

    elseif strcmpi(server,'Jessi_Mac')
        rootPath='/Volumes/data/RNS_DataSharing/RNS_DataConversion/DAT to MEF';
            addpath(fullfile(rootPath,'Tools'))        
     
    else
        error('Enter a valid server (fourier or vault only)')
    end
    
    % Sampling rate
    fs=250;
   
    % Gain
    gain=1;
    
    %% Create the appropriate file names and directory
    
    % Make a subfolder to store the MEF files for the entire dataset
    subfolder = 'MEFFiles'; % name of the folder
    mkdir (fullfile(dataPath,subfolder)); % create the directory
    
    % Find the number of .dat files in the dataPath folder
    folder = dir([dataPath '/*.dat']);
    numFiles = size(folder,1);
    
    % Store the start times
    start_times = [];
    tic;  
    % Iterate through the files
    for i = 511:numFiles
        
        % Track progress
        i
        
        % Retrieve the .dat file names
        folder_contents = dir(fullfile(dataPath,'*.dat'));
        datfile_names = {folder_contents.name};
        
        % Access a single .dat file for the given iteration
        DATfile = datfile_names{1,i};
                
        % Create the file folder name
        sub=DATfile(1:end-4);
        
        % Make a folder to contain the MEF files associated with the current .dat file
        % (The folder will be appended to the dataPath used to call dat2mef_RNS)
        mkdir (fullfile(dataPath,subfolder,sub));

        % Change directory into the folder
        cd (fullfile(dataPath,subfolder,sub));

        % Open the .dat file 
        fid=fopen(fullfile(dataPath,DATfile));
        % read the channel data, write data to a "data" matrix
        data=fread(fid,[numChan, inf],'int16');
        % Close file
        fclose(fid);

        % For organizing data in MEF_Writer
        blockSize = round(4000/fs);
        th = 100000;


    %% Write the data to a MEF file

    % Here, time is in units of microseconds because the Blackfynn interface
    % uses UNIX time, converted to microseconds. UNIX time consists of the
    % number of seconds that have elapsed since January 1, 1970, and Blackfynn
    % converts these seconds to microseconds.

    mw_start=tic; % pair 2
    % Write the MEF files for each channel in the DAT file
        for j=1:numChan
           
            % Split the DATfile name at delimiters
            DATfile_split = strsplit(DATfile, {'_', '.'});
            
            % Create the beginning of the new file name
            sub = [DATfile_split{1}];

            % Label the channel (to store it as a separate MEF file)
            chanLabel=[sub, 'C', num2str(j), '.mef'];

            % Call the MefWriter
            mw = edu.mayo.msel.mefwriter.MefWriter(chanLabel, blockSize, fs, th);

            % Set the time interval (timestep) between successive data points
            timestep = 1000000/fs; % microseconds
                      
            % Get row and column of DAT file in CSV file
            [row,col] = find(strcmp(DATfile,csv_file{:,end})); % find row corresponding to DAT file
            
            % Info for Raw UTC Timestamp
            timestamp_rawUTC = string(csv_file{row,'RawUTCTimestamp'}); % Get the timestamp
            timestamp_info_rawUTC = strsplit(timestamp_rawUTC,{'-',' ',':','.'}); 
            yr_rawUTC = str2num(timestamp_info_rawUTC{1,1});
            mo_rawUTC = str2num(timestamp_info_rawUTC{1,2});
            day_rawUTC = str2num(timestamp_info_rawUTC{1,3});
            hr_rawUTC = str2num(timestamp_info_rawUTC{1,4});
            min_rawUTC = str2num(timestamp_info_rawUTC{1,5});
            sec_rawUTC = str2num(timestamp_info_rawUTC{1,6});
            microsec_rawUTC = (str2num(timestamp_info_rawUTC{1,7}))*(10^3); % microsec
            startTime_rawUTC = ((10^6)*(posixtime(datetime(yr_rawUTC,mo_rawUTC,day_rawUTC,hr_rawUTC,min_rawUTC,sec_rawUTC)))) + microsec_rawUTC;
            
            % Info for Raw Local Timestamp
            timestamp_rawLocal = string(csv_file{row,'RawLocalTimestamp'}); % Get the timestamp
            timestamp_info_rawLocal = strsplit(timestamp_rawLocal,{'-',' ',':','.'}); 
            yr_rawLocal = str2num(timestamp_info_rawLocal{1,1});
            mo_rawLocal = str2num(timestamp_info_rawLocal{1,2});
            day_rawLocal = str2num(timestamp_info_rawLocal{1,3});
            hr_rawLocal = str2num(timestamp_info_rawLocal{1,4});
            min_rawLocal = str2num(timestamp_info_rawLocal{1,5});
            sec_rawLocal = str2num(timestamp_info_rawLocal{1,6});
            microsec_rawLocal = (str2num(timestamp_info_rawLocal{1,7}))*(10^3); % microsec
            startTime_rawLocal = ((10^6)*(posixtime(datetime(yr_rawLocal,mo_rawLocal,day_rawLocal,hr_rawLocal,min_rawLocal,sec_rawLocal)))) + microsec_rawLocal;
            
            % Compute the time difference between UTC and Local time
            time_conversion_microsec = startTime_rawUTC - startTime_rawLocal; % time difference in microseconds
            
            % Info for Timestamp
            timestamp = string(csv_file{row,'Timestamp'}); % Get the timestamp
            timestamp_info = strsplit(timestamp,{'-',' ',':','.'}); 
            yr = str2num(timestamp_info{1,1});
            mo = str2num(timestamp_info{1,2});
            day = str2num(timestamp_info{1,3});
            hr = str2num(timestamp_info{1,4}); 
            min = str2num(timestamp_info{1,5});
            sec = str2num(timestamp_info{1,6});
            microsec = (str2num(timestamp_info{1,7}))*(10^3); % microsec
            
            % Convert startTime to UNIX time (in microseconds)
            startTime = (((10^6)*(posixtime(datetime(yr,mo,day,hr,min,sec)))) + microsec) + time_conversion_microsec; % time in microseconds since Jan 1, 1970 (in UTC)
            
            start_times = [start_times, startTime];
            
            % Create time array for x-axis in Blackfynn visualizer
            time = startTime:timestep:((size(data,2)*timestep) + startTime - timestep);
            
            % Commands to write the data to MEF files
            mw.writeData(data(j,:), time, length(data)); % Time should be array of timestamps
            mw.setInstitution(inst);
            mw.setSubjectID(U24id);
            mw.setChannelName(chanLabel);
            mw.setVoltageConversionFactor(gain);
            mw.close;
        end
       disp(toc(mw_start))
       toc
    end
end