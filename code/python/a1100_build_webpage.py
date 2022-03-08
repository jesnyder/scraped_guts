import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import shutil

from a0001_admin import clean_dataframe
from a0001_admin import name_paths
from a0001_admin import retrieve_categories
from a0001_admin import retrieve_format
from a0001_admin import retrieve_list
from a0001_admin import retrieve_path
from a0001_admin import write_paths
from a0200_aggregate_info import add_ref_year
from find_color import find_color




def build_webpage():
    """
    Objective: Summarize the projects and findings

    Tasks:
        1. Write summary of html

    """

    print("running build_webpage")

    tasks = [0]

    if  0 in tasks: tasks = np.arange(1, 101, 1)
    if  1 in tasks: copy_media()
    if  2 in tasks: introduction_html()

    print("completed build_webpage")


def copy_media():
    """

    """

    # copy images and gif used to build the website to a folder within docs

    # copy comparison chart
    for name_article in retrieve_list('type_article'):

        for term in retrieve_categories():

            plot_count_annual = str(name_article + '_compare_terms_plot')
            src = os.path.join(retrieve_path(plot_count_annual), term +  '_percent' + '_02' + '.png')
            dst_name = str(src)
            dst_name = dst_name.replace('/','_')
            dst = os.path.join(retrieve_path('web_media'), dst_name)
            shutil.copy(src,dst)

            gif_dst = str(name_article + '_map_gif')
            for file in os.path.join(retrieve_path(gif_dst)):

                src = os.path.join(os.path.join(retrieve_path(gif_dst)), file)
                dst_name = str(src)
                dst_name = dst_name.replace('/','_')
                dst = os.path.join(retrieve_path('web_media'), dst_name)
                try:
                    shutil.copy(src,dst)
                except:
                    print(dst + ' not found')

            file_dst_name = str(name_article + '_map_png')
            try:
                df_file = os.path.join(retrieve_path(file_dst_name), term + '_' + str('2022') + '.png')
            except:
                df_file = os.path.join(retrieve_path(file_dst_name), term + '_' + str('2021') + '.png')

            src = df_file
            dst_name = str(src)
            dst_name = dst_name.replace('/','_')
            dst = os.path.join(retrieve_path('web_media'), dst_name)
            try:
                shutil.copy(src,dst)
            except:
                print(dst + ' not found')


    # copy map image

    # copy map gif


def introduction_html():
    """

    """

    h0_str = 'Survey of Metals Cited in NSF Awards on Heavy Metal Remediation'
    h0_txt = 'Motivation: Survey the number of awards and amount of funding historically dedicated by NSF to heavy metal remediation. '

    h1_str = 'Introduction'
    h1_txt = 'The National Science Foundation (NSF) maintains a public database of all current and past awards. We survey and analyze the awards relevant to "heavy metal public health" and "heavy metal remediation" to identify which metals have been investigated and which have been sidelined. '


    index_html = retrieve_path('html_index')
    f = open(index_html, "w")
    f.close()
    f = open(index_html, "w")
    f.close()

    f = open(index_html, "w")
    f.write('<!DOCTYPE html>' + '\n' )
    f.write('<html>' + '\n' )
    f.write('<title>MetalSurvey</title>' + '\n' )
    f.write('</head>' + '\n' )

    f.write('<style>' + '\n' )
    f.write('.container {' + '\n' )
    f.write('width: 100%;' + '\n' )
    f.write('height: 100%;' + '\n' )
    f.write('}' + '\n' )
    f.write('img {' + '\n' )
    f.write('width: 80%;' + '\n' )
    f.write('height: 80%;' + '\n' )
    f.write('object-fit: cover;' + '\n' )
    f.write('}' + '\n' )
    f.write('</style>' + '\n' )



    # plot of the number of patents per year
    f.write('<body>' + '\n')
    f.write('<center>' + '\n')
    f.write('<div class="container">')

    f.write('<h1>' + str(h0_str) + '</h1>' + '\n')
    f.write('<p>' + str(h0_txt) + '</p>' + '\n')
    f.write('</body>' + '\n')

    f.write('<h2>' + str('Objective & Tasks') + '</h2>' + '\n')
    f.write('<p>' + str('The objective is to query, scrape, and analyze the NSF awards for trends in funding.' ))

    f.write('</center>' + '\n')
    f.write(str('The tasks to complete are: ') + '\n')
    f.write('</p>' + '\n')

    f.write(str('<ol>'))

    f.write('\n' + str('<li>'))
    f.write('\n' + str(' Query: Pool awards by NSF relevant to "heavy metal public health" and "heavy metal remediation" '))
    f.write('\n' + str('</li>'))

    f.write('\n' + str('<li>'))
    f.write('\n' + str(' Aggregate: Coregister datasets into a consistent, machine readable file structure'))
    f.write('\n' + str('</li>'))

    f.write('\n' + str('<li>'))
    f.write('\n' + str(' Define: Define the size of the database. Plot the number of patents per year (cumulative).'))
    f.write('\n' + str('</li>'))

    f.write('\n' + str('<li>'))
    f.write('\n' + str(' Geolocation: Define the geographic footprint of the database. Map the assignee address of the patents per year.'))
    f.write('\n' + str('</li>'))

    f.write('\n' + str('<li>'))
    f.write('\n' + str(' Targeted Text Analysis: Plot the occurrances of metals in the award database and total the amount awarded to date.'))
    f.write('\n' + str('</li>'))

    f.write('\n' + str('*** not yet completed ***'))

    f.write('\n' + str('<li>'))
    f.write('\n' + str(' Untargeted Text Analysis: Count the frequency of all words used in the database.'))
    f.write('\n' + str('</li>'))

    f.write('\n' + str('<li>'))
    f.write('\n' + str(' Cross-reference Google Scholar for cited-by metric to identify most impactful work.'))
    f.write('\n' + str('</li>'))


    f.write('\n' + str(''))
    f.write(str('</ol>)'))

    f.write('</body>' + '\n')

    f.write('<center>' + '\n')

    f.write('<h2>' + str('The History of Heavy Metals in NSF Awards') + '</h2>' + '\n')

    for name_article in retrieve_list('type_article'):

        try:
            print('article = ' + str(name_article))
            ff = os.path.join(retrieve_path(name_article + '_aggregate_df'),  name_article + '_with_address' + '.csv' )
            print('f = ' + str(ff))
            df = clean_dataframe(pd.read_csv(ff))

        except:
            print('article = ' + str(name_article))
            ff = os.path.join(retrieve_path(name_article + '_aggregate_df'),  name_article + '.csv' )
            print('f = ' + str(ff))
            df = clean_dataframe(pd.read_csv(ff))

        print('df.columns = ')
        print(df.columns)

        year_min = min(list(df['ref_year']))
        year_max = max(list(df['ref_year']))
        year_span = year_max - year_min
        total_filed = len(list(df['ref_year']))

        f.write('<p>' + str('The plot represents ' + str(total_filed)))
        f.write(str(' NSF awards issued over a '))
        f.write(str(year_span) + ' year span, from ')
        f.write(str(str(year_min) + '-' + str(year_max) + '. Only a fraction of these awards mention a specific metal of interest to this inquiry. Mention of specific metals in the awards are compared each year.') + '</p>' + '\n')

        print('retrieve_categories() = ')
        print(retrieve_categories())
        for term in retrieve_categories():

            f.write('<img alt="My Image" src="' + '')

            plot_count_annual = str(name_article + '_compare_terms_plot')
            src = os.path.join(retrieve_path(plot_count_annual), term +  '_percent' + '_02' + '.png')
            dst_name = str(src)
            dst_name = dst_name.replace('/','_')
            dst = os.path.join(retrieve_path('web_media_for_index'), dst_name)
            f.write(dst)
            print(dst)
            f.write('" />')

            f.write('</div>')
            f.write('</center>' + '\n')
            f.write('</body>' + '\n')

            # map of patents
            f.write('<body>' + '\n')
            f.write('<center>' + '\n')
            f.write('<div class="container">')
            f.write('<h2>' + str('Map of Heavy Metal NSF Awards') + '</h2>' + '\n')

            # Insert map gif
            f.write('<img alt="My Image" src="' + '')
            gif_dst = str(name_article + '_map_gif')
            for file in os.path.join(retrieve_path(gif_dst)):

                src = os.path.join(os.path.join(retrieve_path(gif_dst)), file)
                dst_name = str(src)
                dst_name = dst_name.replace('/','_')
                dst = os.path.join(retrieve_path('web_media'), dst_name)

                f.write('<img alt="My Image" src="' + '')
                f.write(dst)
                f.write('" />')

            f.write('<img alt="My Image" src="' + '')
            file_dst_name = str(name_article + '_map_png')

            try:
                df_file = os.path.join(retrieve_path(file_dst_name), term + '_' + str('2021') + '.png')
            except:
                df_file = os.path.join(retrieve_path(file_dst_name), term + '_' + str('2020') + '.png')

            src = df_file
            dst_name = str(src)
            dst_name = dst_name.replace('/','_')
            dst = os.path.join(retrieve_path('web_media'), dst_name)
            f.write(dst)
            f.write('" />')

            f.write('</div>')
            f.write('</center>' + '\n')
            f.write('</body>' + '\n')

        f.close()


        for col_name in df.columns:

            name_src, name_dst, name_summary, name_unique, plot_unique = name_paths(name_article)
            file_path = os.path.join(retrieve_path(name_unique),  col_name + '.csv' )
            write_table_count(file_path)



    # Close the html file
    f = open(index_html, "a")
    f.write('</html>' + '\n' )
    f.close()


def write_table_count(file_path):
    """

    """

    print('file_path = ')
    print(file_path)

    file_split = file_path.split('/')
    file_name = file_split[-1]
    file_split = file_name.split('.')
    file_name = file_split[0]

    # retrieve trial counts
    df = pd.read_csv(file_path)
    df = clean_dataframe(df)

    df['counts'] = df['counts'].astype(int)

    term = list(df['value'])
    count = list(df['counts'])
    percent = list(df['percents'])

    chart_title = 'Trial counts for the metadata term:' + file_name

    index_html = retrieve_path('html_index')
    f = open(index_html, "a")
    f.write('<body>' + '\n')
    f.write('<center>' + '\n')
    f.write('<h3>' + str(chart_title) + '</h3>' + '\n')
    f.write('<table>' + '\n')

    f.write('<tr>' + '\n')
    f.write('<th>' + file_name + '        ' + '</th>' + '\n')
    f.write('<th>' + 'Number of Awards' + '</th>' + '\n')
    f.write('</tr>' + '\n')

    for i in range(len(term)):

        if count[i] < 50: continue

        f.write('<tr>' + '\n')
        f.write('<th>' + str(term[i]) + '</th>' + '\n')
        f.write('<th>' + str(count[i]) + '</th>' + '\n')
        f.write('</tr>' + '\n')

    f.write('</table>' + '\n')
    f.write('</center>' + '\n')
    f.write('</body>' + '\n')



if __name__ == "__main__":
    main()
