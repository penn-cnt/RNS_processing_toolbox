import os
import h5py
import numpy as np
import pandas as pd
from scipy.io import loadmat
import warnings
import visualizer
import times
import segmentation
import preprocess
import nltk
from os.path import exists
from tqdm import tqdm
import gc

seizure_token_dict = {
    "seizure": "Seizure",
    "sz": "Seizure",
    "captured": "Seizure",
    "onset": "Seizure",
    "c3/c4": "Seizure",
    "c2/4": "Seizure",
    "c4/2": "Seizure",
    "maximal": "Seizure",
    "burst": "Seizure",
    "bl": "Seizure",
    "c1>c2": "Seizure",
    "c4": "Seizure",
    "UEO": "Seizure",
    "lvfa": "Seizure",
    "abnormal": "Seizure",
    "interictal": "Non-Seizure",
}


def read_files(path='data', patientIDs=None, patient_type=['HUP', 'RNS'], annotation_only=False, verbose=False):
    data = {}

    if patientIDs == None or patientIDs == []:
        dir_list = os.listdir(path)
        patientIDs = [s for s in dir_list for type_string in patient_type if type_string in s.upper()]
    if annotation_only == True:
        dir_list = os.listdir(path)
        patientIDs = [s for s in dir_list if exists(path + "/" + s + "/annots.mat")]

    for id in tqdm(patientIDs, disable=not verbose):
        annot_dict = {}
        try:
            with h5py.File(path + "/" + id + "/Device_Data.mat", "r") as f:
                data_key = list(f.keys())[0]
                ind_key = list(f.keys())[1]

                # Get the data
                ecog = list(f[data_key])
                ind = list(f[ind_key])
                f.close()
            catalog = pd.read_csv(path + "/" + id + "/ECoG_Catalog.csv")
        except:
            print("Patient: " + str(id) + " has NO Data")
            continue
        try:
            annot_file = loadmat(path + "/" + id + "/annots.mat")
            annot_list = annot_file['annots']
            description_list = annot_file['descriptions']
            annot_tuple = tuple(map(tuple, annot_list))
            for i in range(len(annot_tuple)):
                annot_dict[annot_tuple[i]] = description_list[i]
        except:
            # print("Patient: " + str(id) + " has NO Annotations")
            pass

        ecog_arr = np.empty((len(ecog), len(ecog[0])))
        ind_arr = np.empty((len(ind), len(ind[0])))
        for i in range(len(ecog)):
            ecog_arr[i] = ecog[i]
        for i in range(len(ind)):
            ind_arr[i] = ind[i]

        data[id] = PatientInfo(ecog_arr.T, ind_arr.astype(int).T, catalog, annot_dict)

        gc.collect()

    return data


def show_patientIDs(patient_type=['HUP', 'RNS'], path='data'):
    dir_list = os.listdir(path)
    return [s for s in dir_list for type_string in patient_type if type_string in s.upper()]


class PatientInfo:
    def __init__(self, data, indices, catalog, annots):
        self.data = data
        self.indices = indices
        self.catalog = self.process_catalog(catalog)
        self.annots = self.process_annotation(annots)
        self.fs = self.set_sample_rate()
        self.type_map = None
        self.concatenated_data = None
        self.color_map = None
        self.concatenation_indices_table = None
        self.annotation_map = None
        self.window_displacement = None
        self.window_length = None
        self.window_start_stop_indices = None
        self.window_indices_stack = None
        self.window_n = None
        self.concatenate_window_n = None
        self.windowed_data = None

    def get_all_clips(self):
        return [self.data[idx[0]:idx[1]] for idx in self.indices]

    def get_clips(self, indices):
        return [self.data[self.indices[idx][0]:self.indices[idx][1]] for idx in indices]

    def set_sample_rate(self):
        return self.catalog.iloc[0]['Sampling rate']

    def get_event_indices(self, event_type=[], combine_clips=True):
        '''
        get the event indices by event type
        :param event_type: list of string
        :param combine_clips:
        :return:
        '''
        clip = []
        clip_dict = {}
        for e in event_type:
            if e == 'le' or e.lower() == 'long_episode':
                row_idx = self.catalog.index[self.catalog['ECoG trigger'] == 'Long_Episode']
                key = 'Long_Episode'
            elif e == 'skd' or e.lower() == 'scheduled':
                row_idx = self.catalog.index[self.catalog['ECoG trigger'] == 'Scheduled']
                key = 'Scheduled'
            elif e == 'sat' or e.lower() == 'saturation':
                row_idx = self.catalog.index[self.catalog['ECoG trigger'] == 'Saturation']
                key = 'Saturation'
            elif e == 'mag' or e.lower() == 'magnet':
                row_idx = self.catalog.index[self.catalog['ECoG trigger'] == 'Magnet']
                key = 'Magnet'
            elif e == 'rt' or e.lower() == 'real_time':
                row_idx = self.catalog.index[self.catalog['ECoG trigger'] == 'Real_Time']
                key = 'Real_Time'
            else:
                row_idx = self.catalog.index[self.catalog['ECoG trigger'] == e]
                key = e
            row_idx = row_idx.to_list()
            if len(row_idx) == 0:
                warnings.warn("No such  event type: " + e)
            if combine_clips == True:
                clip += row_idx
            elif combine_clips == False:
                clip_dict[key] = row_idx

        if combine_clips == True:
            return clip
        elif combine_clips == False:
            return clip_dict

    def plot_events(self, event_indices):
        """
        :param event_indices: list of int - indices of event to plot
        :return:
        """
        for ind in event_indices:
            raw_data = self.data[self.indices[ind][0]:self.indices[ind][1]]
            df = self.catalog.iloc[ind]
            visualizer.plot_clips(raw_data, df, ind, annot=self.annots)

    def process_catalog(self, catalog):
        """
        process imported catalog to
            - add start and end utc timestamp
            - match the event start and end index from matlab style to python
        :param catalog:
        :return:
        """
        times_string = catalog['Raw UTC timestamp']
        time_length = catalog['ECoG length']
        start_offset = catalog['ECoG pre-trigger length']
        catalog['Event Start idx'] -= 1
        catalog['Event End idx'] -= 1
        start_timestamp = [times.timestring_to_timestamp(ts, -ofst) for ts, ofst in zip(times_string, start_offset)]
        end_timestamp = [times.timestring_to_timestamp(ts, tl - ofst) for ts, ofst, tl in
                         zip(times_string, start_offset, time_length)]
        catalog['Start UTC Timestamp'] = start_timestamp
        catalog['End UTC Timestamp'] = end_timestamp
        ###################################################
        # TODO HUP137 has corrupted data point at idx = 3385, end_idx > start_idx
        ###################################################
        if catalog.iloc[0]['Patient ID'] == 'HUP137':
            catalog = catalog.drop(catalog.index[3385])

        return catalog

    def process_annotation(self, annots):
        '''
        process annotation by generating a df object
        :param annots:
        :return:
        '''
        num = len(list(annots.keys()))
        clip_ind_arr = np.empty(num)
        start_ind_arr = np.empty(num)
        end_ind_arr = np.empty(num)
        annot_length_arr = np.empty(num)
        start_time_string = []
        end_time_string = []
        description_list = []
        classification_list = []

        for i, ts in enumerate(list(annots.keys())):
            start_timestamp = ts[0]
            end_timestamp = ts[1]
            clip_ind_arr[i], start_ind_arr[i] = times.timestamp_to_ind(start_timestamp, self.catalog)
            _, end_ind_arr[i] = times.timestamp_to_ind(end_timestamp, self.catalog)
            annot_length_arr[i] = (end_timestamp - start_timestamp) * 1e-6
            start_time_string.append(times.timestamp_to_utctime(start_timestamp))
            end_time_string.append(times.timestamp_to_utctime(end_timestamp))
            description_list.append(annots[ts])
            classification_list.append(description_classifying_helper(annots[ts], seizure_token_dict))
        annot_df = pd.DataFrame()
        annot_df["Start UTC Time"] = start_time_string
        annot_df["End UTC Time"] = end_time_string
        annot_df["Annot Start Index"] = start_ind_arr.astype(int)
        annot_df["Annot End Index"] = end_ind_arr.astype(int)
        annot_df["Annot Length"] = annot_length_arr
        annot_df["Session Index"] = clip_ind_arr.astype(int)
        annot_df["Description"] = description_list
        annot_df["Class"] = classification_list

        return annot_df

    def set_window_parameter(self, window_length=0.5, window_displacement=0.5):
        """
        set parameter to split the windows
        :param window_length: length of window in second
        :param window_displacement: displacement of window in second
        :return:
        """
        self.window_length = window_length
        self.window_displacement = window_displacement
        self.annots = self.annots.drop(self.annots.index[self.annots["Annot Length"] < self.window_length])

    def get_windowed_data(self, start_indices, end_indices):
        """
        returns windowed data
        :param start_indices: array or list of start indices
        :param end_indices: array or list of end indices
        :return: window indices and windowed data
        """
        self.window_start_stop_indices = segmentation.get_windowed_ind(start_indices, end_indices, self.fs,
                                                                       self.window_length, self.window_displacement)
        self.windowed_data = segmentation.get_windowed_data(self.data, self.window_start_stop_indices)
        self.window_indices_stack = np.vstack(self.window_start_stop_indices)
        self.window_n = len(self.windowed_data)
        return self.window_start_stop_indices, self.windowed_data

    def normalize_windowed_data(self, dmin=-512, dmax=511):
        self.windowed_data = preprocess.normalize(self.windowed_data, dmin, dmax)

    def get_windowed_annotation(self, class_n=2):
        '''
        get annotations associated with the windowed clip
        :param class_n: number of classifications
        :return:
        '''
        self.annotation_map = segmentation.get_annot_map(self.window_start_stop_indices,
                                                         self.annots['Annot Start Index'])
        self.color_map, self.type_map = visualizer.get_color_map(self.annotation_map, self.annots, class_n=class_n)
        return self.annotation_map, self.color_map, self.type_map

    def set_concatenation_parameter(self, concatenate_window_n=4):
        self.concatenate_window_n = concatenate_window_n

    def get_concatenated_data(self, features=None, arrange='time_stack'):
        self.concatenation_indices_table = segmentation.get_concatenation_ind(self.window_start_stop_indices,
                                                                              self.concatenate_window_n)
        self.concatenated_data = segmentation.get_concatenation_data(features, self.concatenation_indices_table,
                                                                     arrange=arrange)
        return self.concatenation_indices_table, self.concatenated_data


def description_classifying_helper(description, token_dict):
    '''
    a temporary helper function to classify the existing annotation
    :param description: string - annotations
    :param token_dict: dict - the manually defined dictionary to classify the annotation
    :return: string - class of the annotation description
    '''
    tokens = nltk.tokenize.word_tokenize(description.lower())
    token_dict_keys = list(token_dict.keys())
    elements = []
    for tk in tokens:
        if tk in token_dict_keys:
            elements.append(token_dict[tk])
    if elements != []:
        classification = most_common(elements)
    else:
        classification = "Unclear"
    return classification


def most_common(list):
    '''
    find the most frequent element in list
    :param lst: list
    :return:
    '''
    return max(set(list), key=list.count)
