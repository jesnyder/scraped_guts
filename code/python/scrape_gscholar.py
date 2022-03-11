from bs4 import BeautifulSoup
import datetime
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

def scrape_gscholar():
    """
    Maximum information
    Minimal scrapes
    Check for redundency
    """

    # scrape json of specific publications by their title
    work_completed('acquire_gscholar_missing_json_scraped', 0)
    missing_json_scraped()
    work_completed('acquire_gscholar_missing_json_scraped', 1)

    # scrape json from gscholar
    work_completed('gscholar_json_scraped', 0)
    json_scraped()
    work_completed('gscholar_json_scraped', 1)

    # scrape html from gscholar and save

    # parse json from scraped html

    # convert json to df
    work_completed('gscholar_json_to_dataframe', 0)
    json_to_dataframe()
    work_completed('gscholar_json_to_dataframe', 1)

    work_completed('gscholar_aggregate_articles', 0)
    aggregate_articles()
    work_completed('gscholar_aggregate_articles', 1)

    # scrape metadata for each article as html

    # scrape metaata for each article as json

    # add article metadata to df


def scrape_gscholar_article():
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

    for url in list(df_original['title_link']):

        try:
            char_remove = ['/', '.', ':', 'httpswww']
            url_name = url
            for char in char_remove:
                url_name = url_name.replace(char, '')
            url_name = url_name[:40]
        except:
            url_name = 'none_found'

        #if check_scraped(name_dataset, url_name, 0, 0) ==  True: continue

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


        df = df.T
        print('df = ')
        print(df)

        df_path = os.path.join(retrieve_path(str(name_dataset + '_article_df')))
        df_dst = os.path.join(df_path, url_name + '.csv')
        df.to_csv(df_dst)
        #print('df_dst = ' + str(df_dst))

        aggregate_articles()


def aggregate_articles():
    """

    """
    name_dataset = 'gscholar'
    name_src, name_dst, name_summary, name_unique, plot_unique = name_paths(name_dataset)

    df_all = pd.DataFrame()
    df_path = os.path.join(retrieve_path(str(name_dataset + '_article_df')))

    for article_file in os.listdir(df_path):

        df_ref = os.path.join(df_path, article_file)
        df_article = pd.read_csv(df_ref)
        df_article = df_article.T
        df_article = clean_dataframe(df_article)

        df_all = df_all.append(df_article)
        df_all = clean_dataframe(df_all)
        df_all = df_all.drop_duplicates()

        #df_path_save = os.path.join(retrieve_path(name_dst)
        df_dst_name = os.path.join(retrieve_path(name_dst), name_dataset + '_meta' + '.csv')

        df_all.to_csv(df_dst_name)
        #print('df_dst_name = ' + str(df_dst_name))


# main programs


def json_scraped():
    """

    """

    headers = {
        'User-agent':
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }

    proxies = {
        'http': os.getenv('HTTP_PROXY') # or just type proxy here without os.getenv()
        }


    for term in retrieve_list('search_terms'):

        print('term = ' + term)

        currentDateTime = datetime.datetime.now()
        date = currentDateTime.date()

        #for year in range(2013, int(date.strftime("%Y")), 1):
        for year in range(int(date.strftime("%Y")), 2013, -1):

            if year != int(date.strftime("%Y")):
                work_completed('begin_acquire_gscholar_json_scraped_' + str(year), 0)


            num_list = np.arange(0, 20, 1, dtype=int)
            for num in num_list:

                print('num = ' + str(num))

                url = 'https://scholar.google.com/scholar?'
                url = url + 'start=' + str(int(num*10))
                url = url + '&q=' + term
                #url = url + '&hl=en&as_sdt=0,5'
                url = url + '&hl=en&as_sdt=0,5'
                url = url + '&as_ylo=' + str(year)
                url = url + '&as_yhi=' + str(year)

                print('url = ')
                print(url)

                # check if recently scraped
                if check_scraped('gscholar', term, year, num) == True:
                    print('json found.')
                    continue

                if year == 2022 and num > 3: continue

                time_string = retrieve_datetime()
                wait_time = random.random()*60 + 60
                print('Wait: ' + str(round(wait_time,2)) + ' from '  + str(time_string))
                time.sleep(wait_time)

                html = requests.get(url, headers=headers, proxies=proxies).text

                soup = BeautifulSoup(html, 'lxml')
                #print(soup)

                # check for errors
                if error_check(soup) == True:
                    return('error')

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


                #json_to_dataframe()
                if data == []: break

                if len(data) < 10 and year != int(date.strftime("%Y")):
                    work_completed('begin_acquire_gscholar_json_scraped_' + str(year), 1)

                data_json = json.dumps(data, indent = 2, ensure_ascii = False)
                print(data_json)

                name_src, name_dst, name_summary, name_unique, plot_unique = name_paths('gscholar')
                json_file = os.path.join(retrieve_path(name_src), 'json', term + ' ' + str(year) + ' ' + str(num) + ' ' + str(retrieve_datetime())  + '.json' )
                json_file = open(json_file, 'w')
                json_file.write(data_json)
                json_file.close()
                json_to_dataframe()


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


# support programs

def check_scraped(name_dataset, term, year, num):
    """

    """
    name_src, name_dst, name_summary, name_unique, plot_unique = name_paths(name_dataset)
    src_path = retrieve_path(name_src)

    paths_to_check = [src_path]

    if name_dataset == 'gscholar':
        src_path_json = os.path.join(src_path, 'json')
        paths_to_check.append(src_path_json)
        df_path = os.path.join(retrieve_path(str(name_dataset + '_article_df')))
        paths_to_check.append(df_path)

    for scr_path in paths_to_check:

        for file in os.listdir(src_path):

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
            if file_year != year: continue
            print('file_year = ' + file_year + ' year = ' + str(year))

            # find and compare file year to year passed into the function
            pattern = '[0-9]{2}'
            file_num = re.findall(pattern, file)
            file_num = file_num[0]
            if file_num != num: continue
            print('file_num = ' + file_num + ' num = ' + str(num))

            # find and compare file saved date to current date
            pattern = '[0-9]{4}' + '-' + '[0-9]{2}' + '-' +  '[0-9]{2}'
            file_date_saved = re.findall(pattern, file)
            file_date_saved = file_date_saved[0]
            print('file_date_saved = ' + file_date_saved)

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


def error_check(soup):
    """
    check if automated search is detected
    """

    #df = pd.read_csv(os.path.join(retrieve_list('gscholar_error')))
    for error in retrieve_list('gscholar_error'):

        if str(error) in str(soup):
            return(True)

    return(False)


def missing_json_scraped():
    """

    """

    headers = {
        'User-agent':
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }

    proxies = {
        'http': os.getenv('HTTP_PROXY') # or just type proxy here without os.getenv()
        }

    try:
        df = pd.read_csv(os.path.join(retrieve_path('gscholar_missing')))
        titles = list(df['title'])

    except:
        titles = []

    for title in titles:

        print('title = ' + title)

        currentDateTime = datetime.datetime.now()
        date = currentDateTime.date()

        url = 'https://scholar.google.com/scholar?'
        url = url + '&q=' + title
        #url = url + 'start=' + str(int(num*10))
        url = url + '&hl=en&as_sdt=0,5'

        print('url = ')
        print(url)

        title_short = str(title[:35])
        if check_scraped('gscholar', title_short, 0, 0) == True:
            print('json found.')
            continue


        time_string = retrieve_datetime()
        wait_time = random.random()*60 + 30
        print('Wait: ' + str(round(wait_time,2)) + ' from '  + str(time_string))
        time.sleep(wait_time)

        html = requests.get(url, headers=headers, proxies=proxies).text

        # Delay scraping to circumvent CAPCHA
        time.sleep(wait_time)
        time_string = retrieve_datetime()
        print('Wait: ' + time_string)

        soup = BeautifulSoup(html, 'lxml')

        # check for errors
        if error_check(soup) == True: break

        # Scrape just PDF links
        for pdf_link in soup.select('.gs_or_ggsm a'):
            pdf_file_link = pdf_link['href']
            print(pdf_file_link)

        # JSON data will be collected here
        data = []

        # Container where all needed data is located
        for result in soup.select('.gs_ri'):
            title = result.select_one('.gs_rt').text
            title_link = result.select_one('.gs_rt a')['href']
            publication_info = result.select_one('.gs_a').text
            snippet = result.select_one('.gs_rs').text
            cited_by = result.select_one('#gs_res_ccl_mid .gs_nph+ a')['href']
            related_articles = result.select_one('a:nth-child(4)')['href']

            # get the year of publication of each paper
            txt_year = result.find("div", class_="gs_a").text
            ref_year = re.findall('[0-9]{4}', txt_year)
            ref_year = ref_year[0]

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

        #json_to_dataframe()
        if data == []: break

        data_json = json.dumps(data, indent = 2, ensure_ascii = False)
        print(data_json)

        name_src, name_dst, name_summary, name_unique, plot_unique = name_paths('gscholar')
        json_file = os.path.join(retrieve_path(name_src), 'json', title_short + '.json' )
        json_file = open(json_file, 'w')
        json_file.write(data_json)
        json_file.close()


if __name__ == "__main__":
    main()
