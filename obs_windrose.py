#!/usr/bin/env python
#
# (C) Copyright 2014 UIO.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0. 
# 
# 
# Creation: July 2017 - Anne Fouilloux - University of Oslo
#
# Usage:
#
#./test_read.py --inputdir=$PWD

import os
from optparse import OptionParser
import os.path
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import windrose as wr
import matplotlib.ticker as plticker

def mkdir_p(file):
    if file != "" and file != ".":
        path = os.path.dirname(file)
        try:
            os.stat(path)
        except:
            os.makedirs(path)

def main():
    usage = """usage: %prog  --inputdir=input_directory [--outputdir=output_directory]  """

    parser = OptionParser(usage=usage)
    parser.add_option("-s", "--inputdir", dest="inputdir",
                      help="root directory for reading input files", metavar="inputdir" )

    parser.add_option("--outputdir", dest="outputdir",
                      help="root directory for storing output files", metavar="outputdir")

    (options, args) = parser.parse_args()

    if not options.inputdir:
        parser.error("Input directory where files to read are located must be specified!")
    else:
        inputdir=options.inputdir


    if not options.outputdir:
# if WORKDIR is defined, we will use it otherwise files 
# will be stored in the current directory
        outputdir=os.environ.get("WORKDIR",".")
    else:
        outputdir=options.outputdir

#--- READ WRF DATA
    filenames = glob.glob(inputdir+"/"+'wind2.txt')
    np_array_list = []
    for filename in filenames:
        print(filename)
        df = pd.read_csv(filename,sep=",",names=['date','Speed','Direction','Level']) 
        df['date'] = pd.to_datetime(df['date'],
                                   format="%Y-%m-%dT%H:%M:%S")

        df = df.dropna(subset=['date'])
        #df = df.dropna(subset=['Speed'])
        #df = df.dropna(subset=['Direction'])
        np_array_list.append(df.as_matrix())

# collect all info for temperature sensors
    comb_np_array = np.vstack(np_array_list)
    big_frame = pd.DataFrame(comb_np_array)

    big_frame.columns = ['date','Speed','Direction','Level']
    big_frame['date']= pd.to_datetime(big_frame['date'])
    big_frame['Level']= big_frame['Level'].astype('float64')
    big_frame['Speed']= big_frame['Speed'].astype('float64')
    big_frame['Direction']= big_frame['Direction'].astype('float64')
    big_frame.index = big_frame['date']
    del big_frame['date']

# Remove too big wind speed values!
    big_frame=big_frame.loc[(big_frame['Speed'] <15)]

#### !!!!! REMEMBER TO REMOVE!!! JUST FOR TESTING#############################
#    big_frame = big_frame.loc[(big_frame.index >= '2018-01-10 00:00:00') & (big_frame.index <= '2018-01-10 02:00:00')]
############################################################################# 
    #print(big_frame)

    ws_10 = big_frame.loc[big_frame['Level'] == 1]
    ws_10 = ws_10['Speed'].resample('10Min').mean()
    ws_10 = ws_10[ws_10.index.minute == 0]
 
    ws_30 = big_frame.loc[big_frame['Level'] == 2]
    ws_30 = ws_30['Speed'].resample('10Min').mean()
    ws_30 = ws_30[ws_30.index.minute == 0]



# Mean Wind    
    dir_mean_a=[]
    dir_mean_b=[]
    time_a=[]
    time_b=[]

    for level, bf in big_frame.groupby('Level'):
        if level == 1:
            # Finding mean wind direction unit vetor
            for dt, group in bf.groupby(pd.Grouper(freq='10Min')):
                if dt.minute == 0:
                    time_a.append(dt)
                    WD = group['Direction']
                    Ux = -np.mean(np.sin((np.pi*WD)/180))
                    Uy = -np.mean(np.cos((np.pi*WD)/180))
                    Theta = np.arctan2(Ux,Uy) *(180/(np.pi))
                    if Theta<180:
                        Theta = Theta + 180
                    elif Theta>180:
                        Theta = Theta - 180
                    dir_mean_a.append(Theta)
        if level == 2:
            # Finding mean wind direction unit vetor
            for dt, group in bf.groupby(pd.Grouper(freq='10Min')):
                if dt.minute == 0:
                    time_b.append(dt)
                    WD = group['Direction']
                    Ux = -np.mean(np.sin((np.pi*WD)/180))
                    Uy = -np.mean(np.cos((np.pi*WD)/180))
                    Theta = np.arctan2(Ux,Uy) *(180/(np.pi))
                    if Theta<180:
                        Theta = Theta + 180
                    elif Theta>180:
                        Theta = Theta - 180
                    dir_mean_b.append(Theta)

    plt.hist([0, 1])
    plt.close()

#A quick way to create new windrose axes...
    def new_axes():
    	fig = plt.figure(figsize=(12, 10), dpi=80, facecolor='w', edgecolor='w')
    	rect = [0.1, 0.1, 0.8, 0.8]
    	ax = wr.WindroseAxes(fig, rect, axisbg='w')
    	fig.add_axes(ax)
    	return ax


    outfilename='obs_rose_Munch_10.png'
    ax = new_axes()
    ax.bar(dir_mean_a, ws_10.values, opening=0.8, edgecolor='white', bins=np.arange(0.5, 15, 2))
    plt.title('Wind Direction and Intensity at 10m - OBS Munch', y=1.08, fontsize=16, fontweight='bold')
    ax.set_xlim(0,450)
    ax.set_ylim(0,450)
    ax.yaxis.set_ticks(np.arange(0,450,50))
    ax.yaxis.set_ticklabels(np.arange(0,450,50))
    ax.set_legend()
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.3), title='Value [m/s]', fontsize=10)
    plt.savefig(outfilename)

    outfilename2='obs_rose_Munch_30.png'
    ax2 = new_axes()
    ax2.bar(dir_mean_b, ws_30.values, opening=0.8, edgecolor='white', bins=np.arange(0.5, 15, 2))
    plt.title('Wind Direction and Intensity at 30m - OBS Munch', y=1.08, fontsize=16, fontweight='bold')
    ax2.set_ylim(0,450)
    ax2.set_xlim(0,450)
    ax2.yaxis.set_ticks(np.arange(0,450,50))
    ax2.yaxis.set_ticklabels(np.arange(0,450,50))
    ax2.set_legend()
    ax2.legend(loc='center left', bbox_to_anchor=(1, 0.3), title='Value [m/s]', fontsize=10)
    plt.savefig(outfilename2)

    #plt.show()





if __name__ == "__main__":
    main()
