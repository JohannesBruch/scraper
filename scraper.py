# -*- coding: utf-8 -*-
"""
Created on 2018_03_28

@author: jrbru

The script extracts annotated images and metadata from the website that you specify via the console.
"""
# import complete packages
import requests, urllib3, certifi, re, yaml, time, math, random
# import members of packages
from PIL import Image
from io import BytesIO
from datetime import date

# define Python user-defined exceptions
class Error(Exception):
    """Base class for other exceptions"""
    pass

class CurrencyNotDefinedError(Error):
    """Raised when the currency does not match any of the expected currencies"""

def extract_proxy(URL, pre_pattern, start, end, post_pattern, c_exclude,
                  c_start, c_end, is_too_much):
    """
    extracting URLs from a URL based on regular expressions
    Created on Thu Jan 24 13:29:00 2019
    @author: jrbru

    Parameters
    ------------
    URL: bytes
        the url that is opened
    pre_pattern: bytes
        the pattern in the data that is expected directly before relevant links
    start: bytes
        the first sequence in the byte_list to be extracted
    end: bytes
        the last sequence in the byte_list to be extracted
    post_pattern: bytes
        the pattern in the data that is expected directly after relevant links
    c_exclude: bytes
        a string of bytes that is contained in links that should be removed 
        from the list byte_list
    c_start: integer
        number of the first byte in each link that is checked for c_exclude
    c_end: integer
        number of the last byte in each link that is checked for c_exclude
    is_too_much: boolean
        True if we want to use the count function for removal of links

    Returns
    -------
    proxies: proxies object
        for requests module
    """

    http = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED',
            ca_certs=certifi.where())
    r = http.request('GET', URL)
    datastr = r.data
    print(b'Search regular expression:' + pre_pattern + start + b'(.+?)' + end + post_pattern)
    links = re.findall(pre_pattern + start + b'(.+?)' + end + post_pattern,
                       datastr)
    # check if the pattern to be excluded is contained in a link
    if is_too_much:
        linksr = links
        linksr.reverse()
        for link in linksr[:]:
            initial = link.count(c_exclude, c_start, c_end)
            if initial == 1:
                links.remove(link)
                initial = 0
    proxy_list = []  # list of bytes tuples with IP and port
    for link in links:
        proxy_list.append(link)

    return proxy_list


def extract_header():
    """
    extracting a random windows user agent from a yaml list
    Created on Thu Jan 24 13:29:00 2019
    @author: jrbru

    Parameters
    ------------

    Returns
    -------
    header: header object
        for requests module
    """
    with open("user_agents.yaml", 'r') as stream:
        user_agents = yaml.load(stream)
    user = user_agents[random.randrange(len(user_agents))]
    user_agent = user.decode("utf-8")
    headers = {'User-Agent': user_agent}
    return headers


def extract_response(URL):
    """
    extracting a response from a URL
    Created on Feb 19 2019
    @author: jrbru

    Parameters
    ----------
    URL: bytes
        the url that is opened

    Returns
    -------
    response: bytes
        the response of a url opened with the requests module
    """
    mu = 2.2389  # mean for sleep times
    sigma = 1.490852389  # std dev for sleep times
    is_proxy = False  # True if we use proxies
    # header extraction from yaml list
    headers = extract_header()
    # defintions for proxy extraction from https://free-proxy-list.net/
    proxy_list_URL = 'https://free-proxy-list.net/'
    pre_pr = b'ago</td></tr><tr><td>'
    start_pr = b''
    end_pr = b'</td><td>(.+?)'
    post_pr = b'</td><td>'
    c_exclude_pr = []
    c_start_pr = []
    c_end_pr = []
    is_too_much_pr = False
    is_connected = False
    if is_proxy:
        proxy_list = extract_proxy(proxy_list_URL, pre_pr, start_pr, end_pr,
                                   post_pr,
                                   c_exclude_pr,
                                   c_start_pr, c_end_pr, is_too_much_pr)
        while is_connected is False:
            try:
                proxy = proxy_list[random.randrange(len(proxy_list))]
                IP = proxy[0].decode("utf-8")
                port = proxy[1].decode("utf-8")
                proxy_spec = 'http://' + IP + ':' + port
                proxies = {
                    "http": proxy_spec,
                    "https": proxy_spec
                }
                response = requests.get(URL,
                                        proxies=proxies,
                                        headers=headers,
                                        timeout=5)
            except:
                print('Probably ProxyError or ConnectTimeout using requests.get')
                continue
            else:
                is_connected = True
                time.sleep(abs(random.gauss(mu, sigma)))
    else:  # is_proxy is False
        proxies = {}
        response = requests.get(URL,
                                proxies=proxies,
                                headers=headers)

        time.sleep(abs(random.gauss(mu, sigma)))  # wait for random period
    return response


def extract_bytes(response, pre_pattern, start, end, post_pattern, c_exclude,
                  c_start, c_end, is_too_much):
    """
    extracting bytes from a URL response based on regular expressions
    Created on Thu Jan 24 2019
    @author: jrbru

    Parameters
    ------------
    response: bytes
        the response of requests package
    pre_pattern: bytes
        the pattern in the data that is expected directly before relevant links
    start: bytes
        the first sequence in the byte_list to be extracted
    end: bytes
        the last sequence in the byte_list to be extracted
    post_pattern: bytes
        the pattern in the data that is expected directly after relevant links
    c_exclude: bytes
        a string of bytes that is contained in links that should be removed
        from the list byte_list
    c_start: integer
        number of the first byte in each link that is checked for c_exclude
    c_end: integer
        number of the last byte in each link that is checked for c_exclude
    is_too_much: boolean
        True if we want to use the count function for removal of links

    Returns
    -------
    byte_list: list of bytes
        this is a list containing all byte strings that are extracted
    """
    datastr = response.content  # bytes that are received via requests module
    print(b'Search regular expression:' + pre_pattern + start + b'(.+?)' + end + post_pattern)
    links = re.findall(pre_pattern + start + b'(.+?)' + end + post_pattern,
                       datastr)
    if is_too_much:
        linksr = links
        linksr.reverse()
        for link in linksr[:]:
            initial = link.count(c_exclude, c_start, c_end)
            if initial > 0:
                links.remove(link)
                initial = 0
    byte_list = []
    for link in links:
        byte_list.append(start + link + end)

    byte_list = list(set(byte_list))  # removes duplicates from list
    return byte_list


def extract_image(response):
    """
    extracting image from a URL using urllib3
    Created on Thu Jan 24 13:29:00 2019
    @author: jrbru

    Parameters
    ------------
    response: bytes
        the response of an url that is opened with requests module

    Returns
    -------
    image_data: jpg
        a RGB image that is stored at the specified URL
    """
    phone_image = Image.open(BytesIO(response.content))
    # phone_images = []
    # phone_images.append(img)
    # this works for saving individual images, but I want to save the list
    # phone_images[0].save('phone_image.jpg')
    return phone_image


def add_annotated_images(image_URLs, model_name, phone_images,
                         phone_image_annotations, phone_image_URLs):
    """
    adding information from an online advert to the dataset.
    Later on, function to remove duplicates must be added.
        Created on Fri Feb 01 2019
    @author: jrbru

    Parameters
    ------------
    image_URLs: list of bytes
        the urls that images are downloaded from by this function
    model_name: bytes
        the name that the phone images will be annotated with
    phone_images: list of image objects in jpg
        the data for machine learning in PI dataset
    phone_image_annotations: list of bytes
        the annotations in PI dataset
    phone_image_URLs: list of bytes
        list of URLs of phone images in PI dataset

    Returns
    -------
    phone_images: list of image objects in jpg
        the appended data for machine learning in PI dataset
    phone_image_annotations: list of bytes
        the appended annotations in PI dataset
    phone_image_URLs: list of bytes
        appended list of URLs of phone images in PI dataset
    """
    for image_URL in image_URLs:
        try:
            image_URL = image_URL.decode('utf-8')
            response = extract_response(image_URL)
            image = extract_image(response)
            last_address = re.findall(r'' + '(\d+)' + '.jpg', phone_images[len(phone_images)-1])
            last_address_int_list = [int(s) for s in last_address[0].split() if s.isdigit()] 
            new_address = last_address_int_list[0] + 1
            image_path = '' + str(new_address) + '.jpg'
            image.save(image_path)
            print('Path of saved image:')
            print(image_path)
# =============================================================================
#             phone_image = skimage.io.imread(image_path)
#             skimage.io.imshow(phone_image)
# =============================================================================
        except:
            print('An image with its annotation and URL could not be added to the lists.')
            return phone_images, phone_image_annotations, phone_image_URLs
        phone_images.append(image_path)
        phone_image_annotations.append(model_name)
        phone_image_URLs.append(image_URL)
    return phone_images, phone_image_annotations, phone_image_URLs


def append_datasets(URL, currency, pre_pattern, start, end, post_pattern,
                    c_exclude,
                    c_start, c_end, is_too_much, pre_p, start_p, end_p, post_p,
                    c_exclude_p, c_start_p, c_end_p, is_too_much_p, pre_t,
                    start_t, end_t, post_t, c_exclude_t, c_start_t, c_end_t,
                    is_too_much_t, phone_images, phone_image_annotations,
                    phone_image_URLs, model_names, average_prices,
                    latest_prices, addition_dates, latest_update_dates,
                    occurence_numbers, exception_URLs,
                    is_new_name, protocol):
    """
    adding information from an online advert to the dataset
        Created on Fri Feb 01 2019
    @author: jrbru

    Parameters
    ------------
    URL: bytes
        the url that is opened
    currency: string
        three letter string indicating the currency of prices on the website
    pre_pattern: bytes
        pattern before image url
    start: bytes
        start of image url
    end: bytes
        end of image url
    post_pattern: bytes
        pattern after image url
    c_exclude: bytes
        pattern to be excluded from list of image urls
    c_start: integer
        position for starting to look for c_exclude in link string
    c_end: integer
        position for stopping to look for c_exclude in link string
    is_too_much: boolean
        true if c_exclude should be searched for in link string
    pre_p: bytes
        pattern before price
    start_p: bytes
        start of price
    end_p: bytes
        end of price
    post_p: bytes
        pattern after price
    c_exclude_p: bytes
        pattern to be excluded from list of prices
    c_start_p: integer
        position for starting to look for c_exclude in price string
    c_end_p: integer
        position for stopping to look for c_exclude in price string
    is_too_much_p: boolean
        true if c_exclude should be searched for in price string
    pre_t: bytes
        pattern before title
    start_t: bytes
        start of title
    end_t: bytes
        end of title
    post_t: bytes
        pattern after title
    c_exclude_t: bytes
        pattern to be excluded from list of titles
    c_start_t: integer
        position for starting to look for c_exclude in title string
    c_end_t: integer
        position for ending to look for c_exclude in title string
    is_too_much_t: boolean
        true if c_exclude should be searched for in title string
    phone_images: list of image objects in jpg
        the data for machine learning in PI dataset
    phone_image_annotations: list of bytes
        the annotations in PI dataset
    phone_image_URLs: list of bytes
        list of URLs of phone images in PI dataset
    model_names: list of bytes
        a set of all names of phone models in the dataset
    average_prices: list of bytes
        the average prices of refurbished phones found in adverts in GBP
    latest_prices: list of bytes
        the average of the prices shown in the latest added advert in GBP
    addition_dates: list of date objects
        date of the first entry of this phone model into dataset (UK time)
    latest_update_dates: list of date objects
        date of the latest update of this entry in dataset (UK time)
    occurence_numbers: list of integers
        the number of prices that were found in its adverts since the model was
        added to the dataset
    exception_URLs: list of bytes
        URLs from which no title or no images was retrieved
    is_new_name: Boolean
        set to True if new name was added during execution
    Returns
    -------
    phone_images: list of image objects in jpg
        the appended data for machine learning in PI dataset
    phone_image_annotations: list of bytes
        the appended annotations in PI dataset
    phone_image_URLs: list of bytes
        appended list of URLs of phone images in PI dataset
    model_names: list of bytes
        appended set of all names of phone models in the dataset
    average_prices: list of bytes
        updated list of average prices of refurbished phones found in adverts
    latest_prices: list of bytes
        updated list of  average of the prices shown in the latest added advert
    addition_dates: list of date objects
        appended list of dates of the first entries of phone models into
        the datasets (UK time)
    latest_update_dates: list of date objects
        updated list of dates of the latest updates of entries in this dataset
        (UK time)
    occurence_numbers: list of integers
        updated list of the numbers of prices that were found in its adverts
        since the models were added to the datasets
    exception_URLs: list of bytes
        appended list of URLs from which no title or no images was retrieved
    is_new_name: Boolean
        set to True if new name was added during execution
    """
    i_metadata = []
    prices = []
    today = date.fromtimestamp(time.time())
    response = extract_response(URL)
    titles = extract_bytes(response, pre_t, start_t, end_t, post_t, c_exclude_t,
                           c_start_t, c_end_t, is_too_much_t)
    if len(titles) < 1:
        exception_URLs.append(URL)
        return phone_images, phone_image_annotations, phone_image_URLs,
        model_names, average_prices, latest_prices, addition_dates,
        latest_update_dates, occurence_numbers, exception_URLs, is_new_name
    print('Extract titles:')
    print(titles)
    # Extracting prices
    prices = extract_bytes(response, pre_p, start_p, end_p, post_p,
                           c_exclude_p, c_start_p, c_end_p, is_too_much_p)
    # try alternative pattern for price extraction
    if len(prices) == 0:
            prices = extract_bytes(response, pre_p2, start_p2, end_p2, post_p2,
                                   c_exclude_p2, c_start_p2, c_end_p2, 
                                   is_too_much_p2)
    print('Extract prices:')
    print(prices)
    try:
        if currency == 'GBP':  # prices will be stored in pound sterling
            currency_conversion = 1
            decimal_symbol = b'\.?'
            thousands_symbol = b',?'
        elif currency == 'EUR':
            currency_conversion = 0.9
            decimal_symbol = b',?'
            thousands_symbol = b'\.?'
        elif currency == 'USD':
            currency_conversion = 0.8
            decimal_symbol = b'\.?'
            thousands_symbol = b',?'
        else:
            raise CurrencyNotDefinedError
    except CurrencyNotDefinedError:
        print("This currency is not defined.")
        print('Please add new currency to conversion table at beginning of append_datasets function.')
        print()
        prices = []
    # We only process metadata if prices are available
    if len(prices) > 0:
        
        for i_p in range(len(prices)):
            bytes_price = re.findall(b'\d*'
                                     + thousands_symbol
                                     + b'-?\d+'
                                     + decimal_symbol
                                     + b'\d*', prices[i_p])
            # If we allowed for thousands separators, this would be needed:
# =============================================================================
#             if decimal_symbol == b'\.?':
#                 formated_price = re.sub(b'\,?', b'', bytes_price)
# =============================================================================
            # for conversion into float the decimal symbol must be '.'
            if decimal_symbol == b',?':
                formated_price = re.sub(b',', b'.', bytes_price[0])
            else:
                formated_price = bytes_price[0]
            prices[i_p] = [float(s) for s in formated_price]
            # b'-?\d+\.?\d*' matches real numbers with point as decimal symbol
            price_temp = prices[i_p]  # a list containing one element
            prices[i_p] = price_temp[0] * currency_conversion  # price in GBP
        average = math.fsum(prices)/len(prices)
    else:
        average = []
# Find all known model_names contained in title
# select longest among them for merging of metadata
    index_list = []
    i_metadata = []
    bytes_length = 0
    for title in titles:
        if type(title) == bytes:
            for i_names in range(len(model_names)):
                if type(model_names[i_names]) == bytes:
                    result = re.fullmatch(b'(.+?)' + model_names[i_names].lower(),
                                      title.lower())
                    if result is not None:
                        index_list.append(i_names)
# Select longest model name that is contained in title
    for i_list in index_list:
        if bytes_length < len(model_names[i_list]):
            bytes_length = len(model_names[i_list])
            i_metadata = i_list
# =============================================================================
#             if title == model_names[i_names]:
#                 i_metadata = i_names
#                 break
# =============================================================================
    if i_metadata == []:  
        # if we need to add a modelname, a human needs to check it.
        is_new_name = True
        i_metadata = len(model_names)
        model_names.append(titles)
        average_prices.append(average)
        latest_prices.append(average)
        addition_dates.append(today)
        latest_update_dates.append(today)
        occurence_numbers.append(len(prices))
    elif len(prices) > 0:
        average_prices[i_metadata] = (average * len(prices) + average_prices[i_metadata] * occurence_numbers[i_metadata]) / (len(prices) + occurence_numbers[i_metadata])
        latest_prices[i_metadata] = average
        latest_update_dates[i_metadata] = today
        occurence_numbers[i_metadata] = occurence_numbers[i_metadata] + len(prices)

    # extracting URLs of phone images in individual adverts on ebay.com
    image_URLs = extract_bytes(response, pre_pattern, start, end, post_pattern,
                               c_exclude, c_start, c_end, is_too_much)
    # adding protocol definition to URL
    for i_URLs in range(len(image_URLs)):
        image_URLs[i_URLs] = protocol + image_URLs[i_URLs]
    print(image_URLs)
    # skip extracting images, if no image URLs found
    if len(image_URLs) < 1:
        exception_URLs.append(URL)
        return phone_images, phone_image_annotations, phone_image_URLs,
        model_names, average_prices, latest_prices, addition_dates,
        latest_update_dates, occurence_numbers, exception_URLs, is_new_name
    else:  # if len(image_URLs) >= 1:
        previous_phone_image_URLs = phone_image_URLs
        previous_phone_image_URLs.reverse()
        indices_to_pop = []
        for i_URLs in range(len(image_URLs)):
            is_duplicate = False
            # check if image_URLs contains duplicates
            for i_URLs_2 in range(i_URLs + 1, len(image_URLs)):
                if image_URLs[i_URLs] == image_URLs[i_URLs_2]:
                    indices_to_pop.append(i_URLs)
                    is_duplicate = True
                    break
            if is_duplicate is False:
                # check if image_URLs and phone_image_URLs contain duplicates
                for previous_image_URL in previous_phone_image_URLs:
                    if image_URLs[i_URLs] == previous_image_URL:
                        indices_to_pop.append(i_URLs)
                        break
        # remove duplicates from image_URLs
        indices_to_pop.reverse()
        for i_to_pop in indices_to_pop:
            image_URLs.pop(i_to_pop)
        # appending list of annotated images
        if len(image_URLs) > 0:
            add_annotated_images(image_URLs,
                                 model_names[i_metadata],
                                 phone_images,
                                 phone_image_annotations,
                                 phone_image_URLs)
        return phone_images, phone_image_annotations, phone_image_URLs,
        model_names, average_prices, latest_prices, addition_dates,
        latest_update_dates, occurence_numbers, exception_URLs


# body
# Defintions of Booleans for execution summary:
# If we need to add a modelname, a human needs to check it.
# The initial assumption is that no new names of phones will be added.
is_new_name = False
# definitions for title extraction
pre_t = bytes(input('What is just in front of the title of the advert: '))
start_t = bytes(input('What is at the start of the title of the advert: '))
end_t = bytes(input('What is at the end of the title of the advert: '))
post_t = bytes(input('What is just behind the title of the advert: '))
is_too_much_t = False
if input('Enter "y", if some should be excluded although they fulfil this pattern.')=='y':
    is_too_much_t = True
c_exclude_t = bytes(input('Links with this pattern will be exluded: '))
c_start_t = int(input('We will make an exception for this rule if the pattern only appear before this index: '))
c_end_t = int(input('And/or after this index: '))

# definitions for price extraction
pre_p = bytes(input('What is usually just in front of the price of the product: '))
start_p = b''
end_p = b''
post_p = bytes(input('What is usually just behind the price of the product: '))
is_too_much_p = False
if input('Enter "y", if some should be excluded although they fulfil this pattern.')=='y':
    is_too_much_p = True
c_exclude_p = bytes(input('Links with this pattern will be exluded: '))
c_start_p = int(input('We will make an exception for this rule if the pattern only appear before this index: '))
c_end_p = int(input('And/or after this index: '))

# alternative definitions for price extraction
pre_p2 = bytes(input('What is alternatively just in front of the price of the product: '))
start_p2 = b''
end_p2 = b''
post_p2 = bytes(input('What is alternatively just behind the price of the product: '))
is_too_much_p2 = False
if input('Enter "y", if some should be excluded although they fulfil this pattern.')=='y':
    is_too_much_p2 = True
c_exclude_p2 = bytes(input('Links with this pattern will be exluded: '))
c_start_p2 = int(input('We will make an exception for this rule if the pattern only appear before this index: '))
c_end_p2 = int(input('And/or after this index: '))

# definitions for image extraction in individual adverts
protocol = bytes(input('Enter the protocol here, if it is not found at the beginning of the image URL: '))
pre_pattern = bytes(input('What is just in front of the image URL: '))
start = bytes(input('What is at the beginning of the image URL: '))
end = bytes(input('What is at the end of the image URL: '))
post_pattern = bytes(input('What is just behind the image URL: '))
is_too_much = False
if input('Enter "y", if some should be excluded although they fulfil this pattern.')=='y':
    is_too_much = True
c_exclude = bytes(input('Links with this pattern will be exluded: '))
c_start = int(input('We will make an exception for this rule if the pattern only appear before this index: '))
c_end = int(input('And/or after this index: '))

# definitions for extracting URLs of phone advert list
next_URL = bytes(input('What is the URL that shows the beginning of the advert list: '))  # inital URL
currency = bytes(input('What is the ISO 4217 code of the currency on this site: ')) # currency of prices on website as three letter code
counter = 0
URL_predial = bytes(input('What do we have to add to the beginning of the URL part that the site will provide for the individual adverts: '))
URL_extension = bytes(input('What do we have to add to the end of the URL part that the site will provide for the individual adverts: '))
pre_pattern_u = bytes(input('What is just in front of that URL part: '))
start_u = bytes(input('What is at the beginning of that URL part: '))
end_u = bytes(input('What is at the end of that URL part: '))
post_pattern_u = bytes(input('What is just behind that URL part: '))'
is_too_much_u = False
if input('Enter "y", if some should be excluded although they fulfil this pattern.')=='y':
    is_too_much_u = True
c_exclude_u = bytes(input('Links with this pattern will be exluded: '))
c_start_u = int(input('We will make an exception for this rule if the pattern only appear before this index: '))
c_end_u = int(input('And/or after this index: '))

# definitions for finding next page of advert list
pre_pattern_n = bytes(input('What is just in front of the URL for the next page of the list: '))
start_n = bytes(input('What is at the beginning of the URL for the next page of the list: '))
end_n = bytes(input('What is at the end of the URL for the next page of the list: '))
post_pattern_n = bytes(input('What is just behind the URL for the next page of the list: '))
is_too_much_n = False
if input('Enter "y", if some should be excluded although they fulfil this pattern.')=='y':
    is_too_much_n = True
c_exclude_n = bytes(input('Links with this pattern will be exluded: '))
c_start_n = int(input('We will make an exception for this rule if the pattern only appear before this index: '))
c_end_n = int(input('And/or after this index: '))


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
# another list
with open("exception_URLs.yaml", 'r') as stream:
    exception_URLs = yaml.load(stream)

dictionary = dict(phone_images=phone_images,
                  phone_image_annotations=phone_image_annotations,
                  phone_image_URLs=phone_image_URLs,
                  model_names=model_names,
                  average_prices=average_prices,
                  latest_prices=latest_prices,
                  addition_dates=addition_dates,
                  latest_update_dates=latest_update_dates,
                  occurence_numbers=occurence_numbers,
                  exception_URLs=exception_URLs
                  )

while True:
    # extracting URLs of phone advert list on ebay.com
    response = extract_response(next_URL)
    # print(response.content)
    URLs = extract_bytes(response, pre_pattern_u, start_u, end_u,
                         post_pattern_u, c_exclude_u, c_start_u, c_end_u,
                         is_too_much_u)
    # find URL of next part of the advert list
    next_p = extract_bytes(response, pre_pattern_n, start_n, end_n,
                           post_pattern_n, c_exclude_n, c_start_n, c_end_n,
                           is_too_much_n)
    # open every advert links via initial_URL and append datasets with adverts
    print(URLs)
    for URL in URLs:
        counter = counter + 1
        URL_string = URL_predial + URL.decode("utf-8") + URL_extension
        append_datasets(URL_string, currency, pre_pattern, start, end,
                        post_pattern, c_exclude, c_start, c_end, is_too_much,
                        pre_p, start_p, end_p, post_p, c_exclude_p, c_start_p,
                        c_end_p, is_too_much_p, pre_t, start_t, end_t, post_t,
                        c_exclude_t, c_start_t, c_end_t, is_too_much_t,
                        phone_images, phone_image_annotations,
                        phone_image_URLs, model_names, average_prices,
                        latest_prices, addition_dates, latest_update_dates,
                        occurence_numbers,
                        exception_URLs,
                        is_new_name,
                        protocol)
    # if there is no further page of the list stop
    if next_p == []:
        break
    # otherwise add preffix or suffix to the URL and change to string
    else:
        next_URL = next_p[0]
        next_URL = URL_predial + next_URL.decode("utf-8") + URL_extension
# saving all lists by serialising to yaml
for key, value in dictionary.items():
    stream = open('' + key + '.yaml', 'w')
    yaml.dump(value, stream)

# print summary
if is_new_name:
    print('Use check_model_names, because new names were added.')
