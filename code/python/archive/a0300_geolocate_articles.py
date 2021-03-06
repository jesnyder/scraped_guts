from bs4 import BeautifulSoup
import datetime
import json
import lxml
import matplotlib.pyplot as plt
import numpy as np
import os
from os.path import exists
import pandas as pd
from serpapi import GoogleSearch
import re
import requests
import time
import urllib.parse

from a0001_admin import clean_dataframe
from a0001_admin import name_paths
from a0001_admin import retrieve_categories
from a0001_admin import retrieve_datetime
from a0001_admin import retrieve_format
from a0001_admin import retrieve_list
from a0001_admin import retrieve_path
from a0001_admin import write_paths
from a0001_admin import work_completed
from a0001_admin import work_to_do

from a0200_aggregate_info  import list_unique_values
from a0200_aggregate_info  import plot_unique_values
from a0200_aggregate_info  import cross_plot_unique
from scrape_gscholar import aggregate_articles
from find_color import find_color
from gif_maker import build_gif


def geolocate_articles():
    """

    """

    work_completed('geolocate_articles', 0)

    geolocate_dataset()
    #if  work_to_do('list_gscholar_addresses'): list_gscholar_addresses()
    #if  work_to_do('find_address'): find_address()
    #if  work_to_do('list_address'): list_address()
    work_completed('geolocate_articles', 1)


def geolocate_dataset():
    """

    """
    for name_dataset in retrieve_list('name_dataset'):

        name_src, name_dst, name_summary, name_unique, plot_unique = name_paths(name_dataset)
        work_completed('find_address_' + name_dataset, 0)

        try:
            f = os.path.join(retrieve_path(name_dst), name_dataset + '_meta' + '.csv')
            df = clean_dataframe(pd.read_csv(f), header=1)
        except:
            f = os.path.join(retrieve_path(name_dst),  name_dataset + '.csv' )
            df = clean_dataframe(pd.read_csv(f))

        for name in ['address', 'lat', 'lon']:
            df[name] = [None] * len(list(df.iloc[:,0]))

        for i in range(len(list(df.iloc[:,0]))):

            print(name_dataset + ' ')
            i=i-1
            df_temp = df.iloc[i,:]

            if 'gscholar' in name_dataset:
                aggregate_articles()
                address, lat, lon = geolocate_gscholar(df_temp)

            df.loc[i, 'lat'] = [lat]
            df.loc[i, 'lon'] = [lon]
            df.loc[i, 'address'] = [address]


        f = os.path.join(retrieve_path(name_dst),  name_dataset + '_geolocated' + '.csv' )
        df.to_csv(f)
    wait(5)


def geolocate_gscholar(df):
    """

    """
    print('df = ')
    print(df)

    print('df.columns = ')
    print(df.columns)

    lat, lon = findLatLong(address)
    if lat != None:
        list_addresses(address, lat, lon)
        return(address, lat, lon)





def list_gscholar_addresses():
    """

    """
    df_new = pd.DataFrame()

    name_dataset = 'gscholar'
    names = name_paths(name_dataset)
    df_dst_name = os.path.join(retrieve_path(names[1]), name_dataset + '_meta' + '.csv')
    print('df_dst_name = ' + df_dst_name)
    df = pd.read_csv(df_dst_name, header=1)
    df = clean_dataframe(df)

    print('df = ')
    print(df)

    print('df.columns')
    print(df.columns)

    for url in list(df['url']):

        df_temp = df[(df['title_link'] == url)]
        addresses = []

        for name in df_temp.columns:

            name = name.lower()
            names_of_interest = ['author', 'institution', 'affiliation', 'contributor']
            for name_of_interest in names_of_interest:

                # check if any column names partially match column names
                if name_of_interest in name:

                    # add contents to list to check for addresses
                    try:
                        contents = list(df_temp[name])
                        for content in contents:
                            print('cotents = ')
                            print(contents)
                            addresses.append(content)
                    except:
                        print('not found')

        address_found, lat_found, lon_found = [], [], []
        try:
            for address in addresses:
                lat, lon = findLatLong(address)
                if lat != None:
                    list_addresses(address, lat, lon)
                    address_found.append(address)
                    lat_found.append(lat)
                    lon_found.append(lon)
        except:
            print('not found')

        df_temp['address_found'] = [address_found]
        df_temp['lat_found'] = [address_found]
        df_temp['lon_found'] = [address_found]

        df_new = df_new.append(df_temp)
        #df_new = clean_dataframe(df_new)
        df_dst_name = os.path.join(retrieve_path(names[1]), name_dataset + '_meta' + '_geotagged'+ '.csv')
        df_new.to_csv(df_dst_name)
        print('df_new = ')
        print(df_new)


def list_addresses(address, lat, lon):
    """

    """
    df_temp = pd.DataFrame()
    df_temp['address'] = [address]
    df_temp['lat'] = [lat]
    df_temp['lon'] = [lon]

    df = pd.read_csv(os.path.join(retrieve_path('list_address')))

    if address in list(df['address']):
        df_temp = df[(df['address'] == address)]
        count = len(list(df_temp['address'])) + 1
    else:
        count = 1

    df_temp['count'] = [count]
    df = clean_dataframe(df)
    df = df.append(df_temp)
    df = df.sort_values('count', ascending=False)
    df = df.drop_duplicates(subset='address')
    df = clean_dataframe(df)

    print('df = ')
    print(df)

    df.to_csv(os.path.join(retrieve_path('list_address')))


# completed programs

def build_clinical_address(df):
    """
    find address and lat/lon for each trial
    """
    #print('df = ')
    #print(df)

    locations = df['Locations']
    sponsors = df['Sponsor/Collaborators']

    address = ''
    address = address + str(sponsors) + ' ; '
    address = address + str(locations)
    address_complete = address
    print('address_complete =   ')
    print(address_complete)

    sponsor_location = []
    try:
        locations_split = locations.split(',')
        for item in locations_split:
            sponsor_location.append(item)
    except:
        hello = 'hello'
    try:
        sponsors_split = sponsors.split('|')
        for item in sponsors_split:
            sponsor_location.append(item)
    except:
        hello = 'hello'


    # hard code address changes
    if 'Hadassah Medical Organization' in sponsor_location:
        target = 'Jerusalem, Israel'
        sponsor_location.append(target)
    elif 'CAR-T (Shanghai) Biotechnology Co., Ltd.' in sponsor_location:
        target = 'Shanghai, China'
        sponsor_location.append(target)
    elif 'Peking University People\'s Hospital' in sponsor_location:
        target = 'Beijing, China'
        sponsor_location.append(target)
    elif 'The First People\'s Hospital of Yunnan' in sponsor_location:
        target = 'Yunnan, China'
        sponsor_location.append(target)
    elif 'Institute of Hematology & Blood Diseases Hospital' in sponsor_location:
        target = 'San Francisco, CA'
        sponsor_location.append(target)
    elif 'Direct Biologics, LLC' in sponsor_location:
        target = 'Austin, TX'
        sponsor_location.append(target)
    elif 'Sclnow Biotechnology Co., Ltd.' in sponsor_location:
        target = '231 S Whisman Rd, Mountain View, CA'
        sponsor_location.append(target)
    elif 'Shandong Qilu Stem Cells Engineering Co., Ltd.' in sponsor_location:
        target = 'South San Francisco, CA'
        sponsor_location.append(target)
    elif 'Vinmec Research Institute of Stem Cell and Gene Technology' in sponsor_location:
        target = 'Times City, Vietnam'
        sponsor_location.append(target)
    elif 'Affiliated Hospital of Jiangsu University' in sponsor_location:
        target = 'Zhenjiang, Jiangsu, China'
        sponsor_location.append(target)
    elif 'Masonic Cancer Center, University of Minnesota' in sponsor_location:
        target = 'University of Minnesota'
        sponsor_location.append(target)
    elif 'Pharmicell Co., Ltd.' in sponsor_location:
        target = 'San Francisco, CA'
        sponsor_location.append(target)
    elif 'Mesoblast, Inc.' in sponsor_location:
        target = '505 5th Ave, New York, NY 10017'
        sponsor_location.append(target)
    elif 'Institute of Biophysics and Cell Engineering of National Academy of Sciences of Belarus' in sponsor_location:
        target = 'Minsk, Belarus'
        sponsor_location.append(target)
    elif 'Ministry of Public Health, Republic of Belarus' in sponsor_location:
        target = 'Minsk, Belarus'
        sponsor_location.append(target)
    elif 'Celltex Therapeutics Corporation' in sponsor_location:
        target = 'Houston, TX 77057'
        sponsor_location.append(target)
    elif 'Celltex Therapeutics Corporation' in sponsor_location:
        target = 'Houston, TX 77057'
        sponsor_location.append(target)
    elif 'PT. Prodia Stem Cell Indonesia' in sponsor_location:
        target = 'Daerah Khusus Ibukota Jakarta, Indonesia'
        sponsor_location.append(target)
    elif 'South China Research Center for Stem Cell and Regenerative Medicine' in sponsor_location:
        target = 'Guangzhou, China'
        sponsor_location.append(target)
    elif 'Regeneris Medical' in sponsor_location:
        target = 'North Attleboro, MA 02760'
        sponsor_location.append(target)
    elif 'Ontario Institute for Regenerative Medicine (OIRM)' in sponsor_location:
        target = '661 University Avenue, Toronto, Ontario, CANADA'
        sponsor_location.append(target)
    elif 'The First Affiliated Hospital of Dalian Medical University' in sponsor_location:
        target = '222 Zhongshan Rd, Xigang District, Dalian, China'
        sponsor_location.append(target)
    elif 'Sorrento Therapeutics, Inc.' in sponsor_location:
        target = '4955 Directors Place, San Diego, CA 92121'
        sponsor_location.append(target)
    elif 'Department of Neurology, University Hospital Motol, Prague, Czech Republic' in sponsor_location:
        target = 'Prague, Czech Republic'
        sponsor_location.append(target)
    elif 'Xinhua Hospital, Shanghai Jiao Tong University School of Medicine' in sponsor_location:
        target = '1555 Kongjiang Rd, Yangpu District, Shanghai, China'
        sponsor_location.append(target)
    elif 'Nature Cell Co. Ltd.' in sponsor_location:
        target = 'Seoul, South Korea '
        sponsor_location.append(target)
    elif 'PLA General Hospital, Beijing' in sponsor_location:
        target = 'Beijing'
        sponsor_location.append(target)
    elif 'Papworth Hospital NHS Foundation Trust' in sponsor_location:
        target = 'Cambridge, United Kingdom'
        sponsor_location.append(target)
    elif 'Cell Therapy Catapult' in sponsor_location:
        target = 'London, United Kingdom'
        sponsor_location.append(target)
    elif 'Royal Free Hospital NHS Foundation Trust' in sponsor_location:
        target = 'London, United Kingdom'
        sponsor_location.append(target)
    elif 'Stem Cells Arabia' in sponsor_location:
        target = 'Ibn Khaldoun St. 40, Amman 11183, Jordan'
        sponsor_location.append(target)
    elif 'Mesoblast, Ltd.' in sponsor_location:
        target = '505 5th Ave, New York, NY 10017'
        sponsor_location.append(target)
    elif 'Fuzhou General Hospital' in sponsor_location:
        target = 'Gulou District, Fuzhou, Fuzhou, China'
        sponsor_location.append(target)
    elif 'The Oxford Dental College, Hospital and Research Center, Bangalore, India' in sponsor_location:
        target = 'Bangalore, India'
        sponsor_location.append(target)
    elif 'The Oxford Dental College, Hospital and Research Center, Bangalore, India' in sponsor_location:
        target = 'Bangalore, India'
        sponsor_location.append(target)
    elif 'Aegle Therapeutics' in sponsor_location:
        target = '400 TradeCenter, Woburn, MA 01801'
        sponsor_location.append(target)
    elif 'Anterogen Co., Ltd.' in sponsor_location:
        target = 'Seoul, South Korea'
        sponsor_location.append(target)
    elif 'Department of Spine Surgery, University Hospital Motol, Prague, Czech Republilc' in sponsor_location:
        target = 'Prague, Czech Republic'
        sponsor_location.append(target)
    elif 'Longeveron Inc.' in sponsor_location:
        target = 'MIAMI, FL 33136'
        sponsor_location.append(target)
    elif 'Medipost Co Ltd.' in sponsor_location:
        target = 'Seoul, South Korea'
        sponsor_location.append(target)
    elif 'Chinese PLA General Hospital' in sponsor_location:
        target = '4th Ring Road, Beijing, China'
        sponsor_location.append(target)
    elif 'Baylx Inc.' in sponsor_location:
        target = 'Irvine, CA 92618'
        sponsor_location.append(target)
    elif 'BioRestorative Therapies' in sponsor_location:
        target = 'Melville, NY 11747'
        sponsor_location.append(target)
    elif 'Celyad Oncology SA' in sponsor_location:
        target = 'New York, NY 10004'
        sponsor_location.append(target)
    elif 'Vitro Biopharma Inc.' in sponsor_location:
        target = 'Golden, CO 80403'
        sponsor_location.append(target)
    elif 'Shenzhen Geno-Immune Medical Institute' in sponsor_location:
        target = 'Shenzhen'
        sponsor_location.append(target)
    elif 'Bright Cell, Inc.' in sponsor_location:
        target = 'Prince George, BC, Canada'
        sponsor_location.append(target)
    elif 'Paean Biotechnology Inc.' in sponsor_location:
        target = 'Seoul, Korea'
        sponsor_location.append(target)
    elif 'National Cancer Institute (NCI)' in sponsor_location:
        target = 'Washington, DC'
        sponsor_location.append(target)
    elif 'Global Stem Cell Center, Baghdad' in sponsor_location:
        target = 'Baghdad'
        sponsor_location.append(target)
    elif 'Rejuva Medical Aesthetics' in sponsor_location:
        target = 'Los Angeles, CA 90025'
        sponsor_location.append(target)
    elif 'Institute of Anatomy TU Dresden' in sponsor_location:
        target = 'Dresden, Germany'
        sponsor_location.append(target)
    elif 'University of Sao Paulo General Hospital' in sponsor_location:
        target = 'Sao Paulo'
        sponsor_location.append(target)
    elif 'The Nordic Network For Clinical Islet Transplantation' in sponsor_location:
        target = 'Torbj??rn'
        sponsor_location.append(target)
    elif 'Taiwan Mitochondrion Applied Technology Co., Ltd.' in sponsor_location:
        target = 'Taiwan'
        sponsor_location.append(target)


    print('sponsor_location = ')
    print(sponsor_location)

    addresses = []
    address = sponsor_location[0]
    addresses.append(address)

    for i in range(len(sponsor_location)):
        address = sponsor_location[i]
        addresses.append(address)

    if len(sponsor_location) > 1:
        address = sponsor_location[0] + ', '
        address = address + sponsor_location[1]
        addresses.append(address)

        address = sponsor_location[1]
        addresses.append(address)

    if len(sponsor_location) > 2:
        address = sponsor_location[0] + ', '
        address = address + sponsor_location[1] + ', '
        address = address + sponsor_location[2]
        addresses.append(address)

        address = sponsor_location[1] + ', '
        address = address + sponsor_location[2]
        addresses.append(address)

        address = sponsor_location[0] + ', '
        address = address + sponsor_location[2]
        addresses.append(address)

        address = sponsor_location[2]
        addresses.append(address)

    if len(sponsor_location) > 3:
        address = sponsor_location[0] + ', '
        address = address + sponsor_location[1] + ', '
        address = address + sponsor_location[2] + ', '
        address = address + sponsor_location[3]
        addresses.append(address)

        address = sponsor_location[1] + ', '
        address = address + sponsor_location[2] + ', '
        address = address + sponsor_location[3]
        addresses.append(address)

        address = sponsor_location[-2] + ', '
        address = address + sponsor_location[-1]
        addresses.append(address)

        address = sponsor_location[3]
        addresses.append(address)

    for address in addresses:
        print('address_complete =   ')
        print(address_complete)
        print('address =   ')
        print(address)
        lat, lon = findLatLong(address)
        if lat != None: return(address_complete, address, lat, lon)

    lat, lon = lookup_address(address_complete, address)
    if lat != None: return(address_complete, address, lat, lon)

    missing_address(name_dataset, address_complete, addresses)
    return(address_complete, address, 0, 0)


def build_nih_address(df):
    """
    identify organization name and lat/lon
    """
    address = df['Organization Name']

    lat = df['Latitude']
    lon = df['Longitude']

    try:
        lat = float(lat)
    except:
        lat = 0

    try:
        lon = float(lon)
    except:
        lon = 0


    """
    print('address = ' + str(address))
    print('lat = ' + str(lat))
    print('lon = ' + str(lon))
    """

    return(address, address, lat, lon)


def build_nsf_address(df):
    """
    build the address and retrieve lat and lon
    for each entry of the grant
    """
    address = ''
    assignee_name = df['Organization']
    street = df['OrganizationStreet']
    city = df['OrganizationCity']
    state = df['OrganizationState']
    country = 'US'

    address = ''
    address = address + str(assignee_name) + ' |  '
    address = address + str(street) + ', '
    address = address + str(city) + ', '
    address = address + str(state) + ', '
    address = address + str(country)
    address_complete = address
    print('address_complete =   ')
    print(address_complete)

    # format elements for OpenStreets search
    try:
        if '(' in city: city = city.replace('(','')
        if ')' in city: city = city.replace(')','')
    except:
        hello = 'hello'

    try:
        addresses = []

        address = assignee_name
        addresses.append(address)

        address = str(street) + ', '
        address = address + str(city) + ', '
        address = address + str(state) + ', '
        address = address + str(country)
        addresses.append(address)

        address = str(city) + ', '
        address = address + str(state) + ', '
        address = address + str(country)
        addresses.append(address)

        address = str(city) + ', '
        address = address + str(state)
        addresses.append(address)

        address = str(city) + ', '
        address = address + str(country)
        addresses.append(address)

        address = str(city)
        addresses.append(address)

        address = str(country)
        addresses.append(address)

        for address in addresses:
            print('address_complete =   ')
            print(address_complete)
            print('address =   ')
            print(address)
            lat, lon = findLatLong(address)
            if lat != None: return(address_complete, address, lat, lon)

        lat = 0
        lon = 0
        return(address_complete, address, lat, lon)

    except:
        lat = 0
        lon = 0
        return(address_complete, address, lat, lon)


def build_gscholar_address(df):

    print('df = ')
    print(df)
    #df = clean_dataframe(df)

    name_dataset = 'gscholar'
    names = name_paths(name_dataset)
    df_dst_name = os.path.join(retrieve_path(names[1]), name_dataset + '_meta' + '.csv')
    df = pd.read_csv(df_dst_name)
    df = clean_dataframe(df)

    print('df = ')
    print(df)

    for url in list(df['url']):

        df_temp = df[(df['title_link'] == url)]
        address = []

        for name in df.columns:

            name = name.lower()
            if 'author' in name or 'institution' in name or 'affiliation' in name or 'contributor' in name:

                content = list(df_temp[name])

        for address in addresses:
            lat, lon = findLatLong(address)
            if lat != None:
                list_addresses(address, lat, lon)
                return(address_complete, address, lat, lon)


    address_complete, address, lat, lon = None, None, None, None
    return(address_complete, address, lat, lon)


def build_patent_address(df):
    """
    build address and look up lat/lon
    """
    #print('df = ')
    #print(df)

    # identify fields
    assignee_name = df['assignee_name']
    assignee_loc = df['assignee_loc']
    name = df['applicant_name']
    city = df['applicant_city']
    state = df['applicant_state']
    country = df['applicant_country']

    # format retrieved info
    try:
        if '(' in city: city = city.replace('(','')
        if ')' in city: city = city.replace(')','')
    except:
        hello = 'hello'
    try:
        if ',' in assignee_name: assignee_name = assignee_name.split(',')[0]
        if '.' in assignee_name: assignee_name = assignee_name.split('.')[0]
    except:
        hello = 'hello'

    # write all address info into a string
    address = ''
    address = address + str(assignee_name) + ', '
    address = address + str(assignee_loc) + ' | '
    address = address + str(name) + ', '
    address = address + str(city) + ', '
    address = address + str(state) + ', '
    address = address + str(country)
    address_complete = address
    print('address_complete =   ')
    print(address_complete)

    # create a list of possible addresses
    addresses = []

    address = str(assignee_name)
    addresses.append(address)

    address = str(assignee_loc)
    addresses.append(address)

    address = str(name)
    addresses.append(address)

    address = str(name) + ', '
    address = address + str(city) + ', '
    address = address + str(state) + ', '
    address = address + str(country)
    addresses.append(address)

    address = str(city) + ', '
    address = address + str(state) + ', '
    address = address + str(country)
    addresses.append(address)

    address = str(city) + ', '
    address = address + str(country)
    addresses.append(address)

    try:
        city_split = city.split(',')
        address = str(city_split[0]) + ', '
        address = address + str(country)
        addresses.append(address)

        address = str(city_split[1]) + ', '
        address = address + str(country)
        addresses.append(address)

        address = str(city)
        addresses.append(address)

        address = str(city_split[0])
        addresses.append(address)

        address = str(city_split[1])
        addresses.append(address)
    except:
        hello = 'hello'

    address = str(country)
    addresses.append(address)

    for address in addresses:
        print('address_complete =   ')
        print(address_complete)
        print('address =   ')
        print(address)
        lat, lon = findLatLong(address)
        if lat != None:
            list_addresses(address, lat, lon)
            return(address_complete, address, lat, lon)


    try:
        names = []
        states = []
        countries = []
        for i in range(len(state)-1):
            if i%2 == 0: continue
            state_i = str(state)[i-1:i+1]
            country_i = str(country)[i-1:i+1]
            states.append(state_i)
            countries.append(country_i)

        address = ''
        address = address + str(states[0]) + ', '
        address = address + str(countries[0])
        print('address = ' + str(address))
        lat, lon = findLatLong(address)
        if lat != None: return(address_complete, address, lat, lon)
    except:
        hello = 'hello'


    try:
        names = []
        countries = []
        for i in range(len(country)-1):
            if i%2 == 0: continue
            country_i = str(country)[i-1:i+1]
            countries.append(country_i)

        address = ''
        address = address + str(countries[0])
        print('address = ' + str(address))
        lat, lon = findLatLong(address)
        if lat != None: return(address_complete, address, lat, lon)
    except:
        hello = 'hello'

    missing_address(name_dataset, address_complete, address)
    return(address_complete, address, 0, 0)


def find_address():
    """
    for all found aticles
    list unique institutions
    """

    #for name_dataset in ['clinical_trials', 'nih_awards', 'nsf_awards', 'patents']:
    for name_dataset in retrieve_list('name_dataset'):

        name_src, name_dst, name_summary, name_unique, plot_unique = name_paths(name_dataset)
        work_completed('find_address_' + name_dataset, 0)

        f = os.path.join(retrieve_path(name_dst),  name_dataset + '.csv' )
        df_ref = clean_dataframe(pd.read_csv(f))

        df_ref['ref_complete_address'] = [None] * len(list(df_ref.iloc[:,0]))
        df_ref['ref_address'] = [None] * len(list(df_ref.iloc[:,0]))
        df_ref['ref_lat'] = [None] * len(list(df_ref.iloc[:,0]))
        df_ref['ref_lon'] = [None] * len(list(df_ref.iloc[:,0]))

        for i in range(len(list(df_ref.iloc[:,0]))):

            i= i

            complete_num = round(100*i/len(list(df_ref.iloc[:,0])),2)
            print(name_dataset + ' % complete: ' + str(complete_num) + '    i = ' + str(i))
            df_ref_row = df_ref.iloc[i,:]


            if 'nih_awards' in name_dataset:
                address_complete, address, lat, lon = build_nih_address(df_ref_row)

            if 'nsf_award' in name_dataset:
                address_complete, address, lat, lon = build_nsf_address(df_ref_row)

            if 'clinical' in name_dataset:
                address_complete, address, lat, lon = build_clinical_address(df_ref_row)

            if 'patent' in name_dataset:
                address_complete, address, lat, lon = build_patent_address(df_ref_row)

            if 'gscholar' in name_dataset:
                address_complete, address, lat, lon = build_gscholar_address(df_ref_row)

            print('lat/lon = ' + str(lat) + ' /  ' + str(lon))

            df_ref.loc[i, 'ref_complete_address'] = address_complete
            df_ref.loc[i, 'ref_address'] = address
            df_ref.loc[i, 'ref_lat'] = float(lat)
            df_ref.loc[i, 'ref_lon'] = float(lon)

        f = os.path.join(retrieve_path(name_dataset + '_aggregate_df'),  name_dataset + '_with_address' + '.csv' )
        df_ref = clean_dataframe(df_ref)
        df_ref.to_csv(f)

        list_unique_values(name_dataset, df_ref)
        plot_unique_values(name_dataset)
        cross_plot_unique(name_dataset, df_ref)

        work_completed('find_address_' + name_dataset, 1)


def findLatLong(address):
    """

    """

    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json'
    #print('url = ')
    #print(url)
    response = requests.get(url).json()
    print(response)

    #print('searching for long/lat url = ')
    #print(url)

    try:
        #print(response[0]["lat"])
        #print(response[0]["lon"])
        lat = response[0]["lat"]
        lon = response[0]["lon"]

    except:
        lat = None
        lon = None

    print('lat/lon = ' + str(lat) + ' / ' + str(lon))

    return(lat, lon)


def lookup_address(address_complete, addresses):
    """

    """
    df = pd.read_csv(retrieve_path('lookup_address'), sep='|')
    df = clean_dataframe(df)

    for name in list(df['name']):

        for address in addresses:

            name_edit = name.replace(' ', '')
            address_edit = address.replace(' ', '')
            if name_edit == address_edit:

                index = list(df['name']).index(name)
                findable_address = df.loc[index,'findable_address']
                lat, lon = findLatLong(findable_address)
                return(lat,lon)

    return(None, None)


def missing_address(name_dataset, address_complete, address):
    """
    save address if not found
    """
    df_temp = pd.DataFrame()
    df_temp['name_dataset'] = [name_dataset]
    df_temp['address_complete'] = [address_complete]
    df_temp['address'] = [address]
    df_temp['date_time'] = [retrieve_datetime()]

    try:
        df = pd.read_csv(retrieve_path('address_not_found'))
        df = clean_dataframe(df)
    except:
        df = pd.DataFrame()

    df = df.append(df_temp)
    df = df.drop_duplicates()
    df = clean_dataframe(df)
    df.to_csv(retrieve_path('address_not_found'))


if __name__ == "__main__":
    main()
