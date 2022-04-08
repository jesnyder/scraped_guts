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

        work_completed(name, 1)

    print('completed untargeted_word_count')


def count_untargeted_words(dataset, df):
    """
    count the words in each dataset
    """

    print('df = ')
    print(df)

    for i in range(len(list(df['ref_year']))):

        str_all = ''
        for name in df.columns:
            print('name = ' + name)
            print('df.loc[i,name] = ')
            print(df.loc[i,name])

            print('str(df.loc[i,name]) = ')
            print(str(df.loc[i,name]))

            str_all = str_all + str(df.loc[i,name])
            str_all = str_all + ' '
            str_all = str_all.lower()

    str = str_all.lower()

    char_remove = ['.', ':', ';', '"', '/', '\'' , ',', '(', ')', '$', '?', '!', '<', '>']
    for char in char_remove:
        str = str.replace(char, '')

    str = str.split(' ')

    terms, counts, percents = [], [], []
    df_count = pd.DataFrame()

    for item in str:

        if item in terms: continue

        terms.append(item)
        count = str.count(item)
        counts.append(count)
        percent = round(count/len(str)*100,3)
        percents.append(percent)

        df_count = pd.DataFrame()
        df_count['terms'] = terms
        df_count['counts'] = counts
        df_count['percents'] = percents

        df_count = df_count.sort_values(by = 'percents', ascending=False)

        file_dst = str(dataset + '_untargeted_count')
        path_dst = os.path.join(retrieve_path(file_dst), dataset  + '.csv')
        df_count.to_csv(path_dst)

    return(df_count)


def clean_count():
    """
    remove stop words
    remove numbers - ints and floats
    remove numbers with $
    save as a shortened df
    """

    for name_dataset in retrieve_list('type_article'):

        print('article = ' + str(name_dataset))
        file_dst = str(name_dataset + '_count_all_words_df')

        # read in the saved dataframe, either complete or in progress
        try:
            try:
                path_dst = os.path.join(retrieve_path(file_dst), 'all_word_count_' + str(retrieve_format('word_count_break_per'))  + '.csv')
            except:
                path_dst = os.path.join(retrieve_path(file_dst), 'all_word_count'  + '.csv')
            df = clean_dataframe(pd.read_csv(path_dst))
        except:
            break

        #print('path_dst = ' + str(path_dst))
        #df = clean_dataframe(pd.read_csv(path_dst))
        df_short = df[(df['counts'] > 2)]

        rows_to_drop = []
        for stop_word in retrieve_list('stop_words'):
            df_short = df_short[(df_short['words'] != stop_word)]

        df_short = df_short.drop(rows_to_drop)
        for i in range(len(list(df_short['words']))):

            word = df.loc[i,'words']

            if isinstance(word, int):
                rows_to_drop.append(i)

            if isinstance(word, float):
                rows_to_drop.append(i)

            try:
                try:
                    word = float(word)
                    rows_to_drop.append(i)
                except:
                    word = int(word)
                    rows_to_drop.append(i)
            except:
                hello = 'hello'

            try:
                try:
                    word = word.remove('$')
                    word = float(word)
                    rows_to_drop.append(i)
                except:
                    word = word.remove('$')
                    word = int(word)
                    rows_to_drop.append(i)
            except:
                hello = 'hello'

        print('rows_to_drop = ')
        print(rows_to_drop)

        df_short = df_short.drop(rows_to_drop)

        df_short = clean_dataframe(df_short)
        file_dst = str(name_dataset + '_count_all_words_df')
        path_dst = os.path.join(retrieve_path(file_dst), 'short_word_count'  + '.csv')
        print('path_dst = ' + str(path_dst))

        print('before saving df_short = ')
        print(df_short)

        df_short.to_csv(path_dst)



if __name__ == "__main__":
    main()
