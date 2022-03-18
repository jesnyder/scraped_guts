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

def acquire_pubs():
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
    work_completed('acquire_pubs', 0)

    # add author affiliations by looking up doi through CrossRef
    task = 'search_crossref'
    work_completed(task, 0)
    if work_to_do(task): search_crossref()
    work_completed(task, 1)

    # consolidate into a single dataframe
    # save to crossref_results.csv
    aggregate_df('crossref_results')
    aggregate_dst()


    # list pubs from search result of gscholar using search term
    task = 'search_gscholar'
    work_completed(task, 0)
    if work_to_do(task): search_gscholar()
    work_completed(task, 1)
    json_to_dataframe()

    # consolidate into a single dataframe
    # save as gscholar_results.csv
    aggregate_df('gscholar_results')
    aggregate_dst()

    # add pub details by looking up url and parsing html
    task = 'meta_html'
    work_completed(task, 0)
    if work_to_do(task): meta_html()
    work_completed(task, 1)

    # consolidate into a single dataframe
    # save as html_meta.csv
    aggregate_df('meta_html')
    aggregate_dst()

    # add author affiliations by looking up doi through CrossRef
    task = 'meta_crossref'
    work_completed(task, 1)
    if work_to_do(task): meta_crossref()
    work_completed(task, 1)

    meta_crossref()
    wait(10)

    # consolidate into a single dataframe
    # save to crossref_meta.csv
    aggregate_df('meta_crossref')
    aggregate_dst()


    work_completed('acquire_pubs', 1)

"""
working programs
"""

def aggregate_df(save_to_file):
    """

    """

    name_dataset = 'gscholar'
    name_src, name_dst, name_summary, name_unique, plot_unique = name_paths(name_dataset)

    df_all = pd.DataFrame()

    if save_to_file == 'crossref_results':
        src_path = os.path.join(retrieve_path('pub_crossref'))
    elif save_to_file == 'gscholar_results':
        src_path = os.path.join(retrieve_path('pub_gscholar'))
    elif save_to_file == 'meta_html':
        src_path = os.path.join(retrieve_path('pub_web'))
    elif save_to_file == 'meta_crossref':
        src_path = os.path.join(retrieve_path('pub_crossref'))


    for file in os.listdir(src_path):

        if '.csv' not in file: continue
        df = pd.read_csv(os.path.join(src_path, file))
        df = clean_dataframe(df)

        df_all = df_all.append(df)
        df_all = clean_dataframe(df_all)
        save_to = os.path.join(retrieve_path(name_dst), save_to_file + '.csv')
        df_all.to_csv(save_to)

        save_to = os.path.join(retrieve_path('pub_agg'), save_to_file + '.csv')
        df_all.to_csv(save_to)


def aggregate_dst():
    """

    """

    name_dataset = 'gscholar'
    name_src, name_dst, name_summary, name_unique, plot_unique = name_paths(name_dataset)

    df_all = pd.DataFrame()

    for file in os.listdir(retrieve_path(name_dst)):

        if '.csv' not in file: continue
        if 'pubs_meta' in file: continue
        df = pd.read_csv(os.path.join(retrieve_path(name_dst), file))
        df = clean_dataframe(df)

        for i in range(len(list(df[:,0]))):

            for name in df.columns:
                if name not in list(df_all.columns):
                    print('name = ' + name)
                    df_all[name] = list(df[name])

        df_all = df_all.append(df)
        df_all = clean_dataframe(df_all)
        save_to = os.path.join(retrieve_path('pub_agg'), 'pubs_meta' + '.csv')
        df_all.to_csv(save_to)


def check_scraped(name_dataset, term, year, num):
    """

    """
    name_src, name_dst, name_summary, name_unique, plot_unique = name_paths(name_dataset)

    paths_to_check = []
    paths_to_check.append(os.path.join(retrieve_path(name_src)))
    paths_to_check.append(os.path.join(retrieve_path('pub_gscholar')))
    paths_to_check.append(os.path.join(retrieve_path('pub_gscholar'), 'json'))
    paths_to_check.append(os.path.join(retrieve_path('pub_web')))
    paths_to_check.append(os.path.join(retrieve_path('pub_crossref')))

    for path in paths_to_check:

        for file in os.listdir(path):

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


def crossref_df(w1):
    """

    """
    keys = list(w1.keys())
    values = list(w1.values())

    df = pd.DataFrame()
    for i in range(len(keys)):

        key_name = str(keys[i])
        df[key_name] = [values[i]]

        keys_of_interest = ['author', 'link', 'reference', 'funder']
        #keys_of_interest = ['author']
        if keys[i] in keys_of_interest:

            w2 = values[i]
            item_num = 0

            for item in w2:

                item_num = item_num + 1
                keys2 = list(item.keys())
                values2 = list(item.values())

                for j in range(len(keys2)):
                    key_name2 = str(key_name + '_' + str(item_num) + '_' + keys2[j])
                    df[key_name2] = [values2[j]]

                    keys_of_interest_2 = ['affiliation']
                    if keys2[j] in keys_of_interest_2:

                        w3 = values2[j]
                        item_num_2 = 0

                        for item_2 in w3:

                            item_num_2 = item_num_2 + 1
                            keys3 = list(item_2.keys())
                            values3 = list(item_2.values())

                            for k in range(len(keys3)):
                                key_name3 = str(key_name2 + '_' + str(item_num_2) + '_' + keys3[k])
                                df[key_name3] = [values3[k]]
    return(df)


def error_check(soup):
    """
    check if automated search is detected
    """

    #df = pd.read_csv(os.path.join(retrieve_list('gscholar_error')))
    for error in retrieve_list('gscholar_error'):

        if str(error) in str(soup):
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

            df_path2 = os.path.join(retrieve_path('pub_gscholar'))
            df_dst2 = os.path.join(df_path2, term + '.csv')
            df_term.to_csv(df_dst2)


def query_crossref():
    """
    CrossRef
    https://www.crossref.org/blog/python-and-ruby-libraries-for-accessing-the-crossref-api/

    CrossRef Works
    https://github.com/fabiobatalha/crossrefapi/blob/master/README.rst#agency
    """

    for term in retrieve_list('search_terms'):

        df = pd.DataFrame()
        cr = Crossref()
        x = cr.works(query = term, limit = 500)
        dois = [z['DOI'] for z in x['message']['items']]

        for doi in dois:
            works = Works()
            w1 = works.doi(doi)
            df_doi = crossref_df(w1)
            df = df.append(df_doi)

        #df = clean_dataframe(df)
        print(retrieve_path('crossref_df'))
        df.to_csv(os.path.join(retrieve_path('crossref_df'), term + '.csv'))


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


def meta_crossref():
    """

    """

    # read in list of files
    src_path = os.path.join(retrieve_path('pub_web'), 'html_meta' + '.csv')
    df = pd.read_csv(src_path)
    df = clean_dataframe(df)

    df_all = pd.DataFrame()

    col_name_interest = 'title_link'
    titles = list(df[col_name_interest])

    for title in titles:

        df_temp =  df[(df[col_name_interest] == title)]

        for col_name in df.columns:

            works = Works()
            doi = list(df_temp[col_name])[0]
            print('doi = ')
            print(doi)

            try:
                w1 = works.doi(doi)
                df_doi = crossref_df(w1)

                df_all = df_all.append(df_doi)
                df_path = os.path.join(retrieve_path('pub_crossref'))
                df_dst = os.path.join(df_path, 'crossref_meta' + '.csv')
                df_all = clean_dataframe(df_all)
                df_all.to_csv(df_dst)
                break

            except:
                continue


def meta_html():
    """

    """
    headers = {
        'User-agent':
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }

    proxies = {
        'http': os.getenv('HTTP_PROXY') # or just type proxy here without os.getenv()
        }


    name_dataset = 'gscholar'
    name_src, name_dst, name_summary, name_unique, plot_unique = name_paths(name_dataset)
    df_path = os.path.join(retrieve_path(name_src), 'df')
    df_file = os.path.join(df_path, name_dataset + '.csv')
    df = pd.read_csv(df_file)
    df = clean_dataframe(df)
    df_original = df

    aggregate_df('html_meta')
    for url in list(df_original['title_link']):

        try:
            char_remove = ['/', '.', ':', 'httpswww']
            url_name = url
            for char in char_remove:
                url_name = url_name.replace(char, '')
            url_name = url_name[:40]
        except:
            url_name = 'none_found'


        print('url_name = ' + str(url_name))
        if check_scraped(name_dataset, url_name, 0, 0): continue
        print('NOT FOUND url_name = ' + str(url_name))

        #df = pd.DataFrame()
        df = df_original[(df_original['title_link'] == url)]
        print('df = ')
        print(df)

        df['time_retrieved'] = [retrieve_datetime()]
        df['url'] = [url]
        print(url)

        #time_string = retrieve_datetime()
        #wait_time = random.random()*5 + 2
        #print('Wait: ' + str(round(wait_time,2)) + ' from '  + str(time_string))
        #time.sleep(wait_time)

        try:
            #html = requests.get(url, headers=headers, proxies=proxies).text
            html = requests.get(url).text
            soup = BeautifulSoup(html, 'html.parser')
        except:
            soup = ''

        try:
            content = soup.head.title.text
            df['head_title'] = [content]
        except:
            df['head_title'] = [None]


        for tag in retrieve_list('html_meta_tags'):

            try:
                content = soup.find('meta', {'name':tag}).get('content')
                print(tag + ' = ')
                print(content)
                df[str(tag)] = [content]
            except:
                df[str(tag)] = [None]

            try:
                #content = soup.find_all('meta', {'name':tag})
                res = []
                for i in soup.find_all('meta', {'name':tag}):
                    res.append(i['content'])
                #print(tag + ' = ')
                #print(content)
                df[str(tag) + '-all'] = [res]
            except:
                df[str(tag)] = [None]


        df = df
        print('df = ')
        print(df.T)

        df_path = os.path.join(retrieve_path(str(name_dataset + '_article_df')))
        df_dst = os.path.join(df_path, url_name + '.csv')
        df.to_csv(df_dst)

        df_path = os.path.join(retrieve_path('pub_web'))
        df_dst = os.path.join(df_path, url_name + '.csv')
        df.to_csv(df_dst)

        aggregate_df('html_meta')
        #print('df_dst = ' + str(df_dst))


def search_crossref():
    """
    CrossRef
    https://www.crossref.org/blog/python-and-ruby-libraries-for-accessing-the-crossref-api/

    CrossRef Works
    https://github.com/fabiobatalha/crossrefapi/blob/master/README.rst#agency
    """

    for term in retrieve_list('search_terms'):

        df = pd.DataFrame()
        cr = Crossref()
        x = cr.works(query = term, limit = 500)
        dois = [z['DOI'] for z in x['message']['items']]

        for doi in dois:
            works = Works()
            w1 = works.doi(doi)

            data_json = json.dumps(w1, indent = 2, ensure_ascii = False)
            json_path = os.path.join(retrieve_path('pub_crossref_json'), doi + '.json')
            json_file = open(json_path, 'w')
            json_file.write(data_json)
            json_file.close()

            df_doi = crossref_df(w1)
            df = df.append(df_doi)

        #df = clean_dataframe(df)
        df_path = os.path.join(retrieve_path('pub_crossref'))
        df_dst = os.path.join(df_path, term + '.csv')
        df.to_csv(df_dst)


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
