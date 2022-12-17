#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Example of making a plot using personal health statistics.
Uses matplotlib.pyplot

Pull blood pressure stats from an app like Apple Health or Nokia HealthMate.
Transform the raw data into a CSV format. See: scrub_raw_data.py
Store in a CSV format at DATAPATH.

Note that weight_lbs is missing from the data file.
If I un-comment the plot instruction for that datapoint, it produces an error,
but a plot is still generated with the data processed up to that point.

"""
from pprint import pprint as pp
import pandas as pd
from matplotlib import pyplot as plt

# DATACOLS = ['reading_date', 'heart_rate_bpm', 'weight_lbs', 'systolic_mmHG', 'diastolic_mmHG']
DATACOLS = ['reading_date', 'heart_rate_bpm', 'systolic_mmHG', 'diastolic_mmHG']
DATAPATH = '/home/dave/Dropbox/Projects/Data_Science/data_files/'
DATAPATH += 'export_from_healthmate.csv'
# Compute average values to use for filling in blanks:
HEALTH_DF1 = pd.read_csv(filepath_or_buffer=DATAPATH,
                         delimiter=",",
                         header=0,
                         usecols=DATACOLS)
AVGBP = round(int(np.mean(HEALTH_DF1.heart_rate_bpm)))
# AVGWGT = round(float(np.mean(HEALTH_DF1.weight_lbs)), 1)
AVGWGT = 180.0
AVGSYS = round(int(np.mean(HEALTH_DF1.systolic_mmHG)))
AVGDIA = round(int(np.mean(HEALTH_DF1.diastolic_mmHG)))

def convert_date(reading_date):
    """ Convert date to pandas Timestamp format """
    pandate = pd.Timestamp(reading_date)
    return pandate

def convert_heartrate(heart_rate_bpm):
    """ Convert heartrate to integer, replacing blanks with average """
    if heart_rate_bpm.isdigit():
        panval = int(heart_rate_bpm)
    else:
        panval = AVGBP
    return panval

def convert_weight(weight_lbs):
    """ Convert weight to float, replacing blanks with average """
    if weight_lbs == '':
        panval = AVGWGT
    else:
        panval = round(float(weight_lbs), 1)
    return panval

def convert_sys_bp(mmgh):
    """ Convert mmgh to integer, replacing blanks with average """
    if mmgh.isdigit():
        panval = int(mmgh)
    else:
        panval = AVGSYS
    return panval

def convert_dia_bp(mmgh):
    """ Convert mmgh to integer, replacing blanks with average """
    if mmgh.isdigit():
        panval = int(mmgh)
    else:
        panval = AVGDIA
    return panval

def plot_data():
    """ Create a trend chart across time """
    mytitle = "Health Stats"
    xoffs = [i for i, _ in enumerate(HEALTH_DF.reading_date)]
    plt.plot(xoffs, HEALTH_DF.heart_rate_bpm, 'y--', label="bpm")
    # plt.plot(xoffs, HEALTH_DF.weight_lbs, 'r-.', label="lbs")
    plt.plot(xoffs, HEALTH_DF.systolic_mmHG, 'b:', label="systolic mmHG")
    plt.plot(xoffs, HEALTH_DF.diastolic_mmHG, 'c:', label="diastolic mmHG")
    plt.legend(loc=('center'), bbox_to_anchor=(0.5, 0.75))
    plt.xlabel("Days")
    plt.title(mytitle)
    fig = plt.figure(1)
    fig.canvas.set_window_title(mytitle)
    plt.show(block=True)

# Convert data set to desired formats, with blanks filled in
HEALTH_DF = pd.read_csv(filepath_or_buffer=DATAPATH,
                        delimiter=",",
                        header=0,
                        usecols=DATACOLS,
                        converters={'reading_date': convert_date,
                                    'heart_rate_bpm': convert_heartrate,
                                    'weight_lbs': convert_weight,
                                    'systolic_mmHG': convert_sys_bp,
                                    'diastolic_mmHG': convert_dia_bp})
pp(HEALTH_DF)
plot_data()
