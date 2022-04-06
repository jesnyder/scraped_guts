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
