# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 11:31:36 2019

@author: jrbru

The script removes images, image URLs and annotations that are specified by the user.
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
    
    # ask for address of DATA to be DELETED
    print('Which images would you like to delete from the PI dataset?')
    index_string = input("Lowest address: ")  # reading address of first image to be removed
    addresses_for_correction = [int(s) for s in index_string.split()
                                if s.isdigit()]
    lowest_address = addresses_for_correction[0]
    index_string = input("Highest address: ")  # reading address of last image to be removed
    addresses_for_correction = [int(s) for s in index_string.split()
                                if s.isdigit()]
    highest_address = addresses_for_correction[0]
    print('If you want to remove all images with addresses between')
    print(lowest_address)
    print('and')
    print(highest_address)
    print(', please reply "y" . Otherwise, the dataset will not be modified.')
    correct_string = input("Reply: ")
    if correct_string == 'y' and highest_address-lowest_address+1 > 10:
        print('Are you sure you want to DELETE that many images?.')
        correct_string = input("Reply: ")
    if correct_string == 'y':
        for address_for_correction in range(lowest_address, highest_address + 1):
            image_path = r'' + str(address_for_correction) + '.jpg'
            #  remove image from dataset
            try:
                image_index = phone_images.index(image_path)
                phone_image_URLs.pop(image_index)
                phone_image_annotations.pop(image_index)
                phone_images.pop(image_index)
                print('The address ' + str(address_for_correction) + '.jpg has been removed from the dataset together with its annotation & URL,')
            except ValueError:
                print('Address' + str(address_for_correction) + 'was not found,')
            # If file exists, delete it ##
            if os.path.isfile(image_path):
                os.remove(image_path)
                print('and the .jpg file was deleted.')
            else:    # Show an error ##
                print("but the .jpg file was not found.")
    
        # save yaml
        for key, value in dictionary.items():
            stream = open('' + key + '.yaml', 'w')
            yaml.dump(value, stream)
    else:
        print('The dataset has not been modified.')
