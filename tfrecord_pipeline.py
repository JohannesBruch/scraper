# -*- coding: utf-8 -*-
"""
Created on March 06 2019
tfrecord usage as explained on https://www.tensorflow.org/tutorials/load_data/tf_records
@author: jrbru
"""
from __future__ import absolute_import, division, print_function

import tensorflow as tf
tf.enable_eager_execution()

from PIL import Image
import yaml, random, os
import numpy as np
dataset_version = 0
# height = width of an image =
_DEFAULT_IMAGE_SIZE = 500


# The following functions can be used to convert a value to a type compatible
# with tf.Example.
def _bytes_feature(value):
    """Returns a bytes_list from a string / byte."""
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


def _float_feature(value):
    """Returns a float_list from a float / double."""
    return tf.train.Feature(float_list=tf.train.FloatList(value=[value]))


def _int64_feature(value):
    """Returns an int64_list from a bool / enum / int / uint."""
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))


def serialize_example(feature0, feature1, labels):
    """Creates a serialised tf.Example message ready to be written to a file.
    A tf.Example is a dictionary that maps {"string": tf.train.Feature}. 
    tf.train.Feature can accept three types: BytesLists, FloatList, and 
    Int64List.

    Parameters
    ------------
    feature0: bytes list
        the first feature to be added to serialised example
    labels: bytes list
        the second feature to be added to serialised example

    Returns
    -------
    example_proto: bytes
        a serialised tf.train.Example
    """
    # Create a dictionary mapping the feature name to the tf.Example-compatible
    # data type.
    feature = {
               'feature0': _bytes_feature(feature0),
               'feature1': _bytes_feature(feature1),
               'labels': _int64_feature(labels),
               }
    # Create a Features message using tf.train.Example.
    example_proto = tf.train.Example(features=tf.train.Features(feature=feature))
    return example_proto.SerializeToString()


def tf_serialize_example(f0, f1, f2):
    """Use the tf.data.Dataset.map method to apply a function to each element
    of a Dataset. The mapped function must operate in TensorFlow graph mode:
    It must operate on and return tf.Tensors. A non-tensor function, like
    serialise_example, can be wrapped with tf.py_func to make it compatible.
    Using tf.py_func requires that you specify the shape and type information
    that is otherwise unavailable:

    Parameters
    ------------
    f0: bytes list
        the first feature to be passes to serialized_example
    f1: bytes list
        the second feature to be passes to serialized_example

    Returns
    -------
    tf_scalar: tf.Tensor
        a tensor containing the serialised dataset (f1,f0)
    """
    tf_string = tf.py_func(
                           serialize_example,
                           (f0, f1, f2),   # pass these args to the above function.
                           tf.string)  # the return type is <a href="../../api_docs/python/tf#string"><code>tf.string</code></a>.
    tf_scalar = tf.reshape(tf_string, ())  # The result is a scalar
    return tf_scalar


def _parse_function(example_proto):
    ''' tf.tensors can be parsed using the function below.
    Alternatively, you can use tf.parse example to parse a whole batch at once.
    '''
    # Create a description of the features. 
    feature_description = {
                           'feature0': tf.FixedLenFeature([], tf.string, default_value=''),
                           'feature1': tf.FixedLenFeature([], tf.string, default_value=''),
                           'labels': tf.FixedLenFeature([], tf.int64, default_value=-1),
                           }
    # Parse the input tf.Example proto using the dictionary above.
    # Or use tf.parse example to parse a whole batch of examples at once
    # return tf.parse_example(example_proto, feature_description)
    return tf.parse_single_example(example_proto, feature_description)

def main():
    # reduce warning level to avoid warning about CPU extensions
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    # load yaml
    # three lists which are meant to keep same length
    with open("phone_images.yaml", 'r') as stream:
        phone_images = yaml.load(stream)
    with open("phone_image_annotations.yaml", 'r') as stream:
        phone_image_annotations = yaml.load(stream)
    with open("phone_image_URLs.yaml", 'r') as stream:
        phone_image_URLs = yaml.load(stream)
    # another 6 lists which are meant to keep same length
    with open("model_names.yaml", 'r') as stream:
        model_names = yaml.load(stream)
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
    # =============================================================================
    # # another list
    # with open("exception_URLs.yaml", 'r') as stream:
    #     exception_URLs = yaml.load(stream)
    # =============================================================================
    
    # define filename for writing and reading tfrecord
    filename = 'PI_dataset' + str(dataset_version) + '.tfrecords'
    
    # create instance of writer used in tf.data pipeline
    writer = tf.data.experimental.TFRecordWriter(filename)
    
    # define lists used in image standardisation
    # a lists containing the respective indices of depicted phone model in metadata for all for rotations
    PI_metadata_indices = []
    # a lists containing the respective URLs images for all for rotations
    PI_URLs = []
    # a list containing data of individual images as four rotated ndarrays each
    PI_arrays = []
    # PI_arrays serialised into bytes
    PI_bytes = []
    
    # load images and  integer annotations into tf.data.dataset
    for i_rot in range(4):
        # a lists containing the respective indices of depicted phone model in metadata
        phone_image_metadata_indices = []
        # a list containing data of individual images as one ndarray each
        PI_array_list = []
        for i_PI in range(len(phone_images)):
            # load image path, but do not open until requested
            img = np.array(Image.open(phone_images[i_PI]))
            # open img to append list with 3darray of image img
            PI_array_list.append(img)
            # make a list of metadata_indices from phone_image_annotations
            phone_image_metadata_indices.append(int(model_names.index(phone_image_annotations[i_PI])))
        
            # resize and pad images to standard size
            ''' create an ndarrays of zeros with shape of PI_array_list[i_PI] and one
            extra dimension with length one, as the resize_area function expects
            a 4darray with the first dimension being a list of images'''
            PI_temp = np.empty((1,PI_array_list[i_PI].shape[0],PI_array_list[i_PI].shape[1],PI_array_list[i_PI].shape[2]))
            PI_temp[0, :, :, :] = PI_array_list[i_PI]
            ''' The larger dimension will be resized to _DEFAULT_IMAGE_SIZE pixels.
            By the resize_area function each output pixel is computed by first
            transforming the pixel's footprint into the input tensor and then
            averaging the pixels that intersect the footprint.
            An input pixel's contribution to the average is
            weighted by the fraction of its area that intersects the footprint.
            This is the same as OpenCV's INTER_AREA.'''
            if PI_temp.shape[2] < PI_temp.shape[1]:
                PI_array_list[i_PI] = tf.image.resize_area(PI_temp,
                                                           [_DEFAULT_IMAGE_SIZE,
                                                            int(_DEFAULT_IMAGE_SIZE*(PI_temp.shape[2]/PI_temp.shape[1]))]
                                                           )
            else:
                PI_array_list[i_PI] = tf.image.resize_area(PI_temp,
                                                           [int(_DEFAULT_IMAGE_SIZE*(PI_temp.shape[1]/PI_temp.shape[2])),
                                                            _DEFAULT_IMAGE_SIZE]
                                                           )
            # the smaller dimension is padded with zeros to make the image squared
            PI_array_list[i_PI] = tf.image.resize_image_with_pad(PI_array_list[i_PI],
                                                                 _DEFAULT_IMAGE_SIZE,
                                                                 _DEFAULT_IMAGE_SIZE,
                                                                 method=tf.image.ResizeMethod.AREA
                                                                 )
            # manipulate fixed percentage of values randomly
            PI_temp= np.array(PI_array_list[i_PI])
            n_values_per_image = PI_temp.shape[1] * PI_temp.shape[2] * PI_temp.shape[3]
            sample_indices = random.sample(range(n_values_per_image), int(n_values_per_image * 0.01))
            for i_sample in sample_indices:
                channel = int(i_sample / (PI_temp.shape[1] * PI_temp.shape[2]))
                channel_remainder = i_sample % (PI_temp.shape[1] * PI_temp.shape[2])
                width = int(channel_remainder / (PI_temp.shape[1]))
                height = channel_remainder % (PI_temp.shape[1])
                PI_temp[0, height, width, channel] = random.randrange(256)
            PI_array_list[i_PI] = PI_temp
            # rotate image by 90degree*i_rot
            PI_array_list[i_PI] = tf.image.rot90(PI_array_list[i_PI],i_rot)
            # cast float values into uint8 values
            PI_temp = tf.cast(PI_array_list[i_PI], tf.uint8)
            # serialise ndarray to bytes in jpg format
            PI_array_list[i_PI] = tf.image.encode_jpeg(PI_temp[0, :, :, :], "rgb", 100)
        PI_arrays.extend(PI_array_list)
        PI_URLs.extend(phone_image_URLs)
        PI_metadata_indices.extend(phone_image_metadata_indices)
                
    # =============================================================================
    #         print('Height:')
    #         print(PI_array_list[i_PI].shape[1])
    #         print('Width:')
    #         print(PI_array_list[i_PI].shape[2])
    #         print('Channels:')
    #         print(PI_array_list[i_PI].shape[3])
    # =============================================================================
    
    ''' a tf.data.Dataset is created from three lists of bytes objects with same
    lengths.'''
    dataset = tf.data.Dataset.from_tensor_slices((PI_arrays,
                                                  PI_URLs,
                                                  PI_metadata_indices))
    PI_dataset = dataset.shuffle(len(phone_images),
                                 reshuffle_each_iteration=False)
    
    # =============================================================================
    # for f0, f1 in PI_dataset.take(2):
    #     print(f0)
    #     print(f1)
    # =============================================================================
    
    ''' Use map function to apply tf_serialize_example to each element of
    PI_dataset, which only has one element. This element contains two tf.tensors.
    tf_serialize_example creates a serialised tf.Example message with PI_array_list
    and phone_image_annotations as features.'''
    serialized_PI_dataset = PI_dataset.map(tf_serialize_example)
    # save tfrecord of tf.data.Dataset to persistent storage
    writer.write(serialized_PI_dataset)
    
    # a list that only contains the filename of the dataset to be loaded is created
    filenames = [filename]
    ''' a tf.data.Dataset is created by loading a list of tfrecords from persistent
    storage.'''
    raw_dataset = tf.data.TFRecordDataset(filenames)
    print('Raw dataset')
    print(raw_dataset)
    # =============================================================================
    # for raw_record in raw_dataset.take(10):
    #     print(repr(raw_record))
    # =============================================================================
    '''To parse a dataset consisting out of tf.tensors from a tfrecord, we apply
    _parse_function to each item in the dataset using the
    tf.data.Dataset.map method '''
    parsed_dataset = raw_dataset.map(_parse_function)
    print('Parsed dataset')
    print(parsed_dataset)
    
    annotations = []
    counter = 0
    for parsed_record in parsed_dataset:  # enter image index
        annotation = np.array(parsed_record["labels"])
        annotations.append(annotation)
        print('annotation: ' + str(counter))
        print(annotation)
        counter = counter + 1
    
    annotations_key = 'PI_annotations' + str(dataset_version)
    dictionary = dict( # PI_URLs=PI_URLs,
                      [(annotations_key, annotations)],
                      )
    # save yaml
    for key, value in dictionary.items():
        stream = open('' + key + '.yaml', 'w')
        yaml.dump(value, stream)
