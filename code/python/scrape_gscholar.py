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


"""
Reference: https://python.plainenglish.io/scrape-google-scholar-with-python-fc6898419305
"""

def scrape_gscholar():
    """
    Maximum information
    Minimal scrapes
    Check for redundency
    """

    # scrape json from gscholar
    json_scraped()

    # scrape html from gscholar and save

    # parse json from scraped html

    # convert json to df
    json_to_dataframe()

    # scrape metadata for each article as html

    # scrape metaata for each article as json

    # add article metadata to df



def error_check(soup):
    """
    check if automated search is detected
    """
    df = pd.read_csv(os.path.join(retrieve_path('gscholar_error')))
    for error in list(df['errors']):

        if str(error) in str(soup):
            return(True)

    return(False)


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

    f = os.path.join(retrieve_path('search_terms'))
    print('f = ' + str(f))
    df_search_terms = pd.read_csv(f)
    for term in list(df_search_terms['term']):

        print('term = ' + term)

        currentDateTime = datetime.datetime.now()
        date = currentDateTime.date()

        for year in range(int(date.strftime("%Y")), 2012, -1):


            num_list = np.arange(0, 10, 1, dtype=int)
            for num in num_list:

                print('num = ' + str(num))
                if num == 0:
                    url = 'https://scholar.google.com/scholar?'
                    url = url + 'as_ylo=' + str(year)
                    url = url + '&q=' + term
                    #url = url + 'start=' + str(int(num*10))
                    url = url + '&hl=en&as_sdt=0,5'

                else:
                    url = 'https://scholar.google.com/scholar?'
                    url = url + 'start=' + str(int(num*10))
                    url = url + '&q=' + term
                    url = url + '&hl=en&as_sdt=0,5'
                    url = url + '&as_ylo=' + str(year)

                print('url = ')
                print(url)

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

                data_json = json.dumps(data, indent = 2, ensure_ascii = False)
                print(data_json)

                json_file = os.path.join(retrieve_path('gscholar_json'), term + ' ' + str(year) + ' ' + str(num) + ' ' + str(retrieve_datetime())  + '.json' )
                json_file = open(json_file, 'w')
                json_file.write(data_json)
                json_file.close()

                json_to_dataframe()
                if data == []: break


def json_to_dataframe():
    """

    """
    df = pd.DataFrame()

    # retrieve archival json
    src_path = retrieve_path('gscholar_json')

    for file in os.listdir(src_path):

        src_file = os.path.join(src_path, file)

        if not file.endswith('.json'): continue

        f = os.path.join(retrieve_path('search_terms'))
        print('f = ' + str(f))
        df_search_terms = pd.read_csv(f)

        for term in list(df_search_terms['term']):

            if term not in str(file): continue

            #print('src_file = ' + str(src_file))
            df_file = pd.read_json(src_file)
            df = pd.DataFrame.append(df, df_file)
            try:
                df = df.sort_values('citations', ascending=False)
            except:
                df = df

            df = df.drop_duplicates(subset = 'title_link')

    # sort
    df = df.sort_values('citations', ascending=False)
    df = df.drop_duplicates(subset = 'title_link')
    df = df.reset_index()
    del df['index']
    df = clean_dataframe(df)
    #print(df)

    name_dataset = 'gscholar'
    dst_path_name = name_dataset + '_query_df'
    dst_path = retrieve_path(dst_path_name)
    df_file = os.path.join(dst_path, term + '.csv')

    df.to_csv(df_file)
    print('df = ')
    print(df)


if __name__ == "__main__":
    main()
