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
    count if each article in each dataset includes a target term
    make a plot
    """

    path_term = str(dataset + '_geolocated')
    print('path_term = ' + path_term)
    path_dst = os.path.join(retrieve_path(path_term))
    print('path_dst = ' + path_dst)
    file_dst = os.path.join(path_dst, dataset + '.csv')
    df = pd.read_csv(file_dst)
    df = clean_dataframe(df)

    # count each terms set for each category

    if '_' in dataset:
        dataset_split = dataset.split('_')
        dataset_short = dataset_split[0]
        name = 'targeted_count_' + dataset_short
    else:
        name = 'targeted_count_' + dataset

    if work_to_do(name):
        work_completed(name, 0)
        count_targeted_words(dataset, df)
        work_completed(name, 1)


    # plot after counting

    if '_' in dataset:
        dataset_split = dataset.split('_')
        dataset_short = dataset_split[0]
        name = 'targeted_plot_' + dataset_short
    else:
        name = 'targeted_plot_' + dataset

    if work_to_do(name):

        work_completed(name, 0)
        annual_count_targeted(dataset)
        plot_annual_count(dataset)
        work_completed(name, 1)

    print('completed targeted_word_count')


def plot_annual_count(dataset):
    """

    """
    for category in retrieve_categories():

        path_src = str(dataset + '_targeted_count')
        file_src = os.path.join(retrieve_path(path_src), category + '_cdf'  + '.csv')
        df = pd.read_csv(file_src)
        df = clean_dataframe(df)

        category_terms = retrieve_terms(category)
        for term in category_terms:

            #df =  df[(df['cdf_total'] > 0)]
            df = clean_dataframe(df)


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

            path_dst = str(dataset + '_targeted_count')
            file_dst = os.path.join(retrieve_path(path_dst), category + '_cdf'  + '.csv')
            plt.savefig(file_dst, dpi = retrieve_format('plot_dpi'), edgecolor = 'w')
            print('saved plot: ' + plot_dst)
            plt.close('all')


def annual_count_targeted(dataset):
    """

    """

    for category in retrieve_categories():

        file_dst = str(dataset + '_targeted_count')
        path_dst = os.path.join(retrieve_path(file_dst), category  + '.csv')
        df = pd.read_csv(path_dst)

        print('df.columns = ')
        print(df.columns)

        year_min = int((min(list(df['ref_year']))))
        year_max = int((max(list(df['ref_year']))))
        years = np.arange(year_min, year_max, 1)

        df_yearly_count = pd.DataFrame()
        df_yearly_count['years'] = years

        category_terms = retrieve_terms(category)
        for term in category_terms:

            counts, values = [], []
            for year in years:

                df_annual = df[(df['ref_year'] == year)]
                target_list = list(df_annual[term])
                count = sum(list(df_annual[term]))
                counts.append(count)

                df_annual_term = df_annual[(df_annual[term] > 0)]
                ref_list = list(df_annual_term['ref_values'])
                value = sum(ref_list)
                values.append(value)

            print('counts = ')
            print(counts)

            print('df_yearly_count = ')
            print(df_yearly_count)

            df_yearly_count[term + '_counts'] = counts
            df_yearly_count[str(term + '_values')] = values

        file_dst = str(dataset + '_targeted_count')
        path_dst = os.path.join(retrieve_path(file_dst), category + '_cdf'  + '.csv')
        df_yearly_count.to_csv(path_dst)


def count_targeted_words(dataset, df):
    """
    for all articles types
    count all words
    """

    df_original = df
    # categories of terms to compare
    for category in retrieve_categories():

        print('category = ' + category)

        df = df_original

        for i in range(len(list(df['ref_year']))):

            str_all = ''
            for name in df.columns:
                str_all = str_all + str(df.loc[i,name])
                str_all = str_all + ' '

            str_all = str_all.lower()

            percent_complete = round(i/len(list(df['ref_year']))*100,2)

            category_terms = retrieve_terms(category)
            for term in category_terms:

                #print('term = ' + term)

                df[term] = [0] * len(list(df['ref_year']))

                if ' | ' in term:
                    compare_term_list = term.split(' | ')
                else:
                    compare_term_list = [term]

                if 'both' == term:

                    if df.loc[i,category_terms[0]] == 1:
                        if df.loc[i,category_terms[1]] == 1:
                            print(dataset + ' category = ' + category + ' percent_complete = ' + str(percent_complete))
                            print('found both')
                            df.loc[i,term] = 1
                            df.loc[i,category_terms[0]] = 0
                            df.loc[i,category_terms[1]] = 0
                            print('df.loc[i,term] = ')
                            print(df.loc[i,term])

                            file_dst = str(dataset + '_targeted_count')
                            path_dst = os.path.join(retrieve_path(file_dst), category  + '.csv')
                            print('path_dst = ' + str(path_dst))
                            df.to_csv(path_dst)

                else:
                    for target_term in compare_term_list:
                        #print('target_term = ' + target_term)
                        target_term = target_term.lower()
                        if str(target_term) in str(str_all):
                            print(dataset + ' category = ' + category + ' percent_complete = ' + str(percent_complete))
                            print('found target_term : ' + target_term)
                            df.loc[i,term] = 1
                            print('df.loc[i,term] = ')
                            print(df.loc[i,term])
                            
                            file_dst = str(dataset + '_targeted_count')
                            path_dst = os.path.join(retrieve_path(file_dst), category  + '.csv')
                            print('path_dst = ' + str(path_dst))
                            df.to_csv(path_dst)

                            continue

        file_dst = str(dataset + '_targeted_count')
        path_dst = os.path.join(retrieve_path(file_dst), category  + '.csv')
        print('path_dst = ' + str(path_dst))
        df.to_csv(path_dst)



if __name__ == "__main__":
    main()
