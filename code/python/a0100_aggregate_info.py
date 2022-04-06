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
    if 'nih_' in dataset:
        df = retrieve_nih()

    elif 'nsf_' in dataset:

    elif 'clinical_' in dataset:

    elif 'patent' in dataset:

    elif 'pub' in dataset:


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
