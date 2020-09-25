# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 11:31:36 2019

@author: jrbru

The script removes URL duplicates
"""
import yaml, os

def main():
    # load yaml
    # deserialise list from yaml
    # load yaml list of image addresses
    with open("phone_images.yaml", 'r') as stream:
        phone_images = yaml.load(stream)
    # load yaml list of model-name annotations
    with open("phone_image_annotations.yaml", 'r') as stream:
        phone_image_annotations = yaml.load(stream)
    # load yaml list of image source URLs
    with open("phone_image_URLs.yaml", 'r') as stream:
        phone_image_URLs = yaml.load(stream)
    # define string names of lists in a dictionary
    dictionary = dict(phone_image_URLs=phone_image_URLs,
                      phone_image_annotations=phone_image_annotations,
                      phone_images=phone_images
                      )
    
    indices_to_pop = []
    # duplicate_URLs = []
    for i_URLs in range(len(phone_image_URLs)):
        is_duplicate = False
        for i_URLs_2 in range(i_URLs + 1, len(phone_image_URLs)):
            if phone_image_URLs[i_URLs] == phone_image_URLs[i_URLs_2]:
                indices_to_pop.append(i_URLs)
                is_duplicate = True
                break
    indices_to_pop.reverse()
    for i_to_pop in indices_to_pop:
        # duplicate_URLs.append(phone_image_URLs[i_to_pop])
        phone_image_URLs.pop(i_to_pop)
        phone_image_annotations.pop(i_to_pop)
        image_path = phone_images.pop(i_to_pop)
        print('The address ' + image_path + ' has been removed from the dataset together with its annotation & URL,')
        # If file exists, delete it ##
        if os.path.isfile(image_path):
            os.remove(image_path)
            print('and the .jpg file was deleted.')
        else:    # Show an error ##
            print("but the .jpg file was not found. ERROR!")
    
    # save yaml
    for key, value in dictionary.items():
        stream = open('' + key + '.yaml', 'w')
        yaml.dump(value, stream)

