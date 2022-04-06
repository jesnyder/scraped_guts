import numpy as np

from a0001_admin import retrieve_list
from a0100_aggregate_info import aggregate_info

def main():
    """

    """


    # for each dataset
    for dataset in retrieve_list('name_dataset'):
        print('dataset = ' + str(dataset))

        # aggregate articles
        aggregate_info(dataset)
        #
        # map articles
        # plot timelines






if __name__ == "__main__":
    main()
