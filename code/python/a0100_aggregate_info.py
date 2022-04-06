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


def list_unique(dataset):
    """
    save csv of all unique values with counts
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

        df_summary['Item Count'] = len(list(df[col_name]))

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
    df.to_csv(file_dst)


if __name__ == "__main__":
    main()
