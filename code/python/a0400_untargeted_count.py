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

    multipliers = [0.05, 0.1, 0.2, 0.4, 1.0]

    print('df = ')
    print(df)

    df_count = pd.DataFrame()


    for multiplier in multipliers:

        str_all = ''
        terms, counts, percents = [], [], []
        percent_complete_threshold = 1
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
                cell_value = str(cell_value)
                str_all = str_all + cell_value

        str_all  = str_all.split(' ')

        all_len = len(str_all)
        for value in str_all:

            if value not in terms:

                terms.append(value)
                count = str_all.count(value)
                counts.append(count)
                percent = round(count/all_len*100,3)
                percents.append(percent)

                str_all.remove(value)

                percent_complete = round(sum(percents),1)
                if percent_complete > percent_complete_threshold:
                    print('name = ' + name + ' multiplier = ' + str(multiplier) + ' percent complete = ' + str(round(sum(percents),3)))
                    percent_complete_threshold = percent_complete_threshold + 3

        df_counts = pd.DataFrame()
        df_counts['term'] = terms
        df_counts['count'] = counts
        df_counts['percent'] = percents

        df_counts = df_counts.sort_values(by = 'count', ascending=False)
        df_counts = clean_dataframe(df_counts)
        file_dst = str(dataset + '_untargeted_count')
        path_dst = os.path.join(retrieve_path(file_dst), dataset  + '.csv')
        df_counts.to_csv(path_dst)
        df_counts = pd.DataFrame()
        #print('saved to: ' + str(path_dst))

        clean_count(dataset, df_counts)      #

    return(df_count)


def clean_count(dataset, df):
    """
    remove stop words
    remove numbers - ints and floats
    remove numbers with $
    save as a shortened df
    """

    df = df[(df['counts'] > 2)]
    df_temp = df

    for term in retrieve_list('stop_words'):

        df_temp =  df_temp[(df_temp['ref_lat'] != term)]

    df_temp = df_temp.sort_values(by = 'count', ascending=False)
    df_temp = clean_dataframe(df_temp)

    file_dst = str(dataset + '_untargeted_count')
    path_dst = os.path.join(retrieve_path(file_dst), dataset + '_short'  + '.csv')
    df_temp.to_csv(path_dst)
    print('short list saved to: ' + str(path_dst))


if __name__ == "__main__":
    main()
