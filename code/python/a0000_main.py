import numpy as np

from a0001_admin import retrieve_list

def main():
    """

    """


    # for each dataset
    for dataset in retrieve_list('name_dataset'):
        print('dataset = ' + str(dataset))


if __name__ == "__main__":
    main()
