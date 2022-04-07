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
from a0001_admin import retrieve_format
from a0001_admin import retrieve_list
from a0001_admin import retrieve_path
from a0001_admin import write_paths
from find_color import find_color


def untargeted_word_count():
    """

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
        name = 'untargeted_' + dataset_short

    if work_to_do(name):
        work_completed(name, 0)

        df_count = count_untargeted_words(dataset, df)

        file_dst = str(dataset + '_untargeted_count')
        path_dst = os.path.join(retrieve_path(file_dst), dataset  + '.csv')
        df_count.to_csv(path_dst)

        work_completed(name, 1)

    print('completed untargeted_word_count')


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


def count_all_words():
    """
    for all articles types
    count all words
    """

    # list article_names
    article_path = os.path.join(retrieve_path('type_article'))
    df = pd.read_csv(article_path)
    article_names = list(df['name'])

    # list search terms
    article_path = os.path.join(retrieve_path('search_terms'))
    df = pd.read_csv(article_path)
    search_terms = list(df['term'])

    # list compare terms
    compare_terms = os.path.join(retrieve_path('term_compare'))
    for file in os.listdir(compare_terms):

        compare_file_term = file.split('.')
        compare_file_term = compare_file_term[0]
        path = os.path.join(retrieve_path('term_compare'), file)
        print('path = ' + str(path))
        df_compare_terms = pd.read_csv(path)
        compare_term_list = list(df_compare_terms['terms'])

        for name_dataset in article_names:

            print('article = ' + str(name_dataset))

            for term in search_terms:
                print('term = ' + str(term))

                f = os.path.join(retrieve_path(name_dataset + '_aggregate_df'),  name_dataset + '.csv' )
                print('f = ' + str(f))
                df = clean_dataframe(pd.read_csv(f))


                str_all = ''
                for i in range(len(list(df.iloc[:,0]))):

                    for name in df.columns:
                        str_all = str_all + str(df.loc[i,name])
                        str_all = str_all + ' '


                str_all = str_all.lower()
                str_all = str_all.replace('.', ' ')
                str_all = str_all.replace('/', ' ')
                str_all = str_all.replace(':', ' ')
                str_all = str_all.replace(',', ' ')
                str_all = str_all.replace(';', ' ')
                str_all = str_all.replace('(', ' ')
                str_all = str_all.replace(')', ' ')
                str_all = str_all.replace('?', ' ')
                str_all = str_all.replace('!', ' ')
                str_all = str_all.replace('<', ' ')
                str_all = str_all.replace('>', ' ')
                str_all = str_all.replace('\"', ' ')
                str_all = str_all.replace('\'', ' ')
                str_list = str_all.split(' ')
                str_list.sort(reverse=True)

                words, counts, percents = [], [], []
                for word in str_list:

                    if word not in words:

                        # do not save numbers
                        try:
                            if '$' in word: word = word.replace('$', '')
                            if ',' in word: word = word.replace(',', '')
                            word = float(word)
                            continue
                        except:
                            hello = 'hello'

                        try:
                            if '$' in word: word = word.replace('$', '')
                            if ',' in word: word = word.replace(',', '')
                            word = int(word)
                            continue
                        except:
                            hello = 'hello'

                        words.append(word)
                        count = str_list.count(word)
                        counts.append(count)
                        percent = count/len(str_list)
                        percents.append(percent)

                        df_counts = pd.DataFrame()
                        df_counts['words'] = words
                        df_counts['counts'] = counts
                        df_counts['percents'] = percents

                        df_counts = df_counts.sort_values('counts', ascending=False)
                        file_dst = str(name_dataset + '_count_all_words_df')
                        #print('file_dst = ' + str(file_dst))
                        path_dst = os.path.join(retrieve_path(file_dst), 'all_word_count'  + '.csv')
                        df_counts = clean_dataframe(df_counts)
                        df_counts.to_csv(path_dst)

                        #print('df_counts = ')
                        #print(df_counts)
                        print(name_dataset + ' words found = ' + str(len(words)) + '  % complete = ' + str(round(100*sum(counts)/len(str_list),5)))

                        percent_found = 100*sum(counts)/len(str_list)
                        if percent_found > int(retrieve_format('word_count_break_per')):
                            file_dst = str(name_dataset + '_count_all_words_df')
                            #print('file_dst = ' + str(file_dst))
                            path_dst = os.path.join(retrieve_path(file_dst), 'all_word_count_' + str(retrieve_format('word_count_break_per'))  + '.csv')
                            df_counts.to_csv(path_dst)
                            break


if __name__ == "__main__":
    main()
