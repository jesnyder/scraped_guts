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

    # scrape metadata for each article as html

    # scrape metaata for each article as json

    # add article metadata to df


def json_scraped():
    """

    """

    headers = {
        'User-agent':
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }

    f = os.path.join(retrieve_path('search_terms'))
    print('f = ' + str(f))
    df_search_terms = pd.read_csv(f)

    for term in list(df_search_terms['term']):

        print('term = ' + term)

        params = {
          "q": term,
          "hl": "en",
          }

        html = requests.get('https://scholar.google.com/scholar', headers=headers, params=params).text
        soup = BeautifulSoup(html, 'lxml')

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

          try:
            all_article_versions = result.select_one('a~ a+ .gs_nph')['href']

          except:
            all_article_versions = None

        data.append({
            'title': title,
            'title_link': title_link,
            'publication_info': publication_info,
            'snippet': snippet,
            'cited_by': f'https://scholar.google.com{cited_by}',
            'related_articles': f'https://scholar.google.com{related_articles}',
            'all_article_versions': f'https://scholar.google.com{all_article_versions}',
        })

        data_json = json.dumps(data, indent = 2, ensure_ascii = False)
        print(data_json)



if __name__ == "__main__":
    main()
