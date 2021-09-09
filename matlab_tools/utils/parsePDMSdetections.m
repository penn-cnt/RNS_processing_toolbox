function [detect_A, detect_B] = parsePDMSdetections(pdms)
%%

% regular experession
param_exp = ['Ch.(?<chan>[1-4]) ([A-Za-z0-9]+ - [A-Za-z0-9]+ )?',...
    '(?<type>(BP|LL))\((?<value1>[\d- ]+)(?<units1>[\w%]+), ',...
    '(?<value2>\d+)(?<units2>[%\w]), (?<value3>[\d.]+)(?<units3>\w)\)'];

% parse detection A
detect = regexp(pdms.Detection_A, param_exp, 'names');
detect_A = struct2table(mergeStructs(detect));
detect_A.date = repelem(pdms.Programming_Date, cellfun(@length, detect)); 

% reformat detection A
v1_reg= regexp(detect_A.value1,'\d*','Match');
detect_A.chan = cellfun(@str2num, detect_A.chan);
detect_A.value1 = cellfun(@(x)cellfun(@str2num,x), v1_reg, 'Uni', 0);
detect_A.value2 = cellfun(@str2num, detect_A.value2);
detect_A.value3 = cellfun(@str2num, detect_A.value3);

% parse detection B
detect = regexp(pdms.Detection_B, param_exp, 'names');
detect_B = struct2table(mergeStructs(detect));
detect_B.date = repelem(pdms.Programming_Date, cellfun(@length, detect));

% reformat detection B
v1_reg= regexp(detect_B.value1,'\d*','Match');
detect_B.chan = cellfun(@str2num, detect_B.chan);
detect_B.value1 = cellfun(@(x)cellfun(@str2num,x), v1_reg, 'Uni', 0);
detect_B.value2 = cellfun(@str2num, detect_B.value2);
detect_B.value3 = cellfun(@str2num, detect_B.value3);



function s= mergeStructs(structList)

    strNames = unique(fieldnames(structList{1})');
    for i_st = 1:length(structList)
        strNames= intersect(fieldnames(structList{i_st}), strNames);
    end

    s= struct();
    for f= strNames'
        ctr = 0;     
        for i_st = 1:length(structList)
            len = length(structList{i_st});
            if ismember(f{1}, fieldnames(structList{i_st}))
                for l = 1:len
                    s(ctr+l).(f{1})= structList{i_st}(l).(f{1});
                end
                ctr = ctr + len;
            else
                [s(ctr+[1:len]).(f{1})] = deal([]);
                ctr = ctr+len;
            end 
        end

    end
end

end