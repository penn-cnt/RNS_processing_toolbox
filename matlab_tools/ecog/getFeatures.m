function [ftmat, flabels] = getFeatures(windows, AllData, fs, ftlist, options)
% [ftmat, ftlabels] = getFeatures(windows, AllData, fs, options)
% Calculates features over data windows
% INPUTS:
%   windows (N x 2) matrix of start/stop window indices into AllData
%   AllData (M x 4) RNS data matrix
%   fs - sampling frequency (usually 250 for RNS)
%   ftlist - features to compute ('ll', 'plv', 'ss', 'bp')
%   options: 
%       'bpFilter' (2 x 1) [hp cutoff, lp cutoff]
%       'resampleFs' frequency to resample to. Note, any filtering occurs before resampling       
%
% OUTPUTS:
%   ftmat (N x nfts) matrix of features for each window
%   flabels (nfts x 1) cell array of feature names
%
% Calculates features over data windows 

arguments
    windows (:,2)
    AllData (:,4)
    fs (1,1)
    ftlist = {'ll', 'bp'}
    options.bands
end
    
    
    % %%% FEATURE SETUP %%% %
    ft_sel = ismember({'ll', 'bp', 'plv'}, ftlist); 

    % define bands
    n_bands = 3; 
    bandnames = {'alpha', 'beta', 'gamma'}; 
    alpha = [8,12];
    beta = [13, 30];
    gamma = [30, 90];

    % pre-calculate bandpass filters
   if ft_sel(3) 
        [B_alpha, A_alpha] = butter(4, [2*alpha/fs]);
        [B_beta, A_beta] = butter(4, [2*beta/fs]);
        [B_gamma, A_gamma] = butter(4, [2*gamma/fs]);

        col_pairs = repmat(nchoosek(1:4,2), n_bands, 1)+repelem((0:4:8)',6);
        has_connection = cell2mat(arrayfun(@(x)find(any(col_pairs == x,2)), (1:12), 'Uni', 0)); 
    end
    
    % Define functions 
    llfun = @(n)sum(abs(diff(n)))./length(n);
    
    % allocate feature matrix
    ft_sz = [1, n_bands, n_bands];
    ftmat = nan(length(windows), sum(ft_sz)*4);

    % Create feature labels 
    all_fts  = {{'ll'}, strcat('bp_', bandnames), strcat('plv_', bandnames)}; 
    ft_labels = all_fts(ft_sel); 
    flabels_chan = cellfun(@(x)strcat(x, {'_ch1', '_ch2', '_ch3', '_ch4'}), [ft_labels{:}], 'Uni', 0);
    flabels = [flabels_chan{:}]; 
    

    % %%% DATA SETUP %%% % 
    % Pull out all data clips into cell array to avoid using a
    % "broadcast variable" in the parfor loop
    dataClips = arrayfun(@(x) double(AllData(windows(x,1):windows(x,2),:)),...
        (1:length(windows)), 'Uni', 0);
    

    % %%%  FEATURE CALCULATIONS %%% % 
    tic
    parfor i_evt = 1:length(windows)

        clip = dataClips{i_evt};

        fts = nan(sum(ft_sel.*ft_sz), 4); 
        i_ft = 1; 
        
        if ft_sel(1)                % LINE LENGTH
            fts(i_ft,:) = llfun(clip); 
            i_ft = i_ft +1; 
        end

        if ft_sel(2)                % BAND POWER
                
            % Calculate psd, then bandpower from that
            % alpha, beta, gamma
            [pxx, freq] = pwelch(clip, [], [], [], fs);
  
            nnan = ~any(isnan(pxx));
            [a_bp, b_bp, g_bp] = deal(nan(1,4));
    
            a_bp(nnan) = bandpower(pxx(:,nnan), freq, alpha, 'psd');
            b_bp(nnan) = bandpower(pxx(:,nnan), freq, beta, 'psd');
            g_bp(nnan) = bandpower(pxx(:,nnan), freq, gamma, 'psd');
            fts(i_ft+(0:2),:) = [a_bp; b_bp; g_bp];
            i_ft = i_ft + 3; 

        end
        
        if ft_sel(3)                    % PLV

            alpha_clip = filtfilt(B_alpha, A_alpha, clip);
            beta_clip = filtfilt(B_beta, A_beta, clip);
            gamma_clip = filtfilt(B_gamma, A_gamma, clip);
            b_clips = [alpha_clip, beta_clip, gamma_clip]; 

            % Hilbert transform, and removal of first and last 10%
            hil = unwrap(angle(hilbert(b_clips)));
            p_10 = floor(length(clip)/10); 
            hil = hil(p_10:end-p_10,:);

            phase_diff = hil(:,col_pairs(:,1)) - hil(:,col_pairs(:,2));
            PLV = abs(sum(exp(1i*phase_diff)))/size(phase_diff,1); 

            % average across all connections for each channel, reshape
            % across bands
            fts(i_ft+[0:2],:) = reshape(mean(PLV(has_connection)), [], n_bands)'; 

        end
            
        % aggregate features (reshape fts from n_fts x 4 channels to vector)
        ftmat(i_evt,:) = reshape(fts', 1,[]);
    end
    toc
   
    

end