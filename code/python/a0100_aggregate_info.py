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
import re
import requests
import time

from a0001_admin import retrieve_path
from a0001_admin import write_paths


def aggregate_info(dataset):
    """
    Save a .csv
    """

    # write paths
    write_paths()

    # retrieve information
    if 'nsf' in dataset: df = acquire_nsf()
    elif 'nih' in dataset: df = acquire_nih()
    elif 'clinical' in dataset: df = acquire_clinical()
    elif 'patent' in dataset: df = acquire_patent()
    elif 'pub' in dataset: df = acquire_pub()


def acquire_nsf():
    """
    aggregate all files in user provided into a single csv
    """

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

    path_term = str(name_dataset + '_src_query')
    path_dst = os.path.join(retrieve_path(path_term))
    file_dst = os.path.join(path_term, dataset + '.csv')
    df.to_csv(file_dst)

    return(df)


def acquire_nih():
    """

    """

    df = pd.DataFrame()
    return(df)


def acquire_clinical():
    """

    """

    df = pd.DataFrame()
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



if __name__ == "__main__":
    main()
