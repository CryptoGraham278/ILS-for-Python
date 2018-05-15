# Incline Layer Separator for Python
# Author : Chris Hertlein
# Incept Date : 6 October 2017
# Version : 0.1
# (based off the visual basic excel sheet masterpiece originally created by Joshua Fisher)



# required libraries
# What do I really NEED?!
import csv
import math
import pandas as pd
import numpy as np
# for testing FIFO
# ==============================================================================
# Set later to user input, but for now these are the range and modulation definitions
#
# Distal 90%
rangedef = 0.90
# Distal 95% to Proximal 95%
moddef = 0.95
# Zebra Serial number
ZebraSN = 0
# Zebra Offset
ZebraOffset = 0
# Zebra WET
ZebraWET = 0

class incline_dialect(csv.Dialect):
    lineterminator = '\n'
    delimiter = ':'

# ==============================================================================
# Import the golden curve for the treatment room
# ** Note ** For the purposes of just testing, this is set to open from the user's home directory
# I WILL make this be a parseable file input in the future.
golden_curve = pd.read_csv(StringIO(''.join(l.replace(':', ';') for l in open('~/Dropbox/Coding/ILS for Python/Sample Data/GoldenCurve.csv'))),sep=';',skiprows=4,header=None)
# This block of code for checking the Golden Curve's minimum sample rate and rejecting if sampling rate is less than 60 (180 channels / 3)
# This block of code for upsampling / interpolating the input Golden Curve up to 180 points (number of channels, required for data manipulation in the full sheet)
# ==============================================================================

# ==============================================================================
# Import the Calibration Shot taken for the day's data for the treatment room
# I can hard-code in the skiprows because the format of the MLIC Cal data should ALWAYS be the same.
# I WILL make this be a parseable file input in the future.
# First, import the csv as "calshottemp" and split the list into two parts: "CalShotHeader" and "CalShot".
calshottemp = []
with open('Calib[2017-8-05 22-54].csv') as f:
    calshottemp = [next(f) for x in xrange(15)]
# Strips out those pesky carriage return and new line bits at the end.
for i in range(len(calshottemp)):
    calshottemp[i] = calshottemp[i].rstrip('\r\n')

# Take the first 8 rows of "calshottemp" for CalShotHeader:
CalShotHeader = []
CalShot = []
#for i in range(10,16,2):
#    calshot[(i/2 - 4)] = calshot.append(pd.read_csv(os.path.expanduser('~/Dropbox/Coding/ILS for Python/Sample Data/Calib[2017-8-05 22-54].csv'),sep=';',skiprows=i,header=None)
for i in range(8):
    CalShotHeader[i] = calshottemp[i]
# Take rows 11 through 15 of "calshottemp" for CalShot:
for i in range (11,16):
    CalShot[(i-11)] = CalShotHeader[i]
# Remove the rows that don't actually have useful data:
CalShot.pop(1)
CalShot.pop(3)

# ==============================================================================
# Extract useful information from CalShotHeader !


# ==============================================================================
# Input Incline Measurement CSV file
# Steps:
# Read header (rows 1-22),
# Read Rows 13 and 14 for Sampling Time [ms] and Number of Samples,
# Read Rows 17 and 18 for Buildup Thickness [cm] and Buildup WET [g/cm^3]
# Read Row 21 using ':' delimiter FIRST to stuff all active channels into one element of list
# Then push that list element to a new list with delimiter ';'
InclineHeader = []
SamplingTime = 0
NumSamples = 0
BuildupThicc = 0
BuildupWET = 0
numpile = []
with open('IBTR2_90_Modulations_2.csv','r') as f:
        InclineHeader = [next(f) for x in xrange(22)]
for i in range(len(InclineHeader)):
    InclineHeader[i] = InclineHeader[i].rstrip('\r\n')
for i in range(len(InclineHeader)):
    # Find Sampling Time and fill it in
    if 'Sampling time:' in InclineHeader[i]:
        InclineHeader[i] = InclineHeader[i].rstrip('[ms]')
        numpile = InclineHeader[i].split(':')
        SamplingTime = int(numpile[1])
        numpile = []
    # Find Number of Samples and fill it in
    if 'Number of samples:' in InclineHeader[i]:
        numpile = InclineHeader[i].split(':')
        NumSamples = int(numpile[1])
        numpile = []
    # Find Buildup Thickness and fill it in
    if 'Build-up thickness:' in InclineHeader[i]:
        InclineHeader[i] = InclineHeader[i].rstrip('[cm]')
        numpile = InclineHeader[i].split(':')
        BuildupThicc = int(numpile[1])
        numpile = []
    # Find Buildup Density and fill it in
    if 'Build-up density:' in InclineHeader[i]:
        InclineHeader[i] = InclineHeader[i].rstrip('[g/cm^3]')
        numpile = InclineHeader[i].split(':')
        BuildupWET = int(numpile[1])
        numpile = []
# ==============================================================================

# Next, need to read the active channels and push that into an array.
