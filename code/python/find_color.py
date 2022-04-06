import os
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random

from a0001_admin import retrieve_color
from a0001_admin import retrieve_path
from a0001_admin import retrieve_format

def find_color(num):
    """

    """

    # print('finding color')

    #colorTransparency = retrieve_ref('scatterTransparency')
    try:
        colorTransparency = float(retrieve_format('colorTransparency'))
    except:
        colorTransparency = (retrieve_format('colorTransparency'))[0]
        colorTransparency = float(colorTransparency)


    """
    colorOrange = [240/255, 83/255, 35/255]
    colorPurple = [23/255, 27/255, 96/255]
    colorBlueDark = [0/255, 153/255, 216/255]
    colorBlueLight = [0/255, 188/255, 231/255]
    colorGray = [233/255, 225/255, 223/255]

    colorGreen = [233/255, 25/255, 223/255]
    colorPink = [240/255, 10/255, 10/255]
    colorYellow = [240/255, 100/255, 10/255]
    colorBlue = [10/255, 10/255, 223/255]

    colorMarker = colorOrange
    colorEdge = colorPurple
    """

    variant = random.randint(-50,50)
    variant = variant/50
    variant_change_strong = 0.02
    variant_change_weak = 0.02


    color_values =  retrieve_color(num)
    colorMarker = color_values
    colorEdge = color_values

    for j in range(len(color_values)):
        if color_values[j] == max(color_values):
            colorMarker[j] = color_values[j] + variant*variant_change_weak
        else:
            colorMarker[j] = color_values[j] + variant*variant_change_strong

        colorEdge[j] = 1.2*colorMarker[j]


    for ii in range(len(colorMarker)):
        colorMarker[ii] = round(colorMarker[ii],4)
        if colorMarker[ii] > 1: colorMarker[ii] = 1
        elif colorMarker[ii] < 0: colorMarker[ii] = 0

    for ii in range(len(colorEdge)):
        colorEdge[ii] = round(colorEdge[ii],4)
        if colorEdge[ii] > 1: colorEdge[ii] = 1
        elif colorEdge[ii] < 0: colorEdge[ii] = 0

    colorEdge = [1,1,1]


    return(colorMarker, colorEdge, colorTransparency)
