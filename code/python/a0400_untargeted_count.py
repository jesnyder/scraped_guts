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

        df_count = word_count(dataset, df)
        clean_count(dataset, df_count)

        work_completed(name, 1)

    print('completed untargeted_word_count')



def word_count(dataset, df):
    """
    count the words in each dataset
    """

    multipliers = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    print('df = ')
    print(df)

    df_count = pd.DataFrame()

    str_all = ''
    for multiplier in multipliers:

        for name in df.columns:

            col_skip_list = retrieve_list('untargeted_columns_excluded')
            if name in col_skip_list: continue

            print('name = ' + name + ' multiplier = ' + str(multiplier))

            range_multiplier = int(len(list(df['ref_year']))*multiplier)
            for i in range(range_multiplier):

                # list contents of a cell
                cell_value = str(df.loc[i,name])

                char_remove = ['.', ':', ';', '"', '/', '\'' , ',', '(', ')', '$', '?', '!', '<', '>']
                for char in char_remove:
                    cell_value  = cell_value.replace(char, '')
                cell_value = cell_value.lower()
                
                try:
                    cell_value = str(cell_value)
                except:
                    print('cell_value = ')
                    print(cell_value)

                str_all = str_all + cell_value

        str_all  = str_all.split(' ')

        df_counts = pd.value_counts(np.array(str_all))

        print('df_counts = ')
        print(df_counts)
        #print('df_counts.columns = ')
        #print(df_counts.columns)
        #df_count = df_count.sort_values(by = '0', ascending=False)
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
