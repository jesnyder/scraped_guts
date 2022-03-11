import numpy as np

from a0001_admin import write_paths
from a0001_admin import work_completed
from a0001_admin import work_to_do
from a0100_acquire_info import acquire_info
from a0200_aggregate_info import aggregate_info
from a0300_geolocate_articles import geolocate_articles
from a0400_untargeted_word_count import untargeted_word_count
from a0500_targeted_word_count import targeted_word_count
from a0600_map_maker import map_maker
from a1100_build_webpage import build_webpage

def main():
    """

    """

    write_paths()
    work_completed('begin_main', 0)
    if work_to_do('acquire_info') == True: acquire_info()
    if work_to_do('aggregate_info') == True: aggregate_info()
    if work_to_do('geolocate_articles') == True: geolocate_articles()
    if work_to_do('untargeted_word_count') == True: untargeted_word_count()
    if work_to_do('targeted_word_count') == True: targeted_word_count()
    if work_to_do('map_maker') == True: map_maker()
    if work_to_do('build_webpage') == True: build_webpage()
    work_completed('begin_main', 0, 1)


if __name__ == "__main__":
    main()
