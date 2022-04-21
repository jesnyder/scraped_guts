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
    elif 'clinical' in dataset:
        df = acquire_clinical(dataset)
        list_clinical_trials(dataset)
    elif 'patent' in dataset: df = acquire_patent(dataset)
    elif 'pub' in dataset: df = acquire_pub(dataset)

    # format and co-register fields of datasets
    df = coregister(dataset)

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

        # remove out of status trials and resave over acquired file
        status_drop = ['Withdrawn', 'Terminated', 'Suspended']
        status_drop.append('Temporarily not available')
        status_drop.append('Unknown status')
        for status in status_drop:
            df =  df[(df['Status'] != status)]

        df = clean_dataframe(df)
        path_term = str(dataset + '_src_query')
        path_dst = os.path.join(retrieve_path(path_term))
        file_dst = os.path.join(path_dst, dataset + '.csv')
        df.to_csv(file_dst)

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


def coregister(dataset):
    """
    add reference value for year and value
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


    if 'nsf' in dataset: df = coregister_nsf(dataset, df)
    if 'nih' in dataset: df = coregister_nih(dataset, df)
    if 'clinical' in dataset: df = coregister_clinical(dataset, df)
    else: return(df)

    return(df)


def coregister_clinical(dataset, df):
    """
    add year and value as enrollment
    """

    print('df = ')
    print(df)

    name = 'coregister_clinical'
    if work_to_do(name):
        work_completed(name, 0)

        years = []
        for date in list(df['Start Date']):
            print('date = ')
            print(date)
            try:
                date = date.replace('"', '')
                date_split = date.split(' ')
                year = date_split[-1]
            except:
                year = 0
            years.append(year)

        values = []
        for item in list(df['Enrollment']):
            item = float(item)
            values.append(item)

        df['ref_year'] = years
        df['ref_values'] = values
        path_term = str(dataset + '_coregistered')
        path_dst = os.path.join(retrieve_path(path_term))
        file_dst = os.path.join(path_dst, dataset + '.csv')
        df.to_csv(file_dst)
        work_completed(name, 1)

        return(df)


def coregister_nih(dataset, df):
    """

    """

    print('df = ')
    print(df)

    name = 'coregister_nih'
    if work_to_do(name):
        work_completed(name, 0)

        years = []
        for date in list(df['Fiscal Year']):
            year = date
            years.append(year)

        values = []
        for item in list(df['Direct Cost IC']):
            item = float(item)
            values.append(item)

        df['ref_year'] = years
        df['ref_values'] = values
        path_term = str(dataset + '_coregistered')
        path_dst = os.path.join(retrieve_path(path_term))
        file_dst = os.path.join(path_dst, dataset + '.csv')
        df.to_csv(file_dst)
        work_completed(name, 1)

        return(df)


def coregister_nsf(dataset, df):
    """

    """

    print('df = ')
    print(df)

    name = 'coregister_nsf'
    if work_to_do(name):
        work_completed(name, 0)

        years = []
        for date in list(df['StartDate']):
            date_split = date.split('/')
            year = date_split[-1]
            years.append(year)

        values = []
        for item in list(df['AwardedAmountToDate']):
            item = item.replace('$', '')
            item = item.replace('"', '')
            item = item.replace(',', '')
            item = float(item)
            values.append(item)

        df['ref_year'] = years
        df['ref_values'] = values
        path_term = str(dataset + '_coregistered')
        path_dst = os.path.join(retrieve_path(path_term))
        file_dst = os.path.join(path_dst, dataset + '.csv')
        df.to_csv(file_dst)
        work_completed(name, 1)

        return(df)


def geolocate(dataset):
    """

    """

    path_term = str(dataset + '_coregistered')
    path_dst = os.path.join(retrieve_path(path_term))
    file_dst = os.path.join(path_dst, dataset + '.csv')
    df = pd.read_csv(file_dst)
    df = clean_dataframe(df)

    if 'nsf' in dataset:
        name = 'geolocate_nsf'
        if work_to_do(name):
            work_completed(name, 0)
            df = geolocate_nsf(dataset, df)
            work_completed(name, 1)

    elif 'nih' in dataset:
        name = 'geolocate_nih'
        if work_to_do(name):
            work_completed(name, 0)
            df = geolocate_nih(dataset, df)
            work_completed(name, 1)

    elif 'clinical' in dataset:
        name = 'geolocate_clinical'
        if work_to_do(name):
            work_completed(name, 0)
            df = geolocate_clinical(dataset, df)
            work_completed(name, 1)

    else:
        df = pd.DataFrame()
        return(df)

    path_term = str(dataset + '_geolocated')
    print('path_term = ' + str(path_term))
    path_dst = os.path.join(retrieve_path(path_term))
    print('path_dst = ' + str(path_dst))
    file_dst = os.path.join(path_dst, dataset + '.csv')
    print('file_dst = ' + str(file_dst))
    df = clean_dataframe(df)
    df.to_csv(file_dst)

    return(df)


def geolocate_clinical(dataset, df):
    """
    look up lat and lon for nsf award address
    """

    #print('df.columns = ')
    #print(df.columns)

    address_found, lat_found, lon_found = [], [], []
    for i in range(len(list(df['Sponsor/Collaborators']))):

        percent_complete = round(i/len(list(df['Sponsor/Collaborators']))*100,2)
        left_i = len(list(df['Sponsor/Collaborators'])) - i
        print('percent_complete = ' + str(percent_complete) + ' i = ' + str(i) + ' left: ' + str(left_i))

        name = df.loc[i, 'Sponsor/Collaborators']
        name = name.replace('"', '')
        names = name.split('|')

        location = df.loc[i, 'Locations']
        location = name.replace('"', '')
        if '|' in location:
            locations = location.split('|')
        else:
            locations = [location]

        addresses = []
        for name in names: addresses.append(name)
        for location in locations: addresses.append(location)

        print('addresses = ')
        print(addresses)

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
        name = name.replace('"', '')
        name = name.replace('/', '')
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


def list_clinical_trials(dataset):
    """

    """
    path_term = str(dataset + '_src_query')
    path_dst = os.path.join(retrieve_path(path_term))
    file_dst = os.path.join(path_dst, dataset + '.csv')
    df = pd.read_csv(file_dst)
    df = clean_dataframe(df)

    print('df.columns = ')
    print(df.columns)

    organizations = []
    target_col_names = ['Sponsor/Collaborators', 'Locations']

    for col_name in target_col_names:

        for i in range(len(df[col_name])):
            org = df.loc[i, col_name]
            org = str(org)

            if '"' in org: org = org.replace('"', '')

            #print('org = ' + str(org))

            if '|' in org:
                orgs = org.split('|')
            else:
                orgs = [org]

            for org in orgs:
                if org not in organizations:
                    organizations.append(org)

    urls = []
    for org in organizations:

        org_urls = []
        for col_name in target_col_names:

            for item in list(df[col_name]):

                try:
                    item = float(item)
                    #print('item = ' + str(item))
                    continue
                except:
                    item = item
                    #print('item = ' + str(item))

                if str(org) not in str(item): continue

                df_temp =  df[(df[col_name] == item)]
                url_temps = list(df_temp['URL'])

                for url in url_temps:
                    if url not in org_urls:
                        #print('url = ')
                        #print(url)
                        org_urls.append(url)


        str_org_urls=" , ".join(str(elem) for elem in org_urls)
        #print('org = ' + str(org))
        #assert len(str_org_urls) > 0

        extra_commas = 20 - len(org_urls)
        for i in range(extra_commas):
            str_org_urls = str_org_urls + ' , '

        urls.append(str_org_urls)


    df = pd.DataFrame()
    df['organizations'] = organizations
    df['url'] = urls
    df = df.sort_values('organizations', ascending=True)
    df = clean_dataframe(df)
    df.to_csv(retrieve_path('clinical_orgs'))


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
