from bs4 import BeautifulSoup
import chardet
from datetime import datetime
import json
import lxml
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from serpapi import GoogleSearch
import statistics
import re
import requests
import time

from a0001_admin import clean_dataframe
from a0001_admin import retrieve_path
from a0001_admin import write_paths
from a0001_admin import work_completed
from a0001_admin import work_to_do
from find_lat_lon import findLatLong


def aggregate_info(dataset):
    """
    Save a .csv
    """

    # write paths
    write_paths()

    # acquire information
    if 'nsf' in dataset: df = acquire_nsf(dataset)
    elif 'nih' in dataset: df = acquire_nih(dataset)
    elif 'clinical' in dataset: df = acquire_clinical(dataset)
    elif 'patent' in dataset: df = acquire_patent()
    elif 'pub' in dataset: df = acquire_pub()

    # aggregate information

    # coregister

    # geolocate
    df = geolocate(dataset)

    # summarize
    df = summarize(dataset)

    # list unique
    df = list_unique(dataset)


def acquire_clinical(dataset):
    """
    from downloaded clinical data, aggregate
    """

    name = 'acquire_clinical'
    if work_to_do(name):
        work_completed(name, 0)
        df = acquire_downloaded(dataset)
        work_completed(name, 1)

    else:
        path_term = str(dataset + '_src_query')
        path_dst = os.path.join(retrieve_path(path_term))
        file_dst = os.path.join(path_dst, dataset + '.csv')
        df = pd.read_csv(file_dst)

    print('Clinical df = ')
    print(df)
    return(df)


def acquire_downloaded(dataset):
    """
    aggregate all files downloaded and saved in user provided
    """

    df = pd.DataFrame()

    path_term = dataset + '_downloaded'
    path_src = os.path.join(retrieve_path(path_term))
    for file in os.listdir(path_src):
        file_src = os.path.join(path_src, file)

        print('file_src = ' + str(file_src))

        try:
            df_src = pd.read_csv(file_src)

        except:
            with open(file_src, 'rb') as file:
                print(chardet.detect(file.read()))
            encodings = ['ISO-8859-1', 'unicode_escape', 'utf-8']
            for encoding in encodings:
                df_src = pd.read_csv(file_src, encoding=encoding)
                break

        df = df.append(df_src)
        df = df.drop_duplicates()

        path_term = str(dataset + '_src_query')
        path_dst = os.path.join(retrieve_path(path_term))
        file_dst = os.path.join(path_dst, dataset + '.csv')
        print('file_dst  = ' + file_dst )
        df.to_csv(file_dst)

    return(df)


def acquire_nsf(dataset):
    """
    aggregate all files in user provided into a single csv
    """

    name = 'acquire_nsf'
    if work_to_do(name):
        work_completed(name, 0)
        df = acquire_downloaded(dataset)
        work_completed(name, 1)

    else:
        path_term = str(dataset + '_src_query')
        path_dst = os.path.join(retrieve_path(path_term))
        file_dst = os.path.join(path_dst, dataset + '.csv')
        df = pd.read_csv(file_dst)

    print('NSF df = ')
    print(df)
    return(df)


def acquire_nih(dataset):
    """
    from downloaded nih data, aggregate
    """

    name = 'acquire_nih'
    if work_to_do(name):
        work_completed(name, 0)
        df = acquire_downloaded(dataset)
        work_completed(name, 1)

    else:
        path_term = str(dataset + '_src_query')
        path_dst = os.path.join(retrieve_path(path_term))
        file_dst = os.path.join(path_dst, dataset + '.csv')
        df = pd.read_csv(file_dst)

    print('NIH df = ')
    print(df)
    return(df)


def acquire_patent():
    """

    """

    df = pd.DataFrame()
    return(df)


def acquire_pub():
    """

    """

    df = pd.DataFrame()
    return(df)


def geolocate(dataset):
    """

    """
    try:
        path_term = str(dataset + '_src_query')
        path_dst = os.path.join(retrieve_path(path_term))
        file_dst = os.path.join(path_dst, dataset + '.csv')
        df = pd.read_csv(file_dst)
        df = clean_dataframe(df)

    except:
        df = pd.DataFrame()
        return(df)

    if 'nsf' in dataset:
        name = 'geolocate_nsf'
        if work_to_do(name):
            work_completed(name, 0)
            df = geolocate_nsf(dataset, df)
            work_completed(name, 1)

    if 'nih' in dataset:
        name = 'geolocate_nih'
        if work_to_do(name):
            work_completed(name, 0)
            df = geolocate_nih(dataset, df)
            work_completed(name, 1)

    if 'clinical' in dataset:
        name = 'geolocate_clinical'
        if work_to_do(name):
            work_completed(name, 0)
            df = geolocate_nih(dataset, df)
            work_completed(name, 1)


    #elif 'clinical' in dataset: df = geolocate_clinical(dataset, df)
    #elif 'patent' in dataset: df = geolocate_patent(dataset, df)
    #elif 'pub' in dataset: df = geolocate_pub(dataset, df)
    else: df = pd.DataFrame()

    path_term = str(dataset + '_geolocated')
    path_dst = os.path.join(retrieve_path(path_term))
    file_dst = os.path.join(path_dst, dataset + '.csv')
    df = pd.read_csv(file_dst)
    df = clean_dataframe(df)

    if 'address_found' not in df.columns: return(df)

    df_geolocated = pd.DataFrame()
    df_geolocated['address_found'] = list(df['address_found'])
    df_geolocated['lat_found'] = list(df['lat_found'])
    df_geolocated['lon_found'] = list(df['lon_found'])

    path_dst = os.path.join(retrieve_path('list_address'))
    file_dst = os.path.join(path_dst, dataset + '.csv')
    df_geolocated = pd.read_csv(file_dst)

    return(df)


def geolocate_clinical(dataset, df):
    """
    look up lat and lon for nsf award address
    """


    for i in range(len(list(df['SponsorCollaborators']))):

        name = df.loc[i, 'SponsorCollaborators']
        name = name.replace('"', '')
        names = name.split('|')

        location = df.loc[i, 'Locations']
        location = name.replace('"', '')
        locations = locations.split('|')

        addresses = []
        for name in names: addresses.append(name)
        for location in locations: addresses.append(location)

        address, lat, lon = findLatLong(addresses)

        address_found.append(address)
        lat_found.append(lat)
        lon_found.append(lon)


    df['address_found'] = address_found
    df['lat_found'] = lat_found
    df['lon_found'] = lon_found
    return(df)


def geolocate_nih(dataset, df):
    """
    look up lat and lon for nsf award address
    """

    """
    for i in range(len(list(df['Organization City']))):

        name = df.loc[i, 'Organization Name']
        name = name.replace('"', '')
        city = df.loc[i, 'Organization City']
        state = df.loc[i, 'Organization State']
        country = df.loc[i, 'Organization Country']
        zip = df.loc[i, 'Organization Zip']

        addresses = []
        addresses.append(name + ' , ' + city + ' , ' country)
        addresses.append(name + ' , ' + city + ' , ' + state + ' , ' + zip)
        addresses.append(city + ' , ' + state + ' , ' country)

        address_found, lat_found, lon_found = [], [], []
        for address in addresses:
            lat, lon = findLatLong(address)
            if lat != None:
                address_found.append(address)
                lat_found.append(lat)
                lon_found.append(lon)
    """

    df['address_found'] = list(df['Organization Name'])
    df['lat_found'] = list(df['Latitude'])
    df['lon_found'] = list(df['Longitude'])

    return(df)


def geolocate_nsf(dataset, df):
    """
    look up lat and lon for nsf award address
    """

    address_found, lat_found, lon_found = [], [], []
    for i in range(len(list(df['OrganizationStreet']))):

        progress = round(i/len(list(df['OrganizationStreet']))*100,2)
        left = len(list(df['OrganizationStreet'])) - i
        print('Progress: ' + str(progress) + ' % '  + str(left) + ' left')

        name = str(df.loc[i, 'Organization'])
        name = name.replace('.', '')
        street = str(df.loc[i, 'OrganizationStreet'])
        city = str(df.loc[i, 'OrganizationCity'])
        state = str(df.loc[i, 'OrganizationState'])
        zip = str(df.loc[i, 'OrganizationZip'])

        print('name = ' + name)
        print('street = ' + street)
        print('city = ' + city)
        print('state = ' + state)
        print('zip = ' + zip)

        addresses = []
        addresses.append(name)
        addresses.append(street + ' , ' + city + ' , ' + state)
        addresses.append(street + ' , ' + city + ' , ' + state + ' , ' + str(zip))
        addresses.append(street + ' , ' + city + ' , ' + state)
        addresses.append(city + ' , ' + state)
        addresses.append(zip)

        #print('addresses = ')
        #print(addresses)

        address, lat, lon = findLatLong(addresses)

        address_found.append(address)
        lat_found.append(lat)
        lon_found.append(lon)


    df['address_found'] = address_found
    df['lat_found'] = lat_found
    df['lon_found'] = lon_found
    return(df)


def list_unique(dataset):
    """
    save csv of all unique values with counts
    """

    try:
        try:

            path_term = str(dataset + '_geolocated')
            path_dst = os.path.join(retrieve_path(path_term))
            file_dst = os.path.join(path_dst, dataset + '.csv')
            df = pd.read_csv(file_dst)
            df = clean_dataframe(df)

        except:
            path_term = str(dataset + '_src_query')
            path_dst = os.path.join(retrieve_path(path_term))
            file_dst = os.path.join(path_dst, dataset + '.csv')
            df = pd.read_csv(file_dst)
            df = clean_dataframe(df)

    except:
        df = pd.DataFrame()
        return(df)

    for col_name in df.columns:

        values =  list(df[col_name])
        df_counts = pd.value_counts(np.array(values))

        path_term = str(dataset + '_unique_df')
        path_dst = os.path.join(retrieve_path(path_term))

        if '/' in col_name:
            col_name = col_name.replace('/', '')

        file_dst = os.path.join(path_dst, col_name + '.csv')
        df_counts.to_csv(file_dst)


def summarize(dataset):
    """
    save a summary as a .csv
    """
    try:
        try:

            path_term = str(dataset + '_geolocated')
            path_dst = os.path.join(retrieve_path(path_term))
            file_dst = os.path.join(path_dst, dataset + '.csv')
            df = pd.read_csv(file_dst)
            df = clean_dataframe(df)

        except:
            path_term = str(dataset + '_src_query')
            path_dst = os.path.join(retrieve_path(path_term))
            file_dst = os.path.join(path_dst, dataset + '.csv')
            df = pd.read_csv(file_dst)
            df = clean_dataframe(df)

    except:
        df = pd.DataFrame()
        return(df)

    df_summary = pd.DataFrame()

    for col_name in df.columns:

        df_summary['Item Count'] = [len(list(df[col_name]))]

        if '/' in col_name:
            col_name_new = col_name.replace('/', '')

        try:
            target = sum(list(df[col_name]))
            df_summary[col_name_new + '_sum'] = [target]
        except:
            hello = 'hello'

        try:
            target = stastistics.mode(list(df[col_name]))
            df_summary[col_name_new + '_mode'] = [target]
        except:
            hello = 'hello'

        try:
            target = stastistics.mean(list(df[col_name]))
            df_summary[col_name_new + '_mean'] = [target]
        except:
            hello = 'hello'

        try:
            target = stastistics.mean(list(df[col_name]))
            df_summary[col_name_new + '_median'] = [target]
        except:
            hello = 'hello'


    df_summary = df_summary.T
    path_term = str(dataset + '_sum')
    path_dst = os.path.join(retrieve_path(path_term))
    file_dst = os.path.join(path_dst, dataset + '.csv')
    df_summary.to_csv(file_dst)


if __name__ == "__main__":
    main()
