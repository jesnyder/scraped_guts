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


    print('df = ')
    print(df)
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
