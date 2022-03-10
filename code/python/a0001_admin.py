from bs4 import BeautifulSoup
from datetime import datetime
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


def clean_dataframe(df):


    df = df.drop_duplicates()

    col_names = df.columns

    for name in df.columns:

        if 'Unnamed:' in str(name):
            del df[name]

        if 'index' in str(name):
            del df[name]

    col_names_sort = ['patent_num', 'AwardNumber', 'citations']
    for name in col_names_sort:
        try:
            df = df.drop_duplicates()
            df = df.sort_values(name, ascending=True)
        except:
            hello = 'hello'

    try:
        df = df.reset_index()
        del df['index']
    except:
        hello = 'hello'

    return(df)


def name_paths(name_dataset):
    """
    provide article type
    make the needed files
    """

    name_src = str(name_dataset + '_src_query')
    name_dst = str(name_dataset + '_dst_query')
    name_summary = str(name_dataset + '_sum')
    name_unique = str(name_dataset + '_unique_df')
    plot_unique = str(name_dataset + '_unique_plot')

    return name_src, name_dst, name_summary, name_unique, plot_unique


def retrieve_categories():
    """
    return file names in compare term folder
    """
    list_categories = []

    compare_terms = os.path.join(retrieve_path('term_compare'))
    for file in os.listdir(compare_terms):

        file_split = file.split('.')
        file_name = file_split[0]
        list_categories.append(file_name)

    return(list_categories)


def retrieve_color(color_num):
    """

    """
    f = os.path.join(retrieve_path('colors'))
    df = pd.read_csv(f)
    df = clean_dataframe(df)

    for col_name in df.columns:

        if 'name' in col_name:
            names = list(df[col_name])

        if 'value' in col_name:
            values = list(df[col_name])

    if color_num == 'end': color_num = len(values)-1
    color_num = color_num%len(names)
    color_name = names[color_num]
    color_values = values[color_num]

    color_values = color_values.split(' ')
    for i in range(len(color_values)):
        num = color_values[i]
        num = float(num)
        if num > 1:
            num = num/255
        color_values[i] = num

    assert len(color_values) == 3

    return(color_values)


def retrieve_datetime():
    """
    send current time as a string
    """

    # datetime object containing current date and time
    now = datetime.now()

    print("now =", now)

    # dd/mm/YY H:M:S
    dt_string = now.strftime("%Y-%m-%d %H %M %S")
    print("date and time =", dt_string)

    return(dt_string)


def retrieve_format(name):
    """
    from name, return variable
    lookup in ref file:
    user_provided/admin/format.csv
    """

    f = os.path.join(retrieve_path('format'))
    df = pd.read_csv(f)

    # find the value from the name
    df = df.loc[df['name'] == name]

    value = list(df['value'])
    value = value[0]
    value = value.split(' ')

    if name == 'markeredgewidth': return(float(value[0]))
    if name == 'plot_font_size': return(int(value[0]))

    try:
        value = [int(item) for item in value]
    except:
        value = [str(item) for item in value]

    if name == 'fig_wid': value = int(value[0])
    if name == 'fig_hei': value = int(value[0])

    try:
        if len(value) == 1:
            value = int(value[0])
    except:
        hello = 'hello'

    return(value)


def retrieve_list(name):
    """
    from the name of a csv path file
    return a list
    """
    try:
        article_path = os.path.join(retrieve_path(name))
        df = pd.read_csv(article_path)

    except:
        df = pd.read_csv(name)

    df = clean_dataframe(df)

    for col in df.columns:
            target_list = list(df[col])

    return(target_list)


def retrieve_path(name):
    """
    from the name of a file
    return the path to the file
    """
    #print('began retrieve_path')


    print('name = ' + name)
    for file_source in ['core_code', 'user_provided', 'program_generated']:

        try:
            f = os.path.join(file_source, 'admin', 'paths' + '.csv')
            print('file = ' + str(f))
            df = pd.read_csv(f)

            # find the path from the name
            df = df.loc[df['name'] == name]
            path = list(df['path'])
            path = path[0]
            path = path.split(' ')
            break

        except:
            hello = 'hello'
            #print('retrieve_path: file not found: ' + name)
            #print('file not found.')


    # build the folder required to save a file
    for folder in path:

        # skip file names
        if '.' in str(folder):
            break

        # intiate a new variable to describe the path
        if folder == path[0]:
            path_short = os.path.join(folder)

        # add folders iteratively to build path
        else:
            path_short = os.path.join(path_short, folder)

        # check if the path exists
        if not os.path.exists(path_short):
            os.makedirs(path_short)

    path = os.path.join(*path)
    return(path)


def write_paths():
    """
    write the paths for all the articles
    """

    name, path = [], []
    df_article = pd.read_csv(retrieve_path('name_dataset'))
    for name_dataset in list(df_article['name']):

        name_src, name_dst, name_summary, name_unique, plot_unique = name_paths(name_dataset)
        name_list =  name_paths(name_dataset)
        name_list = list(name_list)

        name_list.append(str(name_dataset + '_query_html'))
        name_list.append(str(name_dataset + '_query_xml'))
        name_list.append(str(name_dataset + '_query_json'))
        name_list.append(str(name_dataset + '_query_df'))
        name_list.append(str(name_dataset + '_article_html'))
        name_list.append(str(name_dataset + '_article_xml'))
        name_list.append(str(name_dataset + '_article_json'))
        name_list.append(str(name_dataset + '_article_df'))
        name_list.append(str(name_dataset + '_aggregate_df'))
        name_list.append(str(name_dataset + '_annual_df'))
        name_list.append(str(name_dataset + '_annual_plot'))
        name_list.append(str(name_dataset + '_count_all_words_df'))
        name_list.append(str(name_dataset + '_compare_terms_df'))
        name_list.append(str(name_dataset + '_compare_terms_annual_count_df'))
        name_list.append(str(name_dataset + '_compare_terms_plot'))
        name_list.append(str(name_dataset + '_compare_terms_plot_bar'))
        name_list.append(str(name_dataset + '_map_png'))
        name_list.append(str(name_dataset + '_map_gif'))
        name_list.append(str(name_dataset + '_map_bar_png'))
        name_list.append(str(name_dataset + '_map__bar_gif'))
        name_list.append(str(name_dataset + '_js_data'))



        for item in name_list:
            name.append(item)

            if 'src' in item:
                item_path = str('program_generated ' + name_dataset + ' query src')

            elif 'dst' in item:
                item_path = str('program_generated ' + name_dataset + ' query agg')

            elif 'sum' in item:
                item_path = str('program_generated ' + name_dataset + ' sum')

            elif 'unique_df' in item:
                item_path = str('program_generated ' + name_dataset + ' unique df')

            elif '_unique_plot' in item:
                item_path = str('program_generated ' + name_dataset + ' unique plot')

            elif '_query_html' in item:
                item_path = str('program_generated ' + name_dataset + ' query html')

            elif '_query_xml' in item:
                item_path = str('program_generated ' + name_dataset + ' query xml')

            elif '_query_json' in item:
                item_path = str('program_generated ' + name_dataset + ' query json')

            elif '_query_df' in item:
                item_path = str('program_generated ' + name_dataset + ' query df')

            elif '_article_html' in item:
                item_path = str('program_generated ' + name_dataset + ' article html')

            elif '_article_xml' in item:
                item_path = str('program_generated ' + name_dataset + ' article xml')

            elif '_article_json' in item:
                item_path = str('program_generated ' + name_dataset + ' article json')

            elif '_article_df' in item:
                item_path = str('program_generated ' + name_dataset + ' article df')

            elif '_aggregate_df' in item:
                item_path = str('program_generated ' + name_dataset + ' aggregate df')

            elif '_annual_df' in item:
                item_path = str('program_generated ' + name_dataset + ' annual df')

            elif '_annual_plot' in item:
                item_path = str('program_generated ' + name_dataset + ' annual plot')

            elif '_count_all_words_df' in item:
                item_path = str('program_generated ' + name_dataset + ' count_words df')

            elif '_compare_terms_df' in item:
                item_path = str('program_generated ' + name_dataset + ' compare_terms df')

            elif '_compare_terms_annual_count_df' in item:
                item_path = str('program_generated ' + name_dataset + ' compare_terms df_annual')

            elif '_compare_terms_plot' in item:
                item_path = str('program_generated ' + name_dataset + ' compare_terms plot')

            elif '_map_png' in item:
                item_path = str('program_generated ' + name_dataset + ' map png')

            elif '_map_gif' in item:
                item_path = str('program_generated ' + name_dataset + ' map gif')

            elif '_map_bar_png' in item:
                item_path = str('program_generated ' + name_dataset + ' map_bar png')

            elif '_map_bar_gif' in item:
                item_path = str('program_generated ' + name_dataset + ' map_bar gif')

            elif '_js_data' in item:
                item_path = str('program_generated ' + name_dataset + ' js_data')

            elif '_compare_terms_plot_bar' in item:
                item_path = str('program_generated ' + name_dataset + ' compare_terms bar_chart')





            path.append(item_path)

    df = pd.DataFrame()
    df['name'] = name
    df['path'] = path
    f = os.path.join(retrieve_path('write_paths'))
    df.to_csv(f)


def work_completed(task_name, task_number, complete):
    """

    """

    print('task number = ' + str(task_number) + ' task name = ' + task_name)

    df = pd.DataFrame()
    df['name'] = [task_name]
    df['number'] = [task_number]
    df['complete'] = [complete]
    df['active'] = [task_number*complete]
    df['date'] = [str(retrieve_datetime())]

    try:
        df_ref = clean_dataframe(pd.read_csv(os.path.join(retrieve_path('work_plan'))))
        df_ref = df_ref.append(df)
        df = df_ref
    except:
        df = df

    print('df = ')
    print(df)

    df.drop_duplicates()
    df = df.sort_values('number', ascending=False)
    #df.drop_duplicates(subset='complete', keep='first')
    df = clean_dataframe(df)
    df.to_csv(os.path.join(retrieve_path('work_plan')))


def work_plan():
    """

    """

    df_ref = clean_dataframe(pd.read_csv(os.path.join(retrieve_path('work_plan'))))


if __name__ == "__main__":
    main()
