function PDMS_data= parsePDMS_file(pdms)
% Parses CSV file and saves "PDMS_data.mat" in the same location

T = pdms; 

T.Programming_Date = T.Programming_Date + calyears(2000);

T.Tx1_B1 = parseLeads(T.Tx1_B1);
T.Tx1_B2 = parseLeads(T.Tx1_B2);
T.Tx2_B1 = parseLeads(T.Tx2_B1);
T.Tx2_B2 = parseLeads(T.Tx2_B2);
T.Tx3_B1 = parseLeads(T.Tx3_B1);
T.Tx3_B2 = parseLeads(T.Tx3_B2);
T.Tx4_B1 = parseLeads(T.Tx4_B1);
T.Tx4_B2 = parseLeads(T.Tx4_B2);
T.Tx5_B1 = parseLeads(T.Tx5_B1);
T.Tx5_B2 = parseLeads(T.Tx5_B2);

T.ActiveTrodes= ((T.Tx1_B1~=0)+(T.Tx1_B2 ~=0)+ ...
    (T.Tx2_B1~=0)+(T.Tx2_B2 ~=0)+ ...
    (T.Tx3_B1~=0)+(T.Tx3_B2 ~=0)+ ...
    (T.Tx4_B1~=0)+(T.Tx4_B2 ~=0)+ ...
    (T.Tx5_B1~=0)+(T.Tx5_B2 ~=0)) ~= 0;

T.Current_Tx1_B1 = extractNumArray(T.Current_Tx1_B1);
T.Current_Tx1_B2 = extractNumArray(T.Current_Tx1_B2);
T.Current_Tx2_B1 = extractNumArray(T.Current_Tx2_B1);
T.Current_Tx2_B2 = extractNumArray(T.Current_Tx2_B2);
T.Current_Tx3_B1 = extractNumArray(T.Current_Tx3_B1);
T.Current_Tx3_B2 = extractNumArray(T.Current_Tx3_B2);
T.Current_Tx4_B1 = extractNumArray(T.Current_Tx4_B1);
T.Current_Tx4_B2 = extractNumArray(T.Current_Tx4_B2);
T.Current_Tx5_B1 = extractNumArray(T.Current_Tx5_B1);
T.Current_Tx5_B2 = extractNumArray(T.Current_Tx5_B2);

T.Freq_Tx1_B1 = extractNumArray(T.Freq_Tx1_B1);
T.Freq_Tx1_B2 = extractNumArray(T.Freq_Tx1_B2);
T.Freq_Tx2_B1 = extractNumArray(T.Freq_Tx2_B1);
T.Freq_Tx2_B2 = extractNumArray(T.Freq_Tx2_B2);
T.Freq_Tx3_B1 = extractNumArray(T.Freq_Tx3_B1);
T.Freq_Tx3_B2 = extractNumArray(T.Freq_Tx3_B2);
T.Freq_Tx4_B1 = extractNumArray(T.Freq_Tx4_B1);
T.Freq_Tx4_B2 = extractNumArray(T.Freq_Tx4_B2);
T.Freq_Tx5_B1 = extractNumArray(T.Freq_Tx5_B1);
T.Freq_Tx5_B2 = extractNumArray(T.Freq_Tx5_B2);

T.PW_Tx1_B1 = extractNumArray(T.PW_Tx1_B1);
T.PW_Tx1_B2 = extractNumArray(T.PW_Tx1_B2);
T.PW_Tx2_B1 = extractNumArray(T.PW_Tx2_B1);
T.PW_Tx2_B2 = extractNumArray(T.PW_Tx2_B2);
T.PW_Tx3_B1 = extractNumArray(T.PW_Tx3_B1);
T.PW_Tx3_B2 = extractNumArray(T.PW_Tx3_B2);
T.PW_Tx4_B1 = extractNumArray(T.PW_Tx4_B1);
T.PW_Tx4_B2 = extractNumArray(T.PW_Tx4_B2);
T.PW_Tx5_B1 = extractNumArray(T.PW_Tx5_B1);
T.PW_Tx5_B2 = extractNumArray(T.PW_Tx5_B2);

T.Duration_Tx1_B1 = extractNumArray(T.Duration_Tx1_B1);
T.Duration_Tx1_B2 = extractNumArray(T.Duration_Tx1_B2);
T.Duration_Tx2_B1 = extractNumArray(T.Duration_Tx2_B1);
T.Duration_Tx2_B2 = extractNumArray(T.Duration_Tx2_B2);
T.Duration_Tx3_B1 = extractNumArray(T.Duration_Tx3_B1);
T.Duration_Tx3_B2 = extractNumArray(T.Duration_Tx3_B2);
T.Duration_Tx4_B1 = extractNumArray(T.Duration_Tx4_B1);
T.Duration_Tx4_B2 = extractNumArray(T.Duration_Tx4_B2);
T.Duration_Tx5_B1 = extractNumArray(T.Duration_Tx5_B1);
T.Duration_Tx5_B2 = extractNumArray(T.Duration_Tx5_B2);

T.CD_Tx1_B1 = extractNumArray(T.CD_Tx1_B1);
T.CD_Tx1_B2 = extractNumArray(T.CD_Tx1_B2);
T.CD_Tx2_B1 = extractNumArray(T.CD_Tx2_B1);
T.CD_Tx2_B2 = extractNumArray(T.CD_Tx2_B2);
T.CD_Tx3_B1 = extractNumArray(T.CD_Tx3_B1);
T.CD_Tx3_B2 = extractNumArray(T.CD_Tx3_B2);
T.CD_Tx4_B1 = extractNumArray(T.CD_Tx4_B1);
T.CD_Tx4_B2 = extractNumArray(T.CD_Tx4_B2);
T.CD_Tx5_B1 = extractNumArray(T.CD_Tx5_B1);
T.CD_Tx5_B2 = extractNumArray(T.CD_Tx5_B2);

PDMS_data = T;

%%

function parsed= parseLeads(leadstrs)

for i_ld = 1:length(leadstrs)
    if strcmp(leadstrs{i_ld}, 'OFF')
        parsed(i_ld,:) = zeros(1,9);
    else
        a= replace(leadstrs{i_ld}, '-', '-1,');
        b= replace(a, '0', '0,');
        c= replace(b, '+', '1,');
        d= strsplit(c,{'(', ')'});
        p= [str2num(d{2}), str2num(d{3}), str2num(d{4})];
        
        parsed(i_ld,:) = p;
    end
end
end

function parsed = extractNumArray(numCells)
    parsed= zeros(length(numCells), 1);
    i_on= ~strcmp(numCells, 'OFF');
    nums= cellfun(@str2num, regexp([numCells{:}],'\d+\.?\d*','match')');
    parsed(i_on)= nums;

end
end