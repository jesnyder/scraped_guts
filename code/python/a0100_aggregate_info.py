from bs4 import BeautifulSoup
from datetime import datetime
import json
import lxml
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from serpapi import GoogleSearch
import re
import requests
import time

def aggregate_info(dataset):
    """
    Save a .csv
    """

    # retrieve information
    if 'nsf_' in dataset:
        df = retrieve_nsf()

    elif 'nih_' in dataset:
        df = retrieve_nih()

    elif 'clinical_' in dataset:
        df = retrieve_clinical()

    elif 'patent' in dataset:
        df = retrieve_nih()

    elif 'pub' in dataset:
        df = retrieve_nih()


def retrieve_nih():
    """

    """

    df = pd.DataFrame()
    return(df)

def retrieve_nih():
    """

    """

    df = pd.DataFrame()
    return(df)


def retrieve_nsf():
    """

    """

    df = pd.DataFrame()
    return(df)


def retrieve_clinical():
    """

    """

    df = pd.DataFrame()
    return(df)



if __name__ == "__main__":
    main()