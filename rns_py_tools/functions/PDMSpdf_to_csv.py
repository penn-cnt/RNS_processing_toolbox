# PDMStoPDF_Converter.py

import PyPDF2 
import numpy as np
import tqdm
import pandas as pd
from dateutil import parser
import re
import os
import sys


ax = ['id_code','Programming_Date','Tx1_B1','Tx1_B2','Tx2_B1','Tx2_B2','Tx3_B1','Tx3_B2','Tx4_B1','Tx4_B2','Tx5_B1',
 'Tx5_B2','Current_Tx1_B1', 'Current_Tx1_B2','Current_Tx2_B1', 'Current_Tx2_B2','Current_Tx3_B1',
 'Current_Tx3_B2','Current_Tx4_B1', 'Current_Tx4_B2', 'Current_Tx5_B1', 'Current_Tx5_B2', 'Freq_Tx1_B1',
 'Freq_Tx1_B2', 'Freq_Tx2_B1','Freq_Tx2_B2','Freq_Tx3_B1','Freq_Tx3_B2','Freq_Tx4_B1','Freq_Tx4_B2','Freq_Tx5_B1',
 'Freq_Tx5_B2','PW_Tx1_B1','PW_Tx1_B2','PW_Tx2_B1','PW_Tx2_B2','PW_Tx3_B1','PW_Tx3_B2',
 'PW_Tx4_B1','PW_Tx4_B2','PW_Tx5_B1','PW_Tx5_B2','Duration_Tx1_B1','Duration_Tx1_B2','Duration_Tx2_B1',
 'Duration_Tx2_B2','Duration_Tx3_B1','Duration_Tx3_B2','Duration_Tx4_B1','Duration_Tx4_B2',
 'Duration_Tx5_B1','Duration_Tx5_B2','CD_Tx1_B1','CD_Tx1_B2','CD_Tx2_B1','CD_Tx2_B2','CD_Tx3_B1',
 'CD_Tx3_B2','CD_Tx4_B1','CD_Tx4_B2','CD_Tx5_B1','CD_Tx5_B2','Detection_A', 'Detection_B','Long_Episode_Length','Magnets_Total',
      'Saturation_Total','Long_Episode_Total','Episodes_per_day','Therapies_per_day']


def get_therapy_details(all_text):  
    ''' reads through all text, which is a PDF file, then grabs all the 
    parameters and puts it in a pandas dataFrame'''
#     print(all_text)
    index_A, index_B, mag_per_month, sat_per_month, LE_per_month, LE_parm, episodes, T = get_A_B_Parms(all_text)
    
    dates,ind = get_dates(all_text)
    all_text = np.array(all_text)
    Tx1 = np.where(all_text == 'Tx1:')
    Tx2 = np.where(all_text == 'Tx2:')
    Tx3 = np.where(all_text == 'Tx3:')
    Tx4 = np.where(all_text == 'Tx4:')
    Tx5 = np.where(all_text == 'Tx5:')

    all_therapies = [Tx1, Tx2, Tx3, Tx4, Tx5]
    Programming_Epochs = pd.DataFrame()
    Ther = ['Tx1', 'Tx2', 'Tx3', 'Tx4', 'Tx5']
    therNum = 0
    for therapy in all_therapies:
        # set parms
        ElecB1 = []
        ElecB2 = []
        CurrentB1 = []
        CurrentB2 = []
        FreqB1 = []
        FreqB2 = []
        PWB1 = []
        PWB2 = []
        DurB1 = []
        DurB2 = []
        CDB1 = []
        CDB2 = []
        Tx1_B1 = []
        Tx1_B2 = []

        if len(therapy[0]) == 0:
            # print('parameters OFF')
            ElecB1.append('OFF')
            ElecB2.append('OFF')
            CurrentB1.append('OFF')
            CurrentB2.append('OFF')
            FreqB1.append('OFF')
            FreqB2.append('OFF')
            PWB1.append('OFF')
            PWB2.append('OFF')
            DurB1.append('OFF')
            DurB2.append('OFF')
            CDB1.append('OFF')
            CDB2.append('OFF')
            Tx1_B1.append('OFF')
            Tx1_B2.append('OFF')
        else:

            for ind in therapy[0]:
                Tx1_B1.append(ind + 1)
                Tx1_B2.append(ind + 2)
            Burst1 = all_text[Tx1_B1]
            Burst2 = all_text[Tx1_B2]

            split_num = len(Burst1) / 6
            Burst1_Split = np.split(Burst1,split_num)
            Burst2_Split = np.split(Burst2,split_num)


            for item in Burst1_Split:
                ElecB1.append(item[0])
                CurrentB1.append(item[1])
                FreqB1.append(item[2])
                PWB1.append(item[3])
                DurB1.append(item[4])
                CDB1.append(item[5])

            for item in Burst2_Split:
                ElecB2.append(item[0])
                CurrentB2.append(item[1])
                FreqB2.append(item[2])
                PWB2.append(item[3])
                DurB2.append(item[4])
                CDB2.append(item[5])
        ther = Ther[therNum]
        therNum += 1
        Programming_Epochs['Programming_Date'] = dates
        Programming_Epochs[ther + '_B1'] = ElecB1
        Programming_Epochs[ther + '_B2'] = ElecB2
        Programming_Epochs['Current_' + ther + '_B1'] = CurrentB1
        Programming_Epochs['Current_' + ther + '_B2'] = CurrentB2
        Programming_Epochs['Freq_' + ther + '_B1'] = FreqB1
        Programming_Epochs['Freq_' + ther + '_B2'] = FreqB2
        Programming_Epochs['PW_' + ther + '_B1'] = PWB1
        Programming_Epochs['PW_' + ther + '_B2'] = PWB2
        Programming_Epochs['Duration_' + ther + '_B1'] = DurB1
        Programming_Epochs['Duration_' + ther + '_B2'] = DurB2
        Programming_Epochs['CD_' + ther + '_B1'] = CDB1
        Programming_Epochs['CD_' + ther + '_B2'] = CDB2
        Programming_Epochs['Detection_A'] = pd.Series(index_A)
        Programming_Epochs['Detection_B'] = pd.Series(index_B)
        Programming_Epochs['Long_Episode_Length'] = LE_parm
        Programming_Epochs['Magnets_Total'] = mag_per_month
        Programming_Epochs['Saturation_Total'] = sat_per_month
        Programming_Epochs['Long_Episode_Total'] = LE_per_month
        Programming_Epochs['Episodes_per_day'] = episodes
        Programming_Epochs['Therapies_per_day'] = T

    return Programming_Epochs


def get_dates(all_text):
    ''' finds all the dates in the Pdf documnet, (all_text)'''
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    dates = []
    index = []
    for a in range(len(all_text)):
        for b in months:
            if b in all_text[a]:
                if len(all_text[a]) == 12:
                    try:  
                        dt_str = all_text[a]+' '+all_text[a+1]
                        parser.parse(dt_str)  # Checks for date format
                        dates.append(dt_str)
                        index.append(a)
                    except ValueError:
                        continue

    return dates, index


def get_A_B_Parms(all_text):
    ''' looks for the A and B parameters in the all_text, to locate the other parameters, magnets__per_month, 
    sat_per_month,LE_per_month, LE_param, episodes, therapies'''
    index_A = []
    index_B = []
    mag_per_month = []
    sat_per_month = []
    LE_per_month = []
    LE_parm = []
    episodes = []
    therapies = []
    for i in range(len(all_text)):
        if '[A]' in all_text[i]:
            if 'OR' in all_text[i]:
                index_A.append(all_text[i] +' ' +all_text[i+1])
            else:
                index_A.append(all_text[i])
        if '[B]' in all_text[i]:        
        # Find next instance of a " / ":
            for j in range(i,len(all_text)): 
                if bool(re.search(' *\/ * ', all_text[j])):
                    idx=j
                    break
            index_B.append(' '.join(all_text[i:idx-1]))  
            mag_per_month.append(all_text[idx+1])
            sat_per_month.append(all_text[idx+4])
            LE_per_month.append(all_text[idx+8])
            LE_parm.append(all_text[idx+9])
            episodes.append(all_text[idx+10])
            therapies.append(all_text[idx+11])

    return index_A, index_B, mag_per_month, sat_per_month, LE_per_month, LE_parm, episodes, therapies


def create_csv(pdfReader):
    '''creates a readable dataFrame from a PDF'''
    num_pages = pdfReader.numPages
    programmingData = pd.DataFrame()
    for n in range(num_pages):
        pageObj = pdfReader.getPage(n)
        text = pageObj.extractText()
        all_text = text.split('\n')
        dates, index = get_dates(all_text)
        for i in range(len(index)):
            if i == len(index) - 1:
                num = index[i]
                prog = get_therapy_details(all_text[num:len(all_text)])
                programmingData = programmingData.append(prog)

            else:
                num = index[i]
                num2 = index[i + 1]
                prog = get_therapy_details(all_text[num:num2])
                programmingData = programmingData.append(prog)
    return programmingData


def find_diff(df, param):
    ''' finds different times in df for a specific param (parameter)'''
    PC = [] #parameterChangeList
        
    for row in range(len(df)):
        if (row == len(df) - 1):
            ##this is the last row
            PC.append(0)
        elif (df[param][row] != df[param][row+1]):
            ## if the column is different 
            if ((param[0:2]!='Tx') & (param !='Detection_A') & (param != 'Detection_B')):
                if (param == 'Long_Episode_Length'):
                    first_num = getNum(df[param][row])
                    sec_num = getNum(df[param][row+1])
                    diff = float(first_num)-float(sec_num)
                    PC.append(diff)
                else:
                    print(df[param][row])
                    diff = float(df[param][row][:-3])-float(df[param][row+1][:-3])
                    PC.append(diff)
            else:
                PC.append(1)
        else:
            # it is not different, so you append 0
            PC.append(0)

    return PC

def getNum(string):
    answer = ''
    for a in string:
        try:
            int(a)
            answer += a
        except:
            print('letter')
    return(answer)


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print('usage: python PDMStoPDF_Converter.py path/to/PDMS/folder /path/to/output/file.csv')

    pathToPDFs = sys.argv[1]
    outputFile = sys.argv[2]  # .csv

    Dirs = os.listdir(pathToPDFs)
    all_epochs = pd.DataFrame()
    for files in tqdm.tqdm(Dirs):
        if files.endswith(".pdf") and not files.startswith('.'):
            id_code = [files[:-4]]
            print(id_code)
            pdfReader = PyPDF2.PdfFileReader(open(pathToPDFs + files, 'rb'))
            data = create_csv(pdfReader)
            data['id_code'] = id_code * len(data)
            all_epochs = all_epochs.append(data)

    all_epochs = all_epochs.reindex((ax), axis=1)
    all_epochs = all_epochs.reset_index()
    all_epochs.to_csv(outputFile)

