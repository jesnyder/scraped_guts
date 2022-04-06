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


def map_maker(dataset):
    """

    """
    print('began map_maker')

    yearly_map(dataset)
    build_gif(dataset)

    print('completed map_maker')


def build_gif(dataset):
    """

    """
    print('building gif')


    file_dst_name = str(dataset + map_type)
    df_src = os.path.join(retrieve_path(file_dst_name))

    # list compare term files
    compare_terms = os.path.join(retrieve_path('term_compare'))
    for category in retrieve_categories():

        png_list = []
        for file in os.listdir(df_src):

            if category not in str(file): continue
                #df_src = os.path.join(retrieve_path(file_dst_name), file)
                png_list.append(os.path.join(retrieve_path(file_dst_name), file))

                frames = []
                #png_file = os.path.join(path, "*.png")
                gif_dst = str(dataset + '_map_gif')
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


def yearly_map(dataset):
    """
    from df map each year
    """

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

            file_dst_name = str(dataset + '_map_png')
            #print('file_dst_name = ')
            #print(file_dst_name)
            df_file = os.path.join(retrieve_path(file_dst_name), category + '_' + str(year) + '.png')
            #print('df_file = ')
            #print(df_file)
            plt.savefig(df_file, bbox_inches='tight', dpi=retrieve_format('plot_dpi'), edgecolor = 'w')
            plt.close('all')


if __name__ == "__main__":
    main()
