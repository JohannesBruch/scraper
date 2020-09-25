# create_yaml
This file contains the function for creating or overwriting the existing database.

# scraper
This is a web scraper for saving annotated images and metadata from websites with advert lists.

# check_model_names
This contains the function for correcting the labels that are used as annotations.

# check_annotations
This contains the function for checking whether there are annotated images which do not have any metadata assosiated with them.

# remove_annotated_images
This contains a function that helps the user to remove images and annotations from the database, if they specify the filenames of the respective images. After looking at the images, this can be helpful.

# remove_images_with_URL_duplicates
This contains a function for checking for duplicates in the URLs and removing all but one of the assosiated images.

# ftrecord_pipeline
This contains functions to increase the dataset size by augmentation including the replacement of each image by four copies with random deviations. The resulting dataset is saved in the tfrecord format that is part of the tensorflow package.

# web_pipeline
This file just helps you to call the main functions of the other files in a sensible order.
