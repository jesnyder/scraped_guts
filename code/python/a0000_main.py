import numpy as np

from a0001_admin import retrieve_list
from a0100_aggregate_info import aggregate_info
#from a0300_map_maker import map_maker

def main():
    """

    """

    # for each dataset
    for dataset in retrieve_list('name_dataset'):
        print('dataset = ' + str(dataset))

        # aggregate articles
        aggregate_info(dataset)

        # targeted count of categories
        #targeted_count(dataset)

        # untargeted count of categories
        #untargeted_count()

        # map articles
        # map_maker(dataset)

        # plot timelines






if __name__ == "__main__":
    main()
