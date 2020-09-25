# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 15:13:15 2020

@author: Johannes-Robert Bruch

This script helps you to scrape annotated images from online adverts and build a tfrecord from it.
It needs the yaml, requests, urllib3, certifi, re, time, math, random, pillow, io, os, numpy and datetime packages
"""
import create_yaml_lists
import scraper
import check_model_names
import check_annotations
import remove_images_with_URL_duplicates
import remove_annotated_images
import tfrecord_pipeline

def main():
    print('To skip a step, press enter without typing "yes".')
    answer=input('Enter yes to overwrite or create the database.')
    if 'yes'==answer:
        create_yaml_lists.main()
    else:
        print('We will skip this and continue with the next step:')
        
    answer=input('Enter yes to start building a web scraper for images.')
    if 'yes'==answer:
        scraper.main()
    else:
        print('We will skip this and continue with the next step:')
        
    answer=input('Enter yes to check the new product names.')
    if 'yes'==answer:
        check_model_names.main()
    else:
        print('We will skip this and continue with the next step:')
        
    answer=input('Enter yes to check for annotations without metadata.')
    if 'yes'==answer:
        check_annotations.main()
    else:
        print('We will skip this and continue with the next step:')
    
    answer=input('Enter yes to remove images with duplicates in image URLs.')
    if 'yes'==answer:
        remove_images_with_URL_duplicates.main()
    else:
        print('We will skip this and continue with the next step:')
        
    answer=input('Enter yes to remove images with annotations and URL specified by filename of the image.')
    if 'yes'==answer:
        remove_annotated_images.main()
    else:
        print('We will skip this and continue with the next step:')
        
    answer=input('Enter yes to build tfrecord with data augmentation.')
    if 'yes'==answer:
        tfrecord_pipeline.main()
    else:
        print('We skipped this.')
        

        
