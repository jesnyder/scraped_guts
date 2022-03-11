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
from a0001_admin import work_completed
from a0001_admin import work_to_do

from query_patents import query_patents
from scrape_gscholar import scrape_gscholar
from scrape_gscholar import scrape_gscholar_article
from scrape_gscholar import json_to_dataframe
#from scrape_gscholar import scrape_html
#from scrape_gscholar import scrape_json
#from scrape_gscholar import json_to_dataframe
#from scrape_gscholar import article_html
#from scrape_gscholar import article_json
#from scrape_gscholar import article_df
#from scrape_gscholar import html_to_df


def acquire_info():
    """

    """

    work_completed('acquire_info', 0)
    if work_to_do('acquire_nsf_awards') == True: acquire_nsf_awards()
    if work_to_do('acquire_nih_awards') == True: acquire_nih_awards()
    if work_to_do('acquire_clinical_trials') == True: acquire_clinical_trials()
    if work_to_do('acquire_gscholar') == True: acquire_gscholar()
    if work_to_do('acquire_patents') == True: acquire_patents()
    if work_to_do('acquire_wikipedia') == True: acquire_wikipedia()
    work_completed('acquire_info', 1)

def acquire_wikipedia():
    """

    """
    # figure out


# working subprograms

def acquire_gscholar():
    """

    """

    work_completed('acquire_gscholar', 0)

    if work_to_do('scrape_gscholar') == True:
        work_completed('scrape_gscholar', 0)
        scrape_gscholar()
        work_completed('scrape_gscholar', 1)

    if work_to_do('acquire_gscholar_json_to_dataframe') == True:
        work_completed('acquire_gscholar_json_to_dataframe', 0)
        json_to_dataframe()
        work_completed('acquire_gscholar_json_to_dataframe', 1)

    if work_to_do('acquire_gscholar_article') == True:
        work_completed('acquire_gscholar_article', 0)
        scrape_gscholar_article()
        work_completed('acquire_gscholar_article', 1)

    work_completed('acquire_gscholar', 1)


def acquire_patents():
    """
    from search terms
    get search results as a dataframe
    save to program_generated
    """

    work_completed('acquire_patents', 0)

    f = os.path.join(retrieve_path('search_terms'))
    print('f = ' + str(f))
    df_search_terms = pd.read_csv(f)
    search_terms = list(df_search_terms['term'])

    for term in search_terms:
        name_dataset = 'patents'
        #result_limits = [5, 10, 7000, 8000, 9000, 10000, 15000, 20000]
        result_limits = retrieve_format('patent_result_limits')
        query_patents(name_dataset, term, result_limits)

    work_completed('acquire_patents', 1)


def acquire_nih_awards():
    """
    aggregate and save in program generated
    """
    work_completed('acquire_nih_awards', 0)
    name_dataset = 'nih_awards'
    format_src(name_dataset)
    work_completed('acquire_nih_awards', 1)


def acquire_clinical_trials():
    """
    aggregate and save in program generated
    """
    work_completed('acquire_clinical_trials', 0)
    name_dataset = 'clinical_trials'
    format_src(name_dataset)
    work_completed('acquire_clinical_trials', 1)


def acquire_nsf_awards():
    """
    aggregate and save in program generated
    """
    work_completed('acquire_nsf_awards', 0)
    name_dataset = 'nsf_awards'
    format_src(name_dataset)
    work_completed('acquire_nsf_awards', 1)


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
