# -*- coding: utf-8 -*-
"""
Created on Tue Feb 26 09:35:07 2019

@author: jrbru
"""
import yaml

def main():

    dictionary = dict(phone_images=[],
                      phone_image_annotations=[],
                      phone_image_URLs=[],
                      model_names=[],
                      average_prices=[],
                      latest_prices=[],
                      addition_dates=[],
                      latest_update_dates=[],
                      occurence_numbers=[],
                      exception_URLs=[]
                      )

    # saving all lists by serialising to yaml
    for key, value in dictionary.items():
        stream = open('' + key + '.yaml', 'w')
        yaml.dump(value, stream)
