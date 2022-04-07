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


def targeted_word_count(dataset):
    """

    """

    path_term = str(dataset + '_geolocated')
    print('path_term = ' + path_term)
    path_dst = os.path.join(retrieve_path(path_term))
    print('path_dst = ' + path_dst)
    file_dst = os.path.join(path_dst, dataset + '.csv')
    df = pd.read_csv(file_dst)
    df = clean_dataframe(df)


    if 'nsf' in dataset:
        name = 'targetted_nsf'
        if work_to_do(name):
            work_completed(name, 0)
            df = count_targeted_words(dataset, df)
            work_completed(name, 1)

    print('completed targeted_word_count')


def plot_annual_count(dataset):
    """

    """
    # for each article type
    for name_dataset in retrieve_list('type_article'):

        #if name_dataset != 'nih_awards': continue

        for file in os.listdir(retrieve_path('term_compare')):

            path = os.path.join(retrieve_path('term_compare'), file)
            term_list = retrieve_list(path)
            print('term_list = ')
            print(term_list)

            # save dataframe with percent
            file_src = str(name_dataset + '_compare_terms_annual_count_df')
            compare_file_term = file.split('.')
            compare_file_term = compare_file_term[0]
            compare_file_term = str(compare_file_term + '_percent')
            path_src = os.path.join(retrieve_path(file_src), compare_file_term  + '.csv')
            df = clean_dataframe(pd.read_csv(path_src))


            df =  df[(df['cdf_total'] > 0)]
            df = clean_dataframe(df)
            #print('df = ')
            #print(df)

            # begin figure
            plt.close('all')
            figure, axes = plt.subplots()
            plot_row, plot_col, plot_num = 3, 1, 0
            plt.figure(figsize=(plot_col*retrieve_format('fig_wid'), plot_row*retrieve_format('fig_hei')))
            plt.rc('font', size=retrieve_format('plot_font_size'))

            plot_num = plot_num +1
            plt.subplot(plot_row, plot_col, plot_num)
            for term in term_list:
                color_index = term_list.index(term)
                term_cdf = str(term + '_cdf')
                xx = list(df['years'])
                yy = list(df[term_cdf])
                colorMarker, colorEdge, colorTransparency = find_color(color_index)
                label_term = str(sum(yy)) + ' ' + term
                #plt.scatter(xx,yy, color=colorMarker, edgecolor=colorEdge, alpha=colorTransparency, label=label_term)
                plt.plot(xx, yy, color=colorMarker, linestyle='dashed', marker = 'o', ms =retrieve_format('plot_marker_size'), mec = colorEdge, mfc = colorMarker, alpha=colorTransparency, label = label_term)

            plt.title(name_dataset + ' Annual ' + str(int(sum(list(df['annual_total'])))))
            plt.xlabel('year')
            plt.ylabel('count')
            plt.yscale('log')
            plt.legend(bbox_to_anchor=(1, 0.8), loc='upper left')



            plot_num = plot_num +1
            plt.subplot(plot_row, plot_col, plot_num)
            for term in term_list:
                color_index = term_list.index(term)
                #if '|' in term: term = (term.split('|'))[0]
                term_cdf = str(term + '_cdf')
                xx = list(df['years'])
                yy = list(df[term_cdf])
                colorMarker, colorEdge, colorTransparency = find_color(color_index)
                try:
                    label_term = str(yy[-1]) + ' ' + term
                except:
                    label_term = str(0) + ' ' + term
                #plt.scatter(xx,yy, color=colorMarker, edgecolor=colorEdge, alpha=colorTransparency, label=label_term)
                plt.plot(xx, yy, color=colorMarker, linestyle='dashed', marker = 'o', ms =retrieve_format('plot_marker_size'), mec = colorEdge, mfc = colorMarker, alpha=colorTransparency, label = label_term)

            plt.title(name_dataset + ' Cumulative ' + str(int(sum(list(df['annual_total'])))))
            plt.xlabel('year')
            plt.ylabel(term_cdf)
            plt.yscale('log')
            plt.legend(bbox_to_anchor=(1, -0.8), loc='upper left')


            plot_num = plot_num +1
            plt.subplot(plot_row, plot_col, plot_num)
            for term in term_list:
                color_index = term_list.index(term)
                #if '|' in term: term = (term.split('|'))[0]
                term_per = str(term + '_percent')
                xx = list(df['years'])
                yy = list(df[term_per])

                offsets = [0] * len(list(xx))

                if color_index > 0:
                    offsets = []
                    for k in range(len(list(df['years']))):
                        offset = 0
                        for j in range(color_index):
                            #term = term_list[j]
                            offset = offset + df.loc[k][term_list[j] + '_percent']
                        offsets.append(offset)

                assert len(offsets) == len(xx)
                assert len(offsets) == len(yy)
                try:
                    label_term = str(round(100*yy[-1],2)) + '% ' + term
                except:
                    label_term = str(0) + '% ' + term
                colorMarker, colorEdge, colorTransparency = find_color(color_index)
                plt.bar(xx, yy, width=1.0, bottom=offsets, align='center', color=colorMarker,label = label_term)



            plt.title(name_dataset + ' Percent ' + str(int(sum(list(df['annual_total'])))))
            plt.xlabel('year')
            plt.ylabel(term_per)
            # plt.yscale('log')
            #plt.legend(bbox_to_anchor=(0.2, -0.2), loc='upper left')
            plt.legend(bbox_to_anchor=(0.2, 0), loc='upper left')

            plot_count_annual = str(name_dataset + '_compare_terms_plot')
            plot_dst = os.path.join(retrieve_path(plot_count_annual), compare_file_term + '.png')
            plt.savefig(plot_dst, dpi = retrieve_format('plot_dpi'), edgecolor = 'w')
            print('saved plot: ' + plot_dst)
            plt.close('all')


def per_annual_count_targeted():
    """

    """

    # for each article type
    for name_dataset in retrieve_list('type_article'):
        print('article = ' + str(name_dataset))

        #if name_dataset != 'nih_awards': continue

        # all search terms together
        # for each term to compare
        for file in os.listdir(retrieve_path('term_compare')):

            path = os.path.join(retrieve_path('term_compare'), file)
            term_list = retrieve_list(path)
            #print('term_list = ')
            #print(term_list)

            # retrieve dataframe with counts
            compare_file_term = file.split('.')
            compare_file_term = compare_file_term[0]
            file_src = str(name_dataset + '_compare_terms_annual_count_df')
            path_src = os.path.join(retrieve_path(file_src), compare_file_term  + '.csv')
            df = clean_dataframe(pd.read_csv(path_src))

            # add a total column
            df['annual_total'] = [0]* len(list(df['years']))
            for i in range(len(list(df['years']))):

                df_annual = df[(df['years'] == df.loc[i,'years'])]


                count_year = 0
                for name in df_annual.columns:
                    if name in term_list:
                        count_year = count_year + list(df_annual[name])[0]
                df.loc[i,'annual_total'] = count_year
                #print('count_year = ' + str(count_year))


            for term in term_list:

                #if '|' in term: term = (term.split('|'))[0]
                print('term = ' + term)

                term_per = str(term + '_percent')
                df[term_per] = [0]* len(list(df['years']))

                for i in range(len(list(df['years']))):

                    if df.loc[i,'annual_total'] == 0: continue

                    percent = df.loc[i,term]
                    total = df.loc[i,'annual_total']
                    df.loc[i,term_per] = percent/total

            # add a cdf column
            df['cdf_total'] = [0]* len(list(df['years']))
            for term in term_list:

                #if '|' in term: term = (term.split('|'))[0]
                print('term = ' + term)
                term_cdf = str(term + '_cdf')
                df[term_cdf] = [0]* len(list(df['years']))

                for i in range(len(list(df['years']))):

                    df_annual = df[(df['years'] <= df.loc[i,'years'])]
                    df.loc[i,term_cdf] = sum(df_annual[term])
                    df.loc[i,'cdf_total'] = df.loc[i,'cdf_total'] + df.loc[i,term_cdf]

            #print('df = ')
            #print(df)

            # save dataframe with percent
            file_src = str(name_dataset + '_compare_terms_annual_count_df')
            compare_file_term = str(compare_file_term + '_percent')
            path_src = os.path.join(retrieve_path(file_src), compare_file_term  + '.csv')
            df.to_csv(path_src)


def annual_count_targeted():
    """

    """

    # list search terms
    search_terms = retrieve_list('search_terms')

    # list compare terms
    compare_terms = os.path.join(retrieve_path('term_compare'))

    for file in os.listdir(compare_terms):

        path = os.path.join(retrieve_path('term_compare'), file)
        term_list = retrieve_list(path)
        print('term_list = ')
        print(term_list)

        for name_dataset in retrieve_list('type_article'):

            print('article = ' + str(name_dataset))

            #if name_dataset != 'nih_awards': continue

            file_dst = str(name_dataset + '_compare_terms_df')
            compare_file_term = file.split('.')
            compare_file_term = str(compare_file_term[0])
            path_dst = os.path.join(retrieve_path(file_dst), compare_file_term  + '.csv')
            df = clean_dataframe(pd.read_csv(path_dst))

            #print('df = ')
            #print(df)

            #print('df.columns = ')
            #print(df.columns)

            if 'ref_year' not in df.columns:
                df = add_ref_year(df, name_dataset)

            year_min = int((min(list(df['ref_year']))))
            year_max = int((max(list(df['ref_year']))))
            years = np.arange(year_min, year_max, 1)

            df_yearly_count = pd.DataFrame()
            df_yearly_count['years'] = years


            #for term in search_terms:
            for compare_term in term_list:

                """
                if '|' in compare_term:
                    compare_term_list = compare_term.split('|')
                    compare_term = compare_term_list[0]
                """

                #print('compare_term = ' + str(compare_term))
                counts, values = [], []
                for year in years:

                    df_annual = df[(df['ref_year'] == year)]
                    target_list = list(df_annual[compare_term])
                    count = sum(list(df_annual[compare_term]))
                    counts.append(count)

                    df_annual_term = df_annual[(df_annual[compare_term] > 0)]
                    ref_list = list(df_annual_term['ref_value'])
                    value = sum(ref_list)
                    values.append(value)

                df_yearly_count[compare_term] = counts
                df_yearly_count[str(compare_term + '_value')] = values


            compare_file_term = file.split('.')
            compare_file_term = compare_file_term[0]
            file_dst = str(name_dataset + '_compare_terms_annual_count_df')
            path_dst = retrieve_path(file_dst)
            #print('path_dst = ' + str(path_dst))
            path_dst = os.path.join(path_dst, compare_file_term  + '.csv')
            #print('path_dst = ' + str(path_dst))
            df_yearly_count.to_csv(path_dst)


def count_targeted_words(dataset, df):
    """
    for all articles types
    count all words
    """

    for category in retrieve_categories():

        print('category = ' + category)

        for i in range(len(list(df['ref_year']))):

            str_all = ''
            for name in df.columns:
                str_all = str_all + str(df.loc[i,name])
                str_all = str_all + ' '
                str_all = str_all.lower()

            category_terms = retrieve_terms(category)
            for term in category_terms:

                print('term = ' + term)
                df[term] = [0] * len(list(df['ref_year']))

                if '|' in term:
                    compare_term_list = term.split('|')
                else:
                    compare_term_list = [term]

                if 'both' == term:
                    if df.loc[i,category_terms[0]] == 1:
                        if df.loc[i,category_terms[1]] == 1:
                            df.loc[i,term] = 1
                            df.loc[i,category_terms[0]] = 0
                            df.loc[i,category_terms[1]] = 0

                else:
                    for target_term in compare_term_list:
                        target_term = target_term.lower()
                        if str(target_term) in str(str_all):
                            df.loc[i,term] = 1
                            continue

            file_dst = str(name_dataset + '_targeted_count')
            path_dst = os.path.join(retrieve_path(file_dst), category  + '.csv')
            df.to_csv(path_dst)


if __name__ == "__main__":
    main()
