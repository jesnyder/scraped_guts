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

    # search for pubs
    task_name = 'search_term'
    if work_to_do(task_name):
        work_completed(task_name, 0)
        search_term()
        work_completed(task_name, 1)

    # make json folder
    make_json_folder()

    # retrieve metadata

    task_name = 'search_web'
    if work_to_do(task_name):
        work_completed(task_name, 0)
        #shutil.rmtree(os.path.join(retrieve_path('pub_web_json')))
        search_web()
        work_completed(task_name, 1)
    web_to_json()

    # retrieve metadata
    crosssearch_crossref()



    wait_time = random.random()*60 + 60
    print('Wait: ' + str(round(wait_time,2)) + ' from '  + str(time_string))
    time.sleep(wait_time)

    # completed acquire_pubs
    work_completed('acquire_pubs', 1)


def build_doi_url(doi):
    """

    """
    doi_url = 'https://doi.org/'
    doi_url = doi_url + str(doi)
    return(doi_url)


def check_scraped(name_dataset, term, year, num):
    """

    """
    name_src, name_dst, name_summary, name_unique, plot_unique = name_paths(name_dataset)

    paths_to_check = []
    paths_to_check.append(os.path.join(retrieve_path(name_src)))
    paths_to_check.append(os.path.join(retrieve_path('pub_gscholar_json')))
    paths_to_check.append(os.path.join(retrieve_path('pub_crossref_json')))
    paths_to_check.append(os.path.join(retrieve_path('pub_web_json')))

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


def crosssearch_crossref():
    """

    """
    json_src = os.path.join(retrieve_path('pub_json'))

    for file in os.listdir(json_src):

        json_file = open(os.path.join(json_src, file), 'r')
        data = json_file.read()
        json_file.close()
        obj_dst = json.loads(data)

        try:
            try:
                doi = obj_dst['web']['citation_doi']
            except:
                doi = obj_dst['web']['citation_doi']
            print('doi = ')
            print(doi)

        except:

            title = obj_dst['gscholar']['title']
            print('title = ')
            print(title)

            works = Works()

            w1 = works.query(bibliographic=title)
            dois = []
            for item in w1:

                doi = item['doi']
                print('doi = ')
                print(doi)

                dois.append(doi)


        works = Works()
        w1 = works.doi(doi)
        print('w1 = ')
        print(w1)

        searched_list = list(obj_dst['searched'])

        searched_list.append('crossref')
        json_obj = {"searched": [searched_list],}

        json_obj['doi'] = doi
        json_obj['doi_url'] = build_doi_url(doi)

        json_obj['crossref_doi'] = w1

        for search in list(obj_dst['searched']):
            json_obj[search] = obj_dst[search]

        json_file = open(os.path.join(json_src, file), 'w')
        #data_json = json.dumps(w1, indent = 4, ensure_ascii = False)
        #obj_json = json.dumps(obj_json, indent = 3, ensure_ascii = False)
        json_obj = json.dumps(json_obj, indent = 3)
        json_file.write(json_obj)
        json_file.close()


def html_gscholar_to_json(soup):
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


def link_to_filename(link):
    """
    return filename from link
    """

    link = str(link)

    chars = ['https://', 'www', '/', '.']
    for char in chars:
        link = link.replace(char, '')

    link_filename = str(link[:50])
    return(link_filename)


def make_json_folder():
    """

    """
    shutil.rmtree(os.path.join(retrieve_path('pub_json')))

    # list directories with json
    json_src = []
    json_src.append(os.path.join(retrieve_path('pub_crossref_json')))
    json_src.append(os.path.join(retrieve_path('pub_gscholar_json')))

    links = []
    for path in json_src:

        for file in os.listdir(path):

            if '.json' not in str(file): continue

            file_src = os.path.join(path, file)

            # read file and parse
            json_file = open(file_src, 'r')
            data = json_file.read()
            json_file.close()

            obj = json.loads(data)
            #obj = json.dumps(obj, indent = 4, ensure_ascii = False)

            for pub in obj:

                #print('pub = ')
                #print(pub)

                if 'gscholar' in str(path):
                    link = pub['title_link']
                    if link == '':
                        link = pub['title']

                    test_json = {"searched": ["gscholar"],}
                    test_json["gscholar"] = pub

                elif 'crossref' in str(path):
                    pub = obj

                    link = pub["link"][0]["URL"]

                    test_json = {"searched": ["crossref"],}
                    test_json["crossref"] = pub

                links.append(link)
                file_dst = os.path.join(retrieve_path('pub_json'), str(link_to_filename(link)) + '.json')
                json_file = open(file_dst, 'w')
                #obj_json = json.dumps(obj_json, indent = 3, ensure_ascii = False)
                test_json = json.dumps(test_json, indent = 3)
                json_file.write(test_json)
                json_file.close()

            df = pd.DataFrame()
            df['links'] = links
            df = clean_dataframe(df)
            df.to_csv(os.path.join(retrieve_path('pub_links')))
            print('pubs founds: ' + str(len(links)))


def meta_html(url):
    """

    """
    headers = {
        'User-agent':
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }

    proxies = {
        'http': os.getenv('HTTP_PROXY') # or just type proxy here without os.getenv()
        }

    print('url = ')
    print(url)

    try:
        #html = requests.get(url, headers=headers, proxies=proxies).text
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
    except:
        return(0)


    json_obj = {"searched": ["web"],}
    json_obj['url'] = url

    try:
        content = soup.head.title.text
        json_obj['title_head'] = content
    except:
        json_obj['title_head'] = None


    for tag in retrieve_list('html_meta_tags'):

        try:
            content = soup.find('meta', {'name':tag}).get('content')
            print(tag + ' = ')
            print(content)
            json_obj[str(tag)] = content
        except:
            json_obj[str(tag)] = None

        try:
            #content = soup.find_all('meta', {'name':tag})
            res = []
            for i in soup.find_all('meta', {'name':tag}):
                res.append(i['content'])
            #print(tag + ' = ')
            #print(content)
            json_obj[str(tag) + '-all'] = res
        except:
            json_obj[str(tag)] = None

    return(json_obj)


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


def search_web():
    """

    """

    for link in retrieve_list('pub_links'):


        link_name = link_to_filename(link)

        file_names = []
        for file in os.listdir(retrieve_path('pub_web_json')):
            file_split = file.split('.')
            file_name = file_split[0]
            file_names.append(file_name)

        if link_name in file_names: continue

        ref_list = list(retrieve_list('pub_links'))
        ref_index = ref_list.index(link)
        print('% complete = ' + str(100*round((ref_index+1)/(len(ref_list)),2)))

        json_obj = meta_html(link)
        json_file = os.path.join(retrieve_path('pub_web_json'),  link_name + '.json' )
        json_file = open(json_file, 'w')
        json_obj = json.dumps(json_obj, indent = 3)
        json_file.write(json_obj)
        json_file.close()


def search_term():
    """
    Make a folder named for search term
    Save json of each publication found
    Search CrossRef and GoogleScholar
    """
    search_crossref()
    search_gscholar()


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
            json_path = os.path.join(retrieve_path('pub_crossref_json'), link_filename + '.json')
            json_file = open(json_path, 'w')
            json_file.write(data_json)
            json_file.close()


def search_gscholar():
    """
    Retrieve json year by year
    """
    for term in retrieve_list('search_terms'):

        #json_to_dataframe()
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
                if check_scraped('pubs', term, year, num_str):
                    #print('found: ' + 'gscholar' + ' ' + term +  ' ' + str(year) + ' ' + num_str)
                    continue

                soup = retrieve_html(url)
                if error_check(soup) == True: return('error')

                data = html_gscholar_to_json(soup)
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

                #json_to_dataframe()


def web_to_json():
    """

    """
    json_src = os.path.join(retrieve_path('pub_json'))
    json_web = os.path.join(retrieve_path('pub_web_json'))


    for file in os.listdir(json_src):

        for web_file in os.listdir(json_web):

            if file != web_file: continue

            print('file = ')
            print(file)

            print('os.path.join(json_src, file) = ')
            print(os.path.join(json_src, file))

            json_file = open(os.path.join(json_src, file), 'r')
            data = json_file.read()
            json_file.close()
            obj_dst = json.loads(data)

            json_file = open(os.path.join(json_web, file), 'r')
            data = json_file.read()
            json_file.close()
            obj_src = json.loads(data)

            searched_list = list(obj_dst['searched'])
            searched_list.append('web')
            obj_dst['searched'] = searched_list
            obj_dst['web'] = obj_src

            json_file = open(os.path.join(json_src, file), 'w')
            #obj_json = json.dumps(obj_json, indent = 3, ensure_ascii = False)
            obj_dst = json.dumps(obj_dst, indent = 3)
            json_file.write(obj_dst)
            json_file.close()


if __name__ == "__main__":
    main()
