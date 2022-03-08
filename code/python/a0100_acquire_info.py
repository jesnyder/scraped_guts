from bs4 import BeautifulSoup
import chardet
import datetime
import json
import lxml
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from serpapi import GoogleSearch
import shutil
import random
import re
import requests
import time


from a0001_admin import clean_dataframe
from a0001_admin import name_paths
from a0001_admin import retrieve_format
from a0001_admin import retrieve_list
from a0001_admin import retrieve_path
from a0001_admin import write_paths
from query_patents import query_patents
from scrape_gscholar import scrape_html
from scrape_gscholar import scrape_json
from scrape_gscholar import json_to_dataframe
from scrape_gscholar import article_html
from scrape_gscholar import article_json
from scrape_gscholar import article_df
from scrape_gscholar import html_to_df


def acquire_info():
    """

    """
    print('began acquire_info')

    # List task numbers to complete
    tasks = [0]
    write_paths()
    if  0 in tasks: tasks = np.arange(1, 101, 1)
    if  1 in tasks: acquire_nsf_awards()
    if  2 in tasks: acquire_nih_awards()
    if  3 in tasks: acquire_clinical_trials()
    if  4 in tasks: acquire_patents()
    if  5 in tasks: acquire_gscholar()
    if  6 in tasks: acquire_wikipedia()

    print('completed acquire_info')



def acquire_wikipedia():
    """

    """
    # figure out


# working subprograms

def acquire_gscholar():
    """

    """

    """
    # specify the search
    f = os.path.join(retrieve_path('search_terms'))
    df_search_terms = pd.read_csv(f)
    search_terms = list(df_search_terms['term'])
    """

    name_dataset = 'gscholar'
    for term in retrieve_list('search_terms'):

        # specify the range of number
        num_list = np.arange(10, 2000, 1, dtype=int)
        for num in num_list:

            print('num = ' + str(num))
            error_found = scrape_html(term,num)
            if error_found == True: break

            # collect article html and parse
            error_found = article_html(term)
            if error_found == True: break


def acquire_patents():
    """
    from search terms
    get search results as a dataframe
    save to program_generated
    """

    f = os.path.join(retrieve_path('search_terms'))
    print('f = ' + str(f))
    df_search_terms = pd.read_csv(f)
    search_terms = list(df_search_terms['term'])

    for term in search_terms:
        name_dataset = 'patents'
        #result_limits = [5, 10, 7000, 8000, 9000, 10000, 15000, 20000]
        result_limits = retrieve_format('patent_result_limits')
        query_patents(name_dataset, term, result_limits)


def acquire_nih_awards():
    """
    aggregate and save in program generated
    """
    name_dataset = 'nih_awards'
    format_src(name_dataset)


def acquire_clinical_trials():
    """
    aggregate and save in program generated
    """
    name_dataset = 'clinical_trials'
    format_src(name_dataset)


def acquire_nsf_awards():
    """
    aggregate and save in program generated
    """
    name_dataset = 'nsf_awards'
    format_src(name_dataset)


def format_src(name_dataset):
    """
    dataframe downloaded are not readable
    """

    df_agg = pd.DataFrame()

    folder_name = str(name_dataset + '_downloaded')
    download_src = retrieve_path(folder_name)
    print('download_src = ' + str(download_src))

    for file in os.listdir(download_src):

        df_src = os.path.join(download_src, file)
        print('df_src = ' + str(df_src))


        try:
            df = pd.read_csv(df_src)

        except:
            with open(df_src, 'rb') as file:
                print(chardet.detect(file.read()))
            encodings = ['ISO-8859-1', 'unicode_escape', 'utf-8']
            for encoding in encodings:
                df = pd.read_csv(df_src, encoding=encoding)
                break

        df_agg = df_agg.append(df)


        if name_dataset == 'clinical_trials':
            name = 'NCT Number'

        df_agg = clean_dataframe(df_agg)
        print('df_agg = ')
        print(df_agg)

        if 'Title' in df_agg.columns and'AwardedAmountToDate' in df_agg.columns:
            df_agg = df_agg.sort_values(by = 'AwardedAmountToDate', ascending=False)
            df_agg = df_agg.drop_duplicates(subset = 'Title', keep='first')
            df_agg = clean_dataframe(df_agg)

    df_agg = clean_dataframe(df_agg)

    print('df_agg.columns')
    print(df_agg.columns)

    name_src, name_dst, name_summary, name_unique, plot_unique = name_paths(name_dataset)
    print('name_src = ' + str(name_src))
    file_save = os.path.join(retrieve_path(name_src),  name_dataset + '.csv' )
    df_agg.to_csv(file_save)


if __name__ == "__main__":
    main()
