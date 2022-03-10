from bs4 import BeautifulSoup
import datetime
import json
import lxml
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from serpapi import GoogleSearch
import shutil
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
from find_color import find_color
#from scrape_gscholar import scrape_json
#from scrape_gscholar import json_to_dataframe
#from scrape_gscholar import article_json
#from scrape_gscholar import article_df


def aggregate_info():
    """

    """
    tasks = work_to_do()
    work_completed('aggregate_info', 0)
    if  18 in tasks: aggregate_downloaded('nsf_awards')
    if  19 in tasks: aggregate_downloaded('nih_awards')
    if  20 in tasks: aggregate_downloaded('clinical_trials')
    if  21 in tasks: aggregate_patents('patents')
    if  22 in tasks: aggregate_gscholar('gscholar')
    if  23 in tasks: print('aggregate wikipedia')
    if  24 in tasks: annual_count()
    work_completed('aggregate_info', 1)


def annual_count():
    """

    """
    work_completed('aggregate_annual_count', 0)

    for name_dataset in retrieve_list('name_dataset'):

        work_completed('aggregate_annual_count' + '_' + name_dataset, 0)
        name_src, name_dst, name_summary, name_unique, plot_unique = name_paths('gscholar')
        print('name_dataset = ' + name_dataset)

        for term in retrieve_list('search_terms'):

            try:
                print('article = ' + str(name_dataset))
                f = os.path.join(retrieve_path(name_dst),  name_dataset + '_with_address' + '.csv' )
                print('f = ' + str(f))
                df = pd.read_csv(f)
                df = clean_dataframe(df)

            except:
                print('article = ' + str(name_dataset))
                f = os.path.join(retrieve_path(name_dst),  name_dataset + '.csv' )
                print('f = ' + str(f))
                df = pd.read_csv(f)
                df = clean_dataframe(df)

            if df.empty == True: continue

            df_annual = pd.DataFrame()
            years = np.arange(min(list(df['ref_year'])), max(list(df['ref_year'])), 1)
            df_annual['years'] = years

            pdfs, cdfs = [], []
            for year in years:

                df_short =  df[(df['ref_year'] == year)]
                pdf = len(list(df_short.iloc[:,0]))
                pdfs.append(pdf)

                df_short =  df[(df['ref_year'] <= year)]
                cdf = len(list(df_short.iloc[:,0]))
                cdfs.append(cdf)

            df_annual['pdf'] = pdfs
            df_annual['cdf'] = cdfs

            annual_df = str(name_dataset + '_annual_df')
            f = os.path.join(retrieve_path(annual_df), term + '.csv')
            df_annual.to_csv(f)

            annual_plot(name_dataset, df_annual, term)

        work_completed('aggregate_annual_count' + '_' + name_dataset, 1)
 
    work_completed('aggregate_annual_count', 1)


def annual_plot(name_dataset, df_annual, term):
    """

    """
    # begin figure
    plt.close('all')
    figure, axes = plt.subplots()

    plot_num = 2
    plot_row, plot_col, plot_num = 2, 1, 0
    plt.figure(figsize=(plot_col*retrieve_format('fig_wid'), plot_row*retrieve_format('fig_hei')))

    plot_num = plot_num +1
    plt.subplot(plot_row, plot_col, plot_num)
    xx = list(df_annual['years'])
    yy = list(df_annual['pdf'])
    colorMarker, colorEdge, colorTransparency = find_color(6)
    plt.scatter(xx,yy, color=colorMarker, edgecolor=colorEdge, alpha=colorTransparency)

    plt.title(name_dataset)
    plt.xlabel('year')
    plt.ylabel('count (total = ' + str(int(sum(yy))) + ')')

    plot_num = plot_num +1
    plt.subplot(plot_row, plot_col, plot_num)
    xx = list(df_annual['years'])
    yy = list(df_annual['cdf'])
    colorMarker, colorEdge, colorTransparency = find_color(6)
    plt.scatter(xx,yy, color=colorMarker, edgecolor=colorEdge, alpha=colorTransparency)

    plt.title(name_dataset)
    plt.xlabel('year')
    plt.ylabel('count (total = ' + str(int(yy[-1])) + ')')

    annual_plot = str(name_dataset + '_annual_plot')
    f = os.path.join(retrieve_path(annual_plot), term + '.png')
    plt.savefig(f, dpi = 600, edgecolor = 'w')
    plt.close('all')


def aggregate_gscholar(name_dataset):
    """

    """
    work_completed('aggregate_gscholar', 0)

    name_src, name_dst, name_summary, name_unique, plot_unique = name_paths('gscholar')
    src_path = retrieve_path(name_src)
    src_path = os.path.join(src_path, 'df')

    for term in retrieve_list('search_terms'):

        df = pd.DataFrame()

        for file in os.listdir(src_path):

            if term not in file: continue

            df_file = os.path.join(src_path, file)
            df_query = pd.read_csv(df_file)
            df_query = clean_dataframe(df_query)

            df = df.append(df_query)
            df = clean_dataframe(df)
            f = os.path.join(retrieve_path(name_dst),  term + '.csv' )
            df_query.to_csv(f)


    df_query = clean_dataframe(df)
    f = os.path.join(retrieve_path(name_dst),  name_dataset + '.csv' )
    df_query.to_csv(f)

    df = add_ref_year(df, name_dataset)
    list_unique_values(name_dataset, df)
    plot_unique_values(name_dataset)
    cross_plot_unique(name_dataset, df)

    df = clean_dataframe(df)
    f = os.path.join(retrieve_path(name_dst),  name_dataset + '.csv' )
    df.to_csv(f)

    work_completed('aggregate_gscholar', 1)


def aggregate_patents(name_dataset):
    """

    """
    work_completed('aggregate_patents', 0)


    df_all = pd.DataFrame()

    for term in retrieve_list('search_terms'):

        name_src, name_dst, name_summary, name_unique, plot_unique = name_paths(name_dataset)
        download_src = os.path.join(retrieve_path(name_src))

        df = pd.DataFrame()

        for file in os.listdir(download_src):

            if term not in file: continue

            df_src = os.path.join(download_src, file)
            df_src = pd.read_csv(df_src)
            df_src = clean_dataframe(df_src)

            df = df.append(df_src)
            f = os.path.join(retrieve_path(name_dst),  term + '.csv' )
            df = clean_dataframe(df)
            df.to_csv(f)


        df_all = df_all.append(df)
        f = os.path.join(retrieve_path(name_dst), name_dataset + '.csv' )
        df_all = clean_dataframe(df_all)
        df_all.to_csv(f)


    df = clean_dataframe(df)
    df = filter_articles(df, name_dataset)
    df = add_ref_year(df, name_dataset)
    list_unique_values(name_dataset, df)
    plot_unique_values(name_dataset)
    cross_plot_unique(name_dataset, df)

    f = os.path.join(retrieve_path(name_dst),  name_dataset + '.csv' )
    df_all.to_csv(f)

    work_completed('aggregate_patents', 1)


def aggregate_downloaded(name_dataset):
    """

    """
    work_completed('aggregate_info' + '_' + name_dataset, 0)
    # retrieve acquired info
    name_src, name_dst, name_summary, name_unique, plot_unique = name_paths(name_dataset)
    print('name_src = ' + str(name_src))

    try:
        f = os.path.join(retrieve_path(name_src),  name_dataset + '.csv' )
        print('f = ' + str(f))
        df = pd.read_csv(f)
        print('df = ')
        print(df)
        df = clean_dataframe(df)

        print('df.columns')
        print(df.columns)

        if 'nsf' not in name_dataset and 'clinical_trials' not in name_dataset:
            df = filter_articles(df, name_dataset)

        df = add_ref_year(df, name_dataset)
        df = add_ref_value(df, name_dataset)
        list_unique_values(name_dataset, df)
        plot_unique_values(name_dataset)
        cross_plot_unique(name_dataset, df)

        df = clean_dataframe(df)

    except:
        df = pd.DataFrame()


    f = os.path.join(retrieve_path(name_dst),  name_dataset + '.csv' )
    df.to_csv(f)

    work_completed('aggregate_info' + '_' + name_dataset, 1)


def filter_articles(df, name_dataset):
    """

    """
    df['filter_term_count'] = [0] * len(list(df.iloc[:,0]))

    for i in range(len(list(df.iloc[:,0]))):

        print('filtering ' + name_dataset + ' % complete = ' + str(round(100*i/len(list(df.iloc[:,0])),2)))

        str_article = ''
        for col_name in df.columns:

            value = str(df.loc[i,col_name])
            str_article = str_article + ' ' + value

        #print('str_article = ')
        #print(str_article)

        #print('retrieve_list(\'filter_terms\') = ')
        #print(retrieve_list('filter_terms'))

        for filter_term in retrieve_list('filter_terms'):

            if str(filter_term) in str(str_article):

                df.loc[i,'filter_term_count'] = int(df.loc[i,'filter_term_count']) + 1

    assert sum(df['filter_term_count']) > 0

    f = os.path.join(retrieve_path(name_dataset + '_aggregate_df'),  name_dataset + '_no_filter' + '.csv' )
    df = clean_dataframe(df)
    df.to_csv(f)

    len_before = len(list(df.iloc[:,0]))
    df =  df[(df['filter_term_count'] > 1)]
    len_after = len(list(df.iloc[:,0]))
    per_change = round(100*(len_before - len_after)/len_after,2)
    print('len changed after filtering = ' + str(len_before - len_after) + ' % change = ' + str(per_change))
    if len_before - len_after > 1:
        time.sleep(10)

    df = clean_dataframe(df)
    f = os.path.join(retrieve_path(name_dataset + '_aggregate_df'),  name_dataset + '.csv' )
    df.to_csv(f)

    return(df)


def list_unique_values(name_dataset, df):
    """

    """
    for col_name in df.columns:

        col_name = str(col_name)
        print('col_name = ' + str(col_name))
        ref_list = list(df[col_name])
        print('ref_list = ')

        names, counts, percents = [], [], []
        for name in ref_list:
            if name not in names:
                names.append(name)
                counts.append(ref_list.count(name))
                percent = 100*counts[-1]/len(ref_list)
                percents.append(round(percent,2))


        df_count = pd.DataFrame()
        df_count['value'] = names
        df_count['counts'] = counts
        df_count['percents'] = percents
        df_count = df_count.sort_values('percents', ascending=False)
        df_count = df_count.reset_index()
        del df_count['index']

        print('df_count = ')
        print(df_count)

        if '/' in col_name:
            col_name_split = col_name.split('/')
            col_name = col_name_split[0]

        name_src, name_dst, name_summary, name_unique, plot_unique = name_paths(name_dataset)
        print('name_src = ' + str(name_src))
        f = os.path.join(retrieve_path(name_unique),  col_name + '.csv' )
        df_count.to_csv(f)


def plot_unique_values(name_dataset):
    """

    """
    name_src, name_dst, name_summary, name_unique, plot_unique = name_paths(name_dataset)

    for file in os.listdir(retrieve_path(name_unique)):

        src_path = os.path.join(retrieve_path(name_unique), file)
        print('src_path = ' + str(src_path))
        df = pd.read_csv(src_path)

        xx = remove_dollar_sign(list(df['value']))
        yy = remove_dollar_sign(list(df['counts']))

        try:
            # begin figure
            plt.close('all')
            figure, axes = plt.subplots()
            plot_num = 1
            plt.figure(figsize=(retrieve_format('fig_wid'), retrieve_format('fig_hei')))
            plt.subplot(111)

            xx = [float(i) for i in xx]
            yy = [float(i) for i in yy]
            colorMarker, colorEdge, colorTransparency = find_color(6)
            plt.scatter(xx,yy, color=colorMarker, edgecolor=colorEdge, alpha=colorTransparency)

            file_split = file.split('.')
            filename = file_split[0]
            plt.title(name_dataset + ' ' + filename)
            plt.xlabel(filename)
            plt.ylabel('count (total = ' + str(int(sum(yy))) + ')')

            dst_plot = os.path.join(retrieve_path(plot_unique),  filename + '.png' )
            plt.savefig(dst_plot, dpi = 600, edgecolor = 'w')
            plt.close('all')
            print('dst_plot = ' + str(dst_plot))

        except:
            hello = 'hello'


def cross_plot_unique(name_dataset, df):
    """

    """
    name_src, name_dst, name_summary, name_unique, plot_unique = name_paths(name_dataset)
    col_names = list(df.columns)

    for name_1 in col_names:

        for name_2 in col_names:

            if col_names.index(name_1) <= col_names.index(name_2): continue

            #if name_1 != 'ref_year': continue
            #if name_2 != 'AwardNumber': continue

            try:
                # begin figure
                plt.close('all')
                figure, axes = plt.subplots()
                plot_num = 1
                plt.figure(figsize=(retrieve_format('fig_wid'), retrieve_format('fig_hei')))
                plt.subplot(111)

                xx = remove_dollar_sign(list(df[name_1]))
                xx = [float(i) for i in xx]
                yy = remove_dollar_sign(list(df[name_2]))
                yy = [float(i) for i in yy]

                colorMarker, colorEdge, colorTransparency = find_color(col_names.index(name_1))
                plt.scatter(xx,yy, color=colorMarker, edgecolor=colorEdge, alpha=colorTransparency)

                print('names: ' + str(name_1) + ' ' + str(name_2))

                filename = str(name_1 + '_' + name_2)
                plt.title(name_dataset + ' (n=' + str(len(xx)) + ')')
                plt.xlabel(name_1)
                plt.ylabel(name_2)

                dst_plot = os.path.join(retrieve_path(plot_unique),  filename + '.png' )
                plt.savefig(dst_plot, dpi = 600, edgecolor = 'w')
                plt.close('all')
                print('dst_plot = ' + str(dst_plot))

            except:
                hello = 'hello'


def remove_dollar_sign(xx):
    """
    remove $ and return float
    """
    for i in range(len(xx)):

        x = str(xx[i])

        """
        if '$' in x and len(x) < 25:
            #print('x = ' + str(x))
            x = x.replace('$','')
            x = x.replace(',','')
            xx[i] = float(x)
        """

        try:
            x = x.replace('$','')
            x = x.replace(',','')
            x = float(x)
            xx[i] == x
        except:
            hello = 'hello'

        try:
            x = x.replace(',', '')
            x = float(x)
            xx[i] == x
        except:
            hello = 'hello'

        try:
            x_int = int(x)
            if x_int - x == 0:
                xx[i] = x_int
        except:
            hello = 'hello'

    return(xx)


def add_ref_year(df, name_dataset):
    """
    add ref year
    """
    print(df)
    print(df.columns)

    # add ref_year
    years = []
    if name_dataset == 'nsf_awards':
        for date in list(df['StartDate']):
            print('date = ' + str(date))
            date_split = date.split('/')
            year = date_split[-1]
            years.append(year)

    if name_dataset == 'nih_awards':

        for date in list(df['Project Start Date']):

            try:
                print('date = ' + str(date))
                date_split = date.split(' ')
                date = date_split[0]
                date_split = date.split('/')
                date = date_split[-1]
                date = int(date)
                print('date = ' + str(date))
            except:
                date = 1900
            years.append(date)

    if name_dataset == 'clinical_trials':
        for date in list(df['Start Date']):
            #print('date = ' + str(date))
            try:
                year = re.findall('[0-9]{4}', date)
                year = year[0]
                year = int(year)
            except:
                year = 1900
            #print('date = ' + str(date))
            years.append(year)


    if name_dataset == 'patents':
        print(df.columns)
        for date in list(df['file_date']):
            print(date)
            date_split = date.split(' ')
            year = date_split[-1]
            print(year)
            years.append(year)


    if name_dataset == 'gscholar':
        for date in list(df['publication_info']):

            try:
                print('date = ' + str(date))
                year = re.findall('[0-9]{4}', date)
                year = year[0]
                year = int(year)
                print('year = ')
                print(year)
            except:
                year = 0

            years.append(int(year))
            print('len(years) = ' + str(len(years)))

    try:
        years = [int(i) for i in years]
        df['ref_year'] = years
        min_year = int(retrieve_format('min_year'))
        df =  df[(df['ref_year'] >= min_year)]
        df = clean_dataframe(df)
    except:
        #df = df.sort_values('ref_years', ascending=False)
        df['ref_year'] = years
        df = clean_dataframe(df)
    return(df)


def add_ref_value(df, name_dataset):
    """
    add ref year
    """
    print(df)
    print(df.columns)

    # add ref_year
    values = []
    if name_dataset == 'nsf_awards':
        for value in list(df['AwardedAmountToDate']):
            value = remove_dollar_sign([value])
            values.append(value[0])

    if name_dataset == 'nih_awards':
        for value in list(df['Direct Cost IC']):
            try:
                value = float(value)
                if value > 0: value = remove_dollar_sign([value])
                else: value = [0]
            except:
                value = [0]
            values.append(value[0])

    if name_dataset == 'clinical_trials':
        for value in list(df['Enrollment']):
            try:
                value = int(value)
            except:
                value = 0
            values.append(value)


    if name_dataset == 'patents':
        for value in list(df['family_id']):
            try:
                value = int(value)
            except:
                value = 0
            values.append(value)


    if name_dataset == 'gscholar':
        for value in list(df['citations']):
            try:
                value = int(value)
            except:
                value = 0
            values.append(value)


    df['ref_value'] = values
    #df = df.sort_values('ref_years', ascending=False)
    return(df)


if __name__ == "__main__":
    main()
