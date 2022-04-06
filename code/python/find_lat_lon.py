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
from a0001_admin import retrieve_path
from a0001_admin import write_paths
from a0001_admin import work_completed
from a0001_admin import work_to_do


def findLatLong(addresses):
    """
    check an internal list for address
    else look up on street maps
    """

    #print('geolocating.')

    for address in addresses:

        print('address = ' + str(address))

        lat, lon = read_address(address)
        if lat != None and lon != None:
            return(address, lat, lon)

        url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json'
        response = requests.get(url).json()
        #print(response)

        try:
            lat = response[0]["lat"]
            lon = response[0]["lon"]

        except:
            lat = None
            lon = None

        print('lat/lon = ' + str(lat) + ' / ' + str(lon))

        if lat != None and lon != None:
            record_address(address, lat, lon)
            return(address, lat, lon)


def read_address(address):
    """
    cumulative list of all addresses found
    """

    try:
        path_term = 'address_list'
        file_dst = os.path.join(retrieve_path(path_term))
        df = pd.read_csv(file_dst)
        df = clean_dataframe(df)
    except:
        return(None, None)

    address_found = list(df['address'])
    if address in address_found:
        df_temp = df[(df['address'] == address)]
        lat = list(df_temp['lat'])
        lat = lat[0]
        lon = list(df_temp['lon'])
        lon = lon[0]

    else:
        lat, lon = None, None

    return(lat, lon)


def record_address(address, lat, lon):
    """
    cumulative list of all addresses found
    """

    try:
        path_term = 'address_list'
        file_dst = os.path.join(retrieve_path(path_term))
        df = pd.read_csv(file_dst)
        df = clean_dataframe(df)
    except:
        df = pd.DataFrame()

    df_temp = pd.DataFrame()
    df_temp['address'] = [address]
    df_temp['lat'] = [lat]
    df_temp['lon'] = [lon]

    df = df.append(df_temp)
    df = clean_dataframe(df)
    df.to_csv(file_dst)
