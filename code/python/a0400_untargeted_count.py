from bs4 import BeautifulSoup
import datetime
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


from a0001_admin import clean_dataframe
from a0001_admin import name_paths
from a0001_admin import retrieve_categories
from a0001_admin import retrieve_format
from a0001_admin import retrieve_list
from a0001_admin import retrieve_path
from a0001_admin import write_paths
from a0001_admin import work_completed
from a0001_admin import work_to_do
from a0001_admin import retrieve_terms
from find_color import find_color


def untargeted_word_count(dataset):
    """
    count all the words appearing in the dataset
    """
    print('began untargeted_word_count')

    path_term = str(dataset + '_geolocated')
    print('path_term = ' + path_term)
    path_dst = os.path.join(retrieve_path(path_term))
    print('path_dst = ' + path_dst)
    file_dst = os.path.join(path_dst, dataset + '.csv')
    df = pd.read_csv(file_dst)
    df = clean_dataframe(df)

    if '_' in dataset:
        dataset_split = dataset.split('_')
        dataset_short = dataset_split[0]
        name = 'untargeted_' + dataset_short
    else:
        name = 'untargeted_' + dataset

    if work_to_do(name):

        work_completed(name, 0)

        df_count = count_untargeted_words(dataset, df)
        clean_count(dataset, df_count)

        work_completed(name, 1)

    print('completed untargeted_word_count')


def count_untargeted_words(dataset, df):
    """
    count the words in each dataset
    """

    print('df = ')
    print(df)

    df_count = pd.DataFrame()

    str_all = ''
    for name in df.columns:

        print('name = ' + name)

        if name == 'AwardNumber': continue
        if name == 'address_found': continue
        if name == 'ARRAAmount': continue
        if name == 'AwardedAmountToDate': continue
        if name == 'AwardInstrument': continue
        if name == 'AwardNumber': continue
        if name == 'AwardNumber': continue
        if name == 'Co-PIName(s)': continue
        if name == 'EndDate': continue
        if name == 'LastAmendmentDate': continue
        if name == 'lat_found': continue
        if name == 'lon_found': continue
        if name == 'NSFDirectorate': continue
        if name == 'NSFOrganization': continue
        if name == 'Organization': continue
        if name == 'OrganizationCity': continue
        if name == 'OrganizationPhone': continue
        if name == 'OrganizationStreet': continue
        if name == 'OrganizationState': continue
        if name == 'OrganizationZip': continue
        if name == 'PIEmailAddress': continue
        if name == 'PrincipalInvestigator': continue
        if name == 'Program(s)': continue
        if name == 'ProgramElementCode(s)': continue
        if name == 'ProgramManager': continue
        if name == 'ProgramReferenceCode(s)': continue
        if name == 'ref_values': continue
        if name == 'ref_years': continue
        if name == 'StartDate': continue
        if name == 'State': continue

        for i in range(len(list(df['ref_year']))):

            # list contents of a cell
            str_all = str(df.loc[i,name])
            char_remove = ['.', ':', ';', '"', '/', '\'' , ',', '(', ')', '$', '?', '!', '<', '>']
            for char in char_remove:
                str_all  = str_all .replace(char, '')
            str_all = str_all.lower()
            str_all  = str_all.split(' ')
            assert len(str_all) > 0

            for item in str_all :

                df_count_temp = pd.DataFrame()
                df_count_temp['terms'] = item
                df_count_temp['counts'] = 1

            df_count = df_count.append(df_count_temp)

            for term in list(df_count[terms]):

                df_temp = df_count[(df_count['terms'] == term)]




                print('item = ' + item)

                if item in terms: continue

                terms.append(item)
                count = str_all.count(item)
                counts.append(count)
                percent = round(count/len(str_all)*100,3)
                percents.append(percent)

                df_count = pd.DataFrame()
                df_count['terms'] = terms
                df_count['counts'] = counts
                df_count['percents'] = percents

            print('term = ' + term + ' count = ' + str(count) + ' % = ' + str(percent))
            print('percent found = ' + sum(percents))

            df_count = df_count.sort_values(by = 'percents', ascending=False)

            file_dst = str(dataset + '_untargeted_count')
            path_dst = os.path.join(retrieve_path(file_dst), dataset  + '.csv')
            df_count.to_csv(path_dst)
            print('saved to: ' + str(path_dst))




    return(df_count)


def clean_count(dataset, df):
    """
    remove stop words
    remove numbers - ints and floats
    remove numbers with $
    save as a shortened df
    """


    df = df[(df['counts'] > 2)]

    terms = list(df_count['terms'])
    counts = list(df_count['counts'])
    percents = list(df_count['percents'])

    terms_short = []
    for term in terms:
        if term in retrieve_list('stop_words'): continue
        terms_short.append(term)

    counts, percents = [], []
    for term in terms_short:

        df_temp = df[(df['terms'] == term)]
        count = df.loc[0,'counts']
        percent = df.loc[0,'percents']
        counts.append(count)
        percents.append(percent)

    df = pd.DataFrame()
    df['terms'] = terms_short
    df['counts'] = counts
    df['percents'] = percents

    file_dst = str(dataset + '_untargeted_count')
    path_dst = os.path.join(retrieve_path(file_dst), dataset + '_short'  + '.csv')
    df.to_csv(path_dst)
    print('saved to: ' + str(path_dst))


if __name__ == "__main__":
    main()
