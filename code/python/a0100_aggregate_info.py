from bs4 import BeautifulSoup
from datetime import datetime
import json
import lxml
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from serpapi import GoogleSearch
import re
import requests
import time

from a0001_admin import retrieve_path


def aggregate_info(dataset):
    """
    Save a .csv
    """

    # retrieve information
    if 'nsf' in dataset: df = retrieve_nsf()
    elif 'nih' in dataset: df = retrieve_nih()
    elif 'clinical' in dataset: df = retrieve_clinical()
    elif 'patent' in dataset: df = retrieve_patent()
    elif 'pub' in dataset: df = retrieve_pub()


def retrieve_nsf():
    """
    aggregate all files in user provided into a single csv
    """

    print('retrieving nsf')
    df = pd.DataFrame()

    path_term = 'nsf_awards_downloaded'
    path_src = os.path.join(retrieve_path(path_term))
    print('path_src = ' + path_src)
    print('os.listdir(path_src) = ')
    print(os.listdir(path_src))
    for file in os.listdir(path_src):
        print('file = ' + file)



    df = pd.DataFrame()
    return(df)


def retrieve_nih():
    """

    """

    df = pd.DataFrame()
    return(df)


def retrieve_clinical():
    """

    """

    df = pd.DataFrame()
    return(df)


def retrieve_patent():
    """

    """

    df = pd.DataFrame()
    return(df)


def retrieve_pub():
    """

    """

    df = pd.DataFrame()
    return(df)



if __name__ == "__main__":
    main()
