function [ecogT, ecogD, stims, histT, pdms] = loadRNSptData(ptID, rns_config)
    warning('off','all')    

    ecogT = readtable(ptPth(ptID, rns_config, 'ecog catalog'));
    ecogD = matfile(ptPth(ptID, rns_config, 'device data'));
    stims = load(ptPth(ptID, rns_config, 'device stim'));
    histT = readtable(ptPth(ptID, rns_config, 'hourly histogram'));
    
    try
        pdmsPth = ptPth(ptID, rns_config, 'pdms');
        allpdms = readtable(pdmsPth);  
        pdms = allpdms(contains(allpdms.id_code, ptID),:); 
    catch
        warning('Could not find pdms data at %s',pdmsPth)
        pdms = [];
    end
    
    

        
end