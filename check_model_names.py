# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 11:31:36 2019

@author: jrbru

The script asks a user to correct model_names via console
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
    
    # print list of model names in metadata
    print('Model names in metadata list:')
    for i_m in range(0, len(model_names)):
        print('Index ' + str(i_m) + ':')
        print(model_names[i_m])
    
    # ask for string to be corrected
    print('Which byte string would you like to manipulate?')
    index_string = input("Index: ")  # reading string that is to be corrected
    indices_for_correction = [int(s) for s in index_string.split() if s.isdigit()]
    i_for_correction = indices_for_correction[0]
    print('If the model name that you want to correct is')
    incorrect_name = model_names[i_for_correction]
    print(incorrect_name)
    print(', please enter the corrected model name. Otherwise, only press enter.')
    correct_string = input("Correct name: ")
    if correct_string != '':
        correct_name = correct_string.encode('utf-8')  # read correct name as bytes
        
        # check for duplicates
        indices_for_correction = []
        is_in_list = False
        for i_metadata in range(0, len(model_names)):
            if type(model_names[i_metadata]) == bytes:
                if model_names[i_metadata] == correct_name:
                    is_in_list = True
                    break
        if is_in_list is True and correct_name != incorrect_name:
            # load lists to be changed
            with open("average_prices.yaml", 'r') as stream:
                average_prices = yaml.load(stream)
            with open("latest_prices.yaml", 'r') as stream:
                latest_prices = yaml.load(stream)
            with open("addition_dates.yaml", 'r') as stream:
                addition_dates = yaml.load(stream)
            with open("latest_update_dates.yaml", 'r') as stream:
                latest_update_dates = yaml.load(stream)
            with open("occurence_numbers.yaml", 'r') as stream:
                occurence_numbers = yaml.load(stream)
            # append dictionary
            dictionary = dict(phone_image_annotations=phone_image_annotations,
                          model_names=model_names,
                          average_prices=average_prices,
                          latest_prices=latest_prices,
                          addition_dates=addition_dates,
                          latest_update_dates=latest_update_dates,
                          occurence_numbers=occurence_numbers,
                          )
            for index_for_correction in range(len(model_names)):
                if model_names[index_for_correction] == incorrect_name:
                    # merge into first occurence in metadata
                    if type(average_prices[index_for_correction]) == float and type(average_prices[i_metadata]) == float:
                        average_prices[i_metadata] = (average_prices[index_for_correction] * occurence_numbers[index_for_correction] + average_prices[i_metadata] * occurence_numbers[i_metadata]) / (occurence_numbers[index_for_correction] + occurence_numbers[i_metadata])
                        occurence_numbers[i_metadata] = occurence_numbers[i_metadata] + occurence_numbers[index_for_correction]
                    # override if no previous price available
                    elif type(average_prices[index_for_correction]) == float:
                        average_prices[i_metadata] = average_prices[index_for_correction]
                        occurence_numbers[i_metadata] = occurence_numbers[index_for_correction]
                    # override if previous prices not as up-to-date
                    if latest_update_dates[i_metadata] < latest_update_dates[index_for_correction]:
                        latest_update_dates[i_metadata] = latest_update_dates[index_for_correction]
                        latest_prices[i_metadata] = latest_prices[index_for_correction]
                    # override if previous addition date is more recent
                    if addition_dates[i_metadata] > addition_dates[index_for_correction]:
                        addition_dates[i_metadata] = addition_dates[index_for_correction]
                    indices_for_correction.append(index_for_correction)
            indices_for_correction.reverse()
            indices_for_correction_r = indices_for_correction
            for index_for_correction in indices_for_correction_r:
                    # delete other occurence
                    model_names.pop(index_for_correction)
                    average_prices.pop(index_for_correction)
                    latest_prices.pop(index_for_correction)
                    addition_dates.pop(index_for_correction)
                    latest_update_dates.pop(index_for_correction)
                    occurence_numbers.pop(index_for_correction)
            print('Entries with same model name MERGED')
        if is_in_list is False:
            model_names[i_for_correction] = correct_name  # override model name
        
        # rename annotations in dataset
        for i_annotations in range(0, len(phone_image_annotations)):
            if phone_image_annotations[i_annotations] == incorrect_name:
                phone_image_annotations[i_annotations] = correct_name
        
        # save yaml
        for key, value in dictionary.items():
            stream = open('' + key + '.yaml', 'w')
            yaml.dump(value, stream)
        
        print('New model name in model_names and phone_image_annotations: ')
        print(correct_name)
        # print('Do not forget to check_annotations without metadata.')
    else:
        print('Data was not changed.')
    '''
    the following could be extracted from model names
    manufacturers = ['Apple', 'Samsung', 'Google', 'LG']
    '''
