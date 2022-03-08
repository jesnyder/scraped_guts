from bs4 import BeautifulSoup
import datetime
import glob
import json
import lxml
import math
import matplotlib.pyplot as plt
import numpy as np
import os
from os.path import exists
import pandas as pd
from PIL import Image
from serpapi import GoogleSearch
import re
import requests
import time
import urllib.parse


from a0001_admin import clean_dataframe
from a0001_admin import name_paths
from a0001_admin import retrieve_categories
from a0001_admin import retrieve_format
from a0001_admin import retrieve_list
from a0001_admin import retrieve_path
from a0001_admin import write_paths
from find_color import find_color
from gif_maker import build_gif


def map_maker():
    """

    """
    print('began map_maker')

    # List task numbers to complete
    tasks = [2,3]
    write_paths()
    if  0 in tasks: tasks = np.arange(1, 101, 1)
    if  1 in tasks: data_for_js_map()
    if  2 in tasks: yearly_map()
    if  3 in tasks: build_gif()
    if  4 in tasks: yearly_map_bar()

    print('completed map_maker')


def data_for_js_map():
    """

    """
    for name_dataset in retrieve_list('type_article'):

        # list compare term files
        compare_terms = os.path.join(retrieve_path('term_compare'))
        for category in retrieve_categories():

            # retrieve search terms
            f = os.path.join(retrieve_path('term_compare'), category + '.csv')
            search_terms = retrieve_list(f)

            # retrieve list of al articles
            file_src = str(name_dataset + '_compare_terms_df')
            f = os.path.join(retrieve_path(file_src), category  + '.csv')
            print('f = ' + str(f))
            df = clean_dataframe(pd.read_csv(f))
            df =  df[(df['ref_lat'] != 0)]

            df_js = pd.DataFrame()

            df_js['0'] = [np.round(float(i), 6) for i in list(df['ref_lon'])]
            df_js['1'] = [np.round(float(i), 6) for i in list(df['ref_lat'])]
            df_js['date'] = list(df['StartDate'])
            df_js =  df_js[(df_js['0'] >= -120)]
            df_js =  df_js[(df_js['0'] <= -79)]
            df_js =  df_js[(df_js['1'] >= 25)]
            df_js =  df_js[(df_js['1'] <= 47)]


            js_data = str(name_dataset + '_js_data')
            f = os.path.join(retrieve_path(js_data), category + '.tsv')
            df_js.to_csv(f, sep="\t", index=False)

            f = os.path.join(retrieve_path('term_compare'), category + '.csv')
            for term in  retrieve_list(f):

                print('term = ' + str(term))

                df_short =  df[(df[term] > 0)]
                df_js = pd.DataFrame()

                df_js['0'] = [np.round(float(i), 6) for i in list(df_short['ref_lon'])]
                df_js['1'] = [np.round(float(i), 6) for i in list(df_short['ref_lat'])]
                df_js['date'] = list(df_short['StartDate'])
                df_js =  df_js[(df_js['0'] >= -120)]
                df_js =  df_js[(df_js['0'] <= -79)]
                df_js =  df_js[(df_js['1'] >= 25)]
                df_js =  df_js[(df_js['1'] <= 47)]

                try:
                    term_label = term.split('|')[0]
                except:
                    term_label = term
                js_data = str(name_dataset + '_js_data')
                f = os.path.join(retrieve_path(js_data), category + '_' + term_label + '.tsv')
                df_js.to_csv(f, sep="\t", index=False)


def yearly_map_bar():
    """
    from df map each year
    """

    # list articles
    for name_dataset in retrieve_list('type_article'):

        # list compare term files
        compare_terms = os.path.join(retrieve_path('term_compare'))
        for category in retrieve_categories():

            # retrieve search terms
            f = os.path.join(retrieve_path('term_compare'), category + '.csv')
            search_terms = retrieve_list(f)

            # retrieve list of al articles
            file_src = str(name_dataset + '_compare_terms_df')
            f = os.path.join(retrieve_path(file_src), category  + '.csv')
            print('f = ' + str(f))
            df = clean_dataframe(pd.read_csv(f))
            df =  df[(df['ref_lat'] != 0)]

            print('df.columns = ')
            print(df.columns)
            print('name_dataset = ' + name_dataset)


            years = np.arange(int(min(list(df['ref_year']))), int(max(list(df['ref_year']))), 1)

            for year in years:

                print('year = ' + str(year))

                df_temp =  df[(df['ref_year'] <= year)]
                lats = list(df_temp['ref_lat'])
                lons = list(df_temp['ref_lon'])

                plt.close('all')
                figure, axes = plt.subplots()
                plot_row, plot_col, plot_num = 2, 1, 0
                plt.rc('font', size=10) #controls default text size
                plt.figure(figsize=(plot_col*retrieve_format('fig_wid'), plot_row*retrieve_format('fig_hei')))
                #plt.figure(figsize=(plot_col*90, plot_row*45))

                plot_num = plot_num +1
                plt.subplot(plot_row, plot_col, plot_num)

                # add background of the globe
                map_path = os.path.join(retrieve_path('blank_map'))
                img = plt.imread(map_path)
                extent = [-170, 190, -58, 108]
                axes.imshow(img, extent=extent, aspect='auto')

                label_str = str(len(list(df_temp['ref_year']))) + ' ' + 'all '
                num = 8
                colorMarker, colorEdge, colorTransparency = find_color(num)
                plt.scatter(lons, lats, color=colorMarker, edgecolors=colorEdge, alpha=float(colorTransparency),label=label_str)

                for term in search_terms:
                    #if '|' in term: term = (term.split('|'))[0]
                    df_term =  df_temp[(df_temp[term] > 0)]
                    lats = list(df_term['ref_lat'])
                    lons = list(df_term['ref_lon'])
                    label_str = str(len(list(df_term['ref_year']))) + ' ' + term
                    num = search_terms.index(term) +1
                    colorMarker, colorEdge, colorTransparency = find_color(num)

                    # set sizes based on the reference value
                    try:
                        sizes = []
                        for  size in list(df_term['ref_value']):
                            sizes.append(size+10)
                        sizes = scale_sizes(sizes)
                    except:
                        sizes = [40]*len(lons)

                    plt.scatter(lons, lats, s=sizes, color=colorMarker, edgecolors=colorEdge, linewidth=float(retrieve_format('markeredgewidth')), alpha=float(colorTransparency),label=label_str)

                axes.axis('off')
                plt.title(name_dataset + ' ' + str(int(min(list(df['ref_year'])))) + '-' + str(year))
                plt.legend(bbox_to_anchor=(0.2, -0.2), loc ="upper left")


                plot_num = plot_num +1
                plt.subplot(plot_row, plot_col, plot_num)

                file_src = str(name_dataset + '_compare_terms_annual_count_df')
                compare_file_term = str(category + '_percent')
                path_src = os.path.join(retrieve_path(file_src), compare_file_term  + '.csv')
                df_bar = clean_dataframe(pd.read_csv(path_src))

                #print('df_bar = ')
                #print(df_bar)
                #print('df_bar.columns = ')
                #print(df_bar.columns)

                df_bar =  df_bar[(df_bar['cdf_total'] > 0)]
                df_bar = clean_dataframe(df_bar)
                #print('df_bar = ')
                #print(df_bar)

                df_bar =  df_bar[(df_bar['years'] <= year)]

                for term in search_terms:
                    color_index = search_terms.index(term)
                    #if '|' in term: term = (term.split('|'))[0]
                    term_per = str(term + '_percent')
                    xx = list(df_bar['years'])
                    yy = list(df_bar[term_per])

                    offsets = [0] * len(list(xx))

                    if color_index > 0:
                        offsets = []
                        for k in range(len(list(df_bar['years']))):
                            offset = 0
                            for j in range(color_index):
                                #term = term_list[j]
                                offset = offset + df_bar.loc[k][search_terms[j] + '_percent']
                            offsets.append(offset)

                    assert len(offsets) == len(xx)
                    assert len(offsets) == len(yy)
                    try:
                        label_term = str(round(100*yy[-1],2)) + '% ' + term
                    except:
                        label_term = str(0) + '% ' + term
                    colorMarker, colorEdge, colorTransparency = find_color(color_index)
                    plt.bar(xx, yy, width=1.0, bottom=offsets, align='center', color=colorMarker,label = label_term)


                plt.title(name_dataset + ' Percent ' + str(int(sum(list(df_bar['annual_total'])))))
                plt.xlabel('year')
                plt.xlim([min(years), max(years)])
                plt.ylabel(term_per)
                # plt.yscale('log')
                plt.legend(bbox_to_anchor=(0.2, -0.2), loc='upper left')
                #plt.legend(bbox_to_anchor=(1, 0.8), loc='upper left')

                file_dst_name = str(name_dataset + '_map_bar_png')
                df_file = os.path.join(retrieve_path(file_dst_name), category + '_' + str(year) + '.png')
                plt.savefig(df_file, bbox_inches='tight', dpi=150, edgecolor = 'w')
                plt.close('all')


### completed programs ###


def build_gif():
    """

    """
    print('building gif')

    # list articles
    for name_dataset in retrieve_list('type_article'):

        for map_type in ['_map_png', '_map_bar_png']:

            file_dst_name = str(name_dataset + map_type)
            df_src = os.path.join(retrieve_path(file_dst_name))

            # list compare term files
            compare_terms = os.path.join(retrieve_path('term_compare'))
            for category in retrieve_categories():

                png_list = []
                for file in os.listdir(df_src):

                    if category not in str(file): continue
                    #df_src = os.path.join(retrieve_path(file_dst_name), file)
                    png_list.append(os.path.join(retrieve_path(file_dst_name), file))

                #print('png_list = ')
                #print(png_list)
                #assert len(png_list) > 1

                frames = []
                #png_file = os.path.join(path, "*.png")
                gif_dst = str(name_dataset + '_map_gif')
                save_file = os.path.join(retrieve_path(gif_dst) , category + '.gif')
                print('save_file = ' + str(save_file))

                #imgs = glob.glob(png_file)
                for i in png_list:

                    per_complete = round(100*png_list.index(i)/len(png_list),2)
                    print(name_dataset + ' ' + category + ' % complete = ' + str(per_complete) )

                    new_frame = Image.open(i)
                    frames.append(new_frame)

                    # Save into a GIF file that loops forever
                    frames[0].save(save_file, format='GIF',
                                append_images=frames[1:],
                                save_all=True,
                                duration=500, loop=0)


def scale_sizes(sizes):
    """
    provide list of numbers
    scale
    """

    scatter_size_min = int(retrieve_format('scatter_size_min'))
    scatter_size_max = int(retrieve_format('scatter_size_min'))

    sizes_scaled = []
    for size in sizes:

        try:
            size_min = size + 2
            size_scaled = math.log(size_min)
            size_scaled = math.sqrt(size_min)
            size_scaled = float(size_scaled)
        except:
            size_scaled = scatter_size_min
            size_scaled = float(size_scaled)

        size_scaled = scatter_size_max*size_scaled/max(sizes) + scatter_size_min
        sizes_scaled.append(size_scaled)

    assert len(sizes) == len(sizes_scaled)
    return(sizes_scaled)


def yearly_map():
    """
    from df map each year
    """

    # list articles
    for name_dataset in retrieve_list('type_article'):

        # list compare term files
        compare_terms = os.path.join(retrieve_path('term_compare'))
        for category in retrieve_categories():

            # retrieve search terms
            f = os.path.join(retrieve_path('term_compare'), category + '.csv')
            search_terms = retrieve_list(f)

            # retrieve list of al articles
            file_src = str(name_dataset + '_compare_terms_df')
            f = os.path.join(retrieve_path(file_src), category  + '.csv')
            print('f = ' + str(f))
            df = clean_dataframe(pd.read_csv(f))
            df =  df[(df['ref_lat'] != 0)]
            df =  df[(df['ref_lon'] != 0)]
            try:
                df = df.dropna(subset=['ref_value'])
            except:
                df['ref_value'] = [1]*len(list(df['ref_lat']))

            print('df.columns = ')
            print(df.columns)
            #print('name_dataset = ' + name_dataset)

            #print('df[\'ref_lat\'] = ')
            #print(df['ref_lat'])

            # trim the geolocated data to map extents
            extent = [-170, 190, -58, 108]
            df =  df[(df['ref_lat'] >= extent[0])]
            df =  df[(df['ref_lat'] <= extent[1])]
            #df =  df[(df['ref_lon'] >= extent[2])]
            #df =  df[(df['ref_lon'] <= extent[3])]

            print('df = ')
            print(df)

            years = np.arange(int(min(list(df['ref_year']))), int(max(list(df['ref_year']))), 1)

            for year in years:

                print('year = ' + str(year))

                df_temp =  df[(df['ref_year'] <= year)]
                lats = list(df_temp['ref_lat'])
                lons = list(df_temp['ref_lon'])
                #lats = [float(i) for i in list(df_temp['ref_lat'])]
                #lons = [float(i) for i in list(df_temp['ref_lon'])]

                #print('lons = ')
                #print(lons)
                #print('lats =')
                #print(lats)


                plt.close('all')
                figure, axes = plt.subplots()
                plt.rc('font', size=retrieve_format('map_font_size')) #controls default text size

                # add background of the globe
                map_path = os.path.join(retrieve_path('blank_map'))
                img = plt.imread(map_path)
                extent = [-170, 190, -58, 108]
                axes.imshow(img, extent=extent)

                #print('df[\'ref_value\'] = ')
                #print(df['ref_value'])

                total_ref_value = sum(list(df_temp['ref_value']))

                if 'award' in str(name_dataset):
                    total_ref_value_millions = round(total_ref_value/1000000,2)
                    label_str = str(len(list(df_temp['ref_year']))) + ' $' + str(total_ref_value_millions) + 'million invested in ' + 'all'

                elif 'clincial_trials' == str(name_dataset):
                    total_ref_value = int(total_ref_value)
                    label_str = str(len(list(df_temp['ref_year']))) + ' ' + str(total_ref_value) + 'patients enrolled in ' + 'all'

                else:
                    total_ref_value = int(total_ref_value)
                    label_str = str(len(list(df_temp['ref_year']))) + ' '  + 'all'


                colorMarker, colorEdge, colorTransparency = find_color('end')

                plt.scatter(lons, lats, color=colorMarker, edgecolors=colorMarker, alpha=0.25, label=label_str)


                for term in search_terms:
                    #if '|' in term: term = (term.split('|'))[0]
                    df_term =  df_temp[(df_temp[term] > 0)]
                    lats = list(df_term['ref_lat'])
                    lons = list(df_term['ref_lon'])
                    total_ref_value = sum(list(df_term['ref_value']))

                    if 'award' in str(name_dataset):
                        total_ref_value_millions = round(total_ref_value/1000000,2)
                        label_str = str(len(list(df_term['ref_year']))) + ' $' + str(total_ref_value_millions) + ' million invested in ' + term

                    elif 'clincial_trials' == str(name_dataset):
                        total_ref_value = int(total_ref_value)
                        label_str = str(len(list(df_term['ref_year']))) + ' ' + str(total_ref_value) + ' patients enrolled in ' + term

                    else:
                        total_ref_value = int(total_ref_value)
                        label_str = str(len(list(df_term['ref_year']))) + ' '  + term


                    num = search_terms.index(term)
                    colorMarker, colorEdge, colorTransparency = find_color(num)

                    # set sizes based on the reference value
                    try:
                        sizes = []
                        for  size in list(df_term['ref_value']):
                            sizes.append(size+10)
                        sizes = scale_sizes(sizes)
                    except:
                        sizes = [40]*len(lons)

                    plt.scatter(lons, lats, s=sizes, color=colorMarker, edgecolors=colorMarker, linewidth=float(retrieve_format('markeredgewidth')), alpha=float(colorTransparency),label=label_str)

                axes.axis('off')
                plt.title(category + ' ' + name_dataset + ' ' + str(int(min(list(df['ref_year'])))) + '-' + str(year))
                plt.legend(bbox_to_anchor=(0.3, 0.10), loc ="upper left")

                file_dst_name = str(name_dataset + '_map_png')
                #print('file_dst_name = ')
                #print(file_dst_name)
                df_file = os.path.join(retrieve_path(file_dst_name), category + '_' + str(year) + '.png')
                #print('df_file = ')
                #print(df_file)
                plt.savefig(df_file, bbox_inches='tight', dpi=retrieve_format('plot_dpi'), edgecolor = 'w')
                plt.close('all')


if __name__ == "__main__":
    main()
