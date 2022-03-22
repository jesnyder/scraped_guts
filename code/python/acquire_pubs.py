from bs4 import BeautifulSoup
from crossref.restful import Works
import datetime
from habanero import Crossref
import json
import lxml
import numpy as np
import os
import pandas as pd
import shutil
import random
import re
import requests
import time

from a0001_admin import clean_dataframe
from a0001_admin import name_paths
from a0001_admin import retrieve_datetime
from a0001_admin import retrieve_format
from a0001_admin import retrieve_list
from a0001_admin import retrieve_path
from a0001_admin import write_paths
from a0001_admin import work_completed
from a0001_admin import work_to_do


def acquire_pubs():
    """

    """

    # set acquire_pubs as a task
    work_completed('acquire_pubs', 0)

    search()

    #list_urls()

    #metadata_json()

    # make a folder of json data on pubs search term in crossref as json


    # search term in gscholar as json

    # list all urls as dataframe

    # metadata from url as json

    # metadate from crossref as json

    # aggregate in json

    # aggregate in dataframe

    hello

    # completed acquire_pubs
    work_completed('acquire_pubs', 1)


def link_to_filename(link):
    """
    return filename from link
    """
    chars = ['https://', '/', '.']
    link = str(link)

    for char in chars:
        link = link.replace(char, '')

    link_filename = str(link)
    return(link_filename)


def search():
    """
    Make a folder named for search term
    Save json of each publication found
    Search CrossRef and GoogleScholar
    """

    search_crossref()
    #search_gscholar()


def search_crossref():
    """
    save search results from crossref as json
    search term saved with json
    each result saved as its url

    CrossRef
    https://www.crossref.org/blog/python-and-ruby-libraries-for-accessing-the-crossref-api/

    CrossRef Works
    https://github.com/fabiobatalha/crossrefapi/blob/master/README.rst#agency
    """

    for term in retrieve_list('search_terms'):

        df = pd.DataFrame()
        cr = Crossref()
        x = cr.works(query = term, limit = 50)
        dois = [z['DOI'] for z in x['message']['items']]

        links = [z['URL'] for z in x['message']['items']]
        print('links = ')
        print(links)

        for doi in dois:
            works = Works()
            w1 = works.doi(doi)

            link = w1['link'][0]['URL']
            print('link = ')
            print(link)
            link_filename = link_to_filename(link)

            data_json = json.dumps(w1, indent = 4, ensure_ascii = False)
            doi_str = str(doi.replace('/', '_'))
            json_path = os.path.join(retrieve_path('pub_crossref_json'), doi_str + '.json')
            json_file = open(json_path, 'w')
            json_file.write(data_json)
            json_file.close()


def search_gscholar():
    """
    Retrieve json year by year
    """
    for term in retrieve_list('search_terms'):

        json_to_dataframe()
        currentDateTime = datetime.datetime.now()
        date = currentDateTime.date()

        search_year_min = int(retrieve_format('search_year_min'))-1
        for year in range(int(date.strftime("%Y")), search_year_min, -1):

            print('year = ' + str(year))

            #work_completed('begin_acquire_gscholar_json_' + str(year), 0)
            for num in np.arange(0, 100, 1, dtype=int):

                num_str = str(num).zfill(3)
                url = 'https://scholar.google.com/scholar?'
                url = url + 'start=' + str(int(num*10))
                url = url + '&q=' + term
                #url = url + '&hl=en&as_sdt=0,5'
                url = url + '&hl=en&as_sdt=0,5'
                url = url + '&as_ylo=' + str(year)
                url = url + '&as_yhi=' + str(year)

                # check if recently scraped
                if check_scraped('gscholar', term, year, num_str):
                    #print('found: ' + 'gscholar' + ' ' + term +  ' ' + str(year) + ' ' + num_str)
                    continue

                soup = retrieve_html(url)
                if error_check(soup) == True: return('error')

                data = html_to_json(soup)
                if data == []: break
                #if len(data) < 10 and year != int(date.strftime("%Y")):
                    #work_completed('begin_acquire_gscholar_json_' + str(year), 1)

                data_json = json.dumps(data, indent = 2, ensure_ascii = False)
                print(data_json)

                name_src, name_dst, name_summary, name_unique, plot_unique = name_paths('gscholar')
                json_file = os.path.join(retrieve_path(name_src), 'json', term + ' ' + str(year) + ' ' + str(num_str) + ' ' + str(retrieve_datetime())  + '.json' )
                json_file = open(json_file, 'w')
                json_file.write(data_json)
                json_file.close()

                json_to_dataframe()


if __name__ == "__main__":
    main()
