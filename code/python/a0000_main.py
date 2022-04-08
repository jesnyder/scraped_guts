import numpy as np

from a0001_admin import retrieve_list
from a0001_admin import write_paths
from a0100_aggregate_info import aggregate_info
from a0300_targeted_count import targeted_word_count
from a0400_untargeted_count import untargeted_word_count

def main():
    """

    """

    write_paths()

    # for each dataset
    for dataset in retrieve_list('name_dataset'):

        print('dataset = ' + str(dataset))

        # aggregate articles
        aggregate_info(dataset)

        # targeted count of categories
        #targeted_word_count(dataset)

        # untargeted count of categories
        untargeted_word_count(dataset)

        # map articles
        # map_maker(dataset)

        # plot timelines






if __name__ == "__main__":
    main()
