# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 11:31:36 2019

@author: jrbru

The script finds annotations without metadata
and merges duplicates
"""
import yaml

def main():
    # load yaml
    # deserialise list from yaml
    # load yaml list of model_names in metadata
    with open("model_names.yaml", 'r') as stream:
        model_names = yaml.load(stream)
    # load yaml list of model-name annotations
    with open("phone_image_annotations.yaml", 'r') as stream:
        phone_image_annotations = yaml.load(stream)
    # define string names of lists in a dictionary
    dictionary = dict(phone_image_annotations=phone_image_annotations,
                      model_names=model_names
                      )
    
    # list of annotations without_metadata
    list_without_metadata = []
    # check for annotations without_metadata
    for i_annotations in range(len(phone_image_annotations)):
        is_in_list = False
        for i_metadata in range(len(model_names)):
            if model_names[i_metadata] == phone_image_annotations[i_annotations]:
                is_in_list = True
        if not is_in_list:
            list_without_metadata.append(phone_image_annotations[i_annotations])
    
    if len(list_without_metadata) > 0:
        # print list of model names in metadata
        print('Annotations without metadata:')
        for i_annotations in range(len(list_without_metadata)):
            print('Index ' + str(i_annotations) + ':')
            print(list_without_metadata[i_annotations])
    
        # ask for string to be corrected
        print('Which byte string would you like to manipulate?')
        index_string = input("Index: ")  # reading string that is to be corrected
        indices_for_correction = [int(s) for s in index_string.split() if s.isdigit()]
        index_for_correction = indices_for_correction[0]
        print('If the model name that you want to correct is')
        incorrect_name = model_names[index_for_correction]
        print(incorrect_name)
        print(', please enter the corrected model name. Otherwise, press control+C.')
        correct_string = input("Correct name: ")
        correct_name = correct_string.encode('utf-8')  # read correct name as bytes
    
        # rename annotations in dataset
        for i_annotations in len(phone_image_annotations):
            if phone_image_annotations[i_annotations] == list_without_metadata[index_for_correction]:
                phone_image_annotations[i_annotations] = correct_name
        print('New model name in phone_image_annotations: ')
        print(correct_name)
    else:
        print('There are no annotations without metadata.')
    
    # save yaml
    for key, value in dictionary.items():
        stream = open('' + key + '.yaml', 'w')
        yaml.dump(value, stream)
