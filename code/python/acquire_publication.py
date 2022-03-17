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


"""
Reference: https://python.plainenglish.io/scrape-google-scholar-with-python-fc6898419305
"""

def acquire_publication():
    """
    List pubs from search result of gscholar using search term
    Consolidate into a single dataframe
    gscholar_results.csv

    Add pub details by looking up url and parsing html
    Consolidate into a single dataframe
    html_meta.csv

    Add author affiliations by looking up doi through CrossRef
    Consolidate into a single dataframe
    crossref_meta.csv

    """

    # list pubs from search result of gscholar using search term
    search_gscholar()

    # consolidate into a single dataframe
    # save as gscholar_results.csv
    aggregate_df()

    # add pub details by looking up url and parsing html
    search_articles()

    # consolidate into a single dataframe
    # save as html_meta.csv
    aggregate_df()


    # add author affiliations by looking up doi through CrossRef
    query_crossref()

    # consolidate into a single dataframe
    # save to crossref_meta.csv
    search_crossref()




"""
working programs
"""

def check_scraped(name_dataset, term, year, num):
    """

    """
    name_src, name_dst, name_summary, name_unique, plot_unique = name_paths(name_dataset)
    src_path = retrieve_path(name_src)

    paths_to_check = [src_path]

    if name_dataset == 'gscholar':
        src_path_json = os.path.join(src_path, 'json')
        src_path = src_path_json
        #paths_to_check.append(src_path_json)
        #df_path = os.path.join(retrieve_path(str(name_dataset + '_article_df')))
        #paths_to_check.append(df_path)

        try:
            df_path = os.path.join(retrieve_path(name_src), 'df')
            df_file = os.path.join(df_path, term + '.csv')
            df = pd.read_csv(df_file)
            df = df[(df['year'] == year)]
            num_int = int(num.lstrip())*10
            #print('num_int = ' + str(num_int))
            if len(list(df['year'])) < num_int:
                #print('found: ' + 'gscholar' + ' ' + term +  ' ' + str(year) + ' ' + str(num))
                return(True)
        except:
            hello = 'hello'


    for file in os.listdir(src_path):

        #print('file = ' + file)
        # check specific gscholar search
        file_split = file.split('.')
        if file_split[0] == term: return(True)

        # find and compare file term to term passed into the function
        pattern = '[a-z]+'
        flags = re.IGNORECASE
        file_term = re.findall(pattern, file, flags)
        file_term = file_term[0]
        if file_term != term: continue
        #print('file_term = ' + file_term + ' term = ' + term)

        # find and compare file year to year passed into the function
        pattern = '[0-9]{4}'
        file_year = re.findall(pattern, file)
        file_year = file_year[0]
        if str(file_year) != str(year): continue
        #print('file_year = ' + file_year + ' year = ' + str(year))

        # find and compare file year to year passed into the function
        pattern = '[0-9]{3}'
        file_num = re.findall(pattern, file)
        file_num = file_num[1]
        if str(file_num) != str(num): continue
        #print('file_num = ' + file_num + ' num = ' + str(num))

        # find and compare file saved date to current date
        file = file.split(' ')
        file = file[3]
        pattern = '[0-9]{4}' + '-' + '[0-9]{2}' + '-' +  '[0-9]{2}'
        file_date_saved = re.findall(pattern, file)
        file_date_saved = file_date_saved[0]
        #print('file_date_saved = ' + file_date_saved)

        a = file_date_saved.split('-')
        a = datetime.datetime(int(a[0]), int(a[1]), int(a[2]), 0, 0)
        #print('a = ' + str(a))
        b = datetime.datetime.today()
        #print('b = ' + str(b))
        v = b-a
        #print('v = ' + str(v))
        v = int(v.days)
        #print('v = ' + str(v))
        if v < 3:
            #print('date match: ' + str(v))
            #print('too many days lapsed since last query.')
            return(True)

    return(False)


def html_to_json(soup):
    """

    """

    # Scrape just PDF links
    for pdf_link in soup.select('.gs_or_ggsm a'):
        pdf_file_link = pdf_link['href']
        print(pdf_file_link)

    # JSON data will be collected here
    data = []

    # Container where all needed data is located
    for result in soup.select('.gs_ri'):
        title = result.select_one('.gs_rt').text

        try:
            title_link = result.select_one('.gs_rt a')['href']
        except:
            title_link = ''

        publication_info = result.select_one('.gs_a').text
        snippet = result.select_one('.gs_rs').text
        cited_by = result.select_one('#gs_res_ccl_mid .gs_nph+ a')['href']
        related_articles = result.select_one('a:nth-child(4)')['href']

        # get the year of publication of each paper
        try:
            txt_year = result.find("div", class_="gs_a").text
            ref_year = re.findall('[0-9]{4}', txt_year)
            ref_year = ref_year[0]
        except:
            ref_year = 0

        # get number of citations for each paper
        try:
            txt_cite = result.find("div", class_="gs_fl").find_all("a")[2].string
            citations = txt_cite.split(' ')
            citations = (citations[-1])
            citations = int(citations)
        except:
            citations = 0

        try:
            all_article_versions = result.select_one('a~ a+ .gs_nph')['href']
        except:
            all_article_versions = None

        data.append({
            'year': ref_year,
            'title': title,
            'title_link': title_link,
            'publication_info': publication_info,
            'snippet': snippet,
            'citations': citations,
            'cited_by': f'https://scholar.google.com{cited_by}',
            'related_articles': f'https://scholar.google.com{related_articles}',
            'all_article_versions': f'https://scholar.google.com{all_article_versions}',
        })

    return(data)


def json_to_dataframe():
    """

    """
    name_dataset = 'gscholar'

    # retrieve archival json
    name_src, name_dst, name_summary, name_unique, plot_unique = name_paths(name_dataset)
    src_path = retrieve_path(name_src)
    src_path = os.path.join(src_path, 'json')

    df_all = pd.DataFrame()

    for term in retrieve_list('search_terms'):

        df_term = pd.DataFrame()

        for file in os.listdir(src_path):

            if not file.endswith('.json'): continue

            json_src = os.path.join(src_path, file)
            df = pd.read_json(json_src)

            df_path = os.path.join(retrieve_path(name_src), 'df')
            if not os.path.exists(df_path):
                os.makedirs(df_path)

            df_file = os.path.join(df_path, name_dataset + '.csv')
            df_all = df_all.append(df)
            df_all = df_all.drop_duplicates(subset = 'title_link')
            df_all = clean_dataframe(df_all)
            df_all.to_csv(df_file)

            if term not in str(file): continue

            df_path = os.path.join(retrieve_path(name_src), 'df')
            df_file = os.path.join(df_path, term + '.csv')
            df_term = df_term.append(df)
            df_term = df_term.drop_duplicates(subset = 'title_link')
            df_term = clean_dataframe(df_term)
            df_term.to_csv(df_file)


def retrieve_html(url):
    """

    """

    print('url = ')
    print(url)

    headers = {
        'User-agent':
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }

    proxies = {
        'http': os.getenv('HTTP_PROXY') # or just type proxy here without os.getenv()
        }

    time_string = retrieve_datetime()
    wait_time = random.random()*60 + 60
    print('Wait: ' + str(round(wait_time,2)) + ' from '  + str(time_string))
    time.sleep(wait_time)

    html = requests.get(url, headers=headers, proxies=proxies).text
    soup = BeautifulSoup(html, 'lxml')

    return(soup)


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
                    print('found: ' + 'gscholar' + ' ' + term +  ' ' + str(year) + ' ' + num_str)
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
