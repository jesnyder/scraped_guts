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
    if str(dataset).contains('nsf'):
        df = retrieve_nsf()

    if str(dataset).contains('nih'):
        df = retrieve_nih()

    if str(dataset).contains('clinical'):
        df = retrieve_clinical()

    if str(dataset).contains('patent'):
        df = retrieve_patent()

    if str(dataset).contains('pub'):
        df = retrieve_pub()


def retrieve_nsf():
    """
    aggregate all files in user provided into a single csv
    """

    df = pd.DataFrame()

    path_term = 'nsf_awards_downloaded'
    for file in os.listdir(os.path.join(retrieve_path(path_term))):
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
